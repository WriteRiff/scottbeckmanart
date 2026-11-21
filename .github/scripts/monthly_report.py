"""Monthly website report, sent to the owner's phone by Pushover on the 1st of each month.
Runs on GitHub's computers (no PC needed, nobody has to start it).

Contents: visits and page views (last month vs the month before), top pages, how people found the site
(the sites that linked to it, from Cloudflare Web Analytics), phone vs computer, downtime last month,
broken links, security certificate and domain renewal dates.
Google's own monthly Search Console email covers what people searched for on Google.

Never asks visitors anything. Prints nothing private: the logs of a public repository are public.
Secrets (entered by the owner in GitHub, never printed): PUSHOVER_USER, PUSHOVER_TOKEN, CF_API_TOKEN.
"""
import base64, json, os, socket, ssl, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from html import escape
from html.parser import HTMLParser
from xml.etree import ElementTree

SITE = os.environ["SITE_URL"].rstrip("/") + "/"
HOST = urllib.parse.urlparse(SITE).hostname
NAME = os.environ.get("SITE_NAME", HOST)
CF_ACCOUNT, CF_SITE = os.environ.get("CF_ACCOUNT", ""), os.environ.get("CF_SITE_TAG", "")
CF_TOKEN = os.environ.get("CF_API_TOKEN", "")
USER, TOKEN = os.environ.get("PUSHOVER_USER", ""), os.environ.get("PUSHOVER_TOKEN", "")
GH, REPO = os.environ.get("GH_TOKEN", ""), os.environ.get("REPO", "")
UA = {"User-Agent": "monthly-site-report (GitHub Actions)"}
LINK_TIMEOUT = 15
BOT_BLOCKING_HOSTS = ("instagram.com", "facebook.com", "youtube.com")
MESSAGE_LIMIT = 1024


def open_url(url, headers=None, data=None, timeout=25):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    return urllib.request.urlopen(req, timeout=timeout)


def get(url, headers=None, data=None, timeout=25):
    with open_url(url, headers, data, timeout) as r:
        return r.status, r.read()


def html_value(value):
    return escape(str(value).replace("\r", " ").replace("\n", " "))


def short_value(value):
    return html_value(value if len(value) <= 40 else value[:39] + "…")


def month_bounds(today):
    first_this = today.replace(day=1)
    last_end = first_this
    last_start = (first_this - timedelta(days=1)).replace(day=1)
    prev_start = (last_start - timedelta(days=1)).replace(day=1)
    return prev_start, last_start, last_end


def cf(start, end):
    q = """query($a:String!,$s:String!,$from:Time!,$to:Time!){viewer{accounts(filter:{accountTag:$a}){
      total:rumPageloadEventsAdaptiveGroups(limit:1,filter:{siteTag:$s,datetime_geq:$from,datetime_lt:$to}){count sum{visits}}
      pages:rumPageloadEventsAdaptiveGroups(limit:5,orderBy:[count_DESC],filter:{siteTag:$s,datetime_geq:$from,datetime_lt:$to}){count dimensions{requestPath}}
      refs:rumPageloadEventsAdaptiveGroups(limit:6,orderBy:[sum_visits_DESC],filter:{siteTag:$s,datetime_geq:$from,datetime_lt:$to}){sum{visits} dimensions{refererHost}}
      devices:rumPageloadEventsAdaptiveGroups(limit:4,orderBy:[sum_visits_DESC],filter:{siteTag:$s,datetime_geq:$from,datetime_lt:$to}){sum{visits} dimensions{deviceType}}
    }}}"""
    var = {"a": CF_ACCOUNT, "s": CF_SITE, "from": f"{start}T00:00:00Z", "to": f"{end}T00:00:00Z"}
    _, body = get("https://api.cloudflare.com/client/v4/graphql",
                  {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"},
                  json.dumps({"query": q, "variables": var}).encode())
    j = json.loads(body)
    if j.get("errors"):
        raise RuntimeError("Cloudflare query failed")
    return j["data"]["viewer"]["accounts"][0]


def visitors_section(prev_start, last_start, last_end):
    if not (CF_TOKEN and CF_ACCOUNT and CF_SITE):
        return ["<b>Visitors</b>: not set up yet (needs the Cloudflare token in GitHub)."]
    try:
        now_, before = cf(last_start, last_end), cf(prev_start, last_start)
    except Exception as e:
        return [f"<b>Visitors</b>: couldn't read Cloudflare ({html_value(type(e).__name__)})."]
    t = now_["total"][0] if now_["total"] else {"count": 0, "sum": {"visits": 0}}
    b = before["total"][0] if before["total"] else {"count": 0, "sum": {"visits": 0}}
    out = [f"<b>Visitors</b>: {html_value(t['sum']['visits'])} visits, {html_value(t['count'])} page views "
           f"(month before: {html_value(b['sum']['visits'])} visits)"]
    pages = ", ".join(f"{short_value(p['dimensions']['requestPath'])} {html_value(p['count'])}" for p in now_["pages"])
    if pages:
        out.append(f"<b>Top pages</b>: {pages}")
    refs = []
    for r in now_["refs"]:
        h = r["dimensions"]["refererHost"] or "typed in / bookmark"
        if h == HOST or h.endswith("." + HOST):
            continue
        refs.append(f"{html_value(h)} {html_value(r['sum']['visits'])}")
    if refs:
        out.append(f"<b>How people found it</b>: {', '.join(refs[:5])}")
    dev = ", ".join(f"{html_value(d['dimensions']['deviceType'])} {html_value(d['sum']['visits'])}" for d in now_["devices"])
    if dev:
        out.append(f"<b>Devices</b>: {dev}")
    return out


def downtime_section(last_start, last_end):
    try:
        _, body = get(f"https://api.github.com/repos/{REPO}/contents/state.json?ref=uptime-state",
                      {"Authorization": f"Bearer {GH}", "Accept": "application/vnd.github+json"})
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "<b>Downtime</b>: none recorded."
        return "<b>Downtime</b>: couldn't read downtime record."
    except Exception:
        return "<b>Downtime</b>: couldn't read downtime record."

    start = datetime.combine(last_start, datetime.min.time(), timezone.utc)
    end = datetime.combine(last_end, datetime.min.time(), timezone.utc)
    try:
        state = json.loads(base64.b64decode(json.loads(body)["content"]))
        down = state["down"]
        if not isinstance(down, bool):
            raise ValueError("Invalid downtime status")
        intervals = [(datetime.fromisoformat(i["start"]), datetime.fromisoformat(i["end"]))
                     for i in state.get("incidents", [])]
        if down:
            intervals.append((datetime.fromisoformat(state["since"]), datetime.now(timezone.utc)))
        overlap = [min(incident_end, end) - max(incident_start, start)
                   for incident_start, incident_end in intervals]
    except Exception:
        return "<b>Downtime</b>: couldn't read downtime record."
    seconds = [duration.total_seconds() for duration in overlap if duration > timedelta(0)]
    ongoing = " (Down right now!)" if down else ""
    if not seconds:
        return "<b>Downtime</b>: none." + ongoing
    return (f"<b>Downtime</b>: {html_value(len(seconds))} time(s), "
            f"{html_value(round(sum(seconds) / 60))} minutes in all.{ongoing}")


class PageLinks(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.links = []
        self.ids = set()
        self.feed(body.decode("utf-8", "replace"))
        self.close()

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.links.append(value)
            elif name == "id" and value:
                self.ids.add(value)


def fetch_page(url):
    with open_url(url, timeout=LINK_TIMEOUT) as response:
        return response.geturl(), PageLinks(response.read())


def link_label(url, fragment=""):
    parts = urllib.parse.urlsplit(url)
    host = short_value(parts.hostname) if parts.hostname != HOST else ""
    return host + short_value((parts.path or "/") + ("#" + fragment if fragment else ""))


def missing_fragments(url, fragments, ids):
    return [link_label(url, fragment) for fragment in sorted(fragments - ids)]


def check_target(url, fragments):
    try:
        with open_url(url, timeout=LINK_TIMEOUT) as response:
            if fragments:
                return missing_fragments(url, fragments, PageLinks(response.read()).ids)
    except urllib.error.HTTPError as e:
        with e:
            host = urllib.parse.urlsplit(e.geturl()).hostname or ""
            if e.code in (401, 403, 429) and any(host == site or host.endswith("." + site) for site in BOT_BLOCKING_HOSTS):
                return []
            return [f"{link_label(url)} ({html_value(e.code)})"]
    except Exception:
        return [link_label(url)]
    return []


def broken_links():
    try:
        _, sm = get(SITE + "sitemap.xml", timeout=LINK_TIMEOUT)
        pages = list(dict.fromkeys(loc.text.strip() for loc in ElementTree.fromstring(sm).findall(".//{*}loc")
                                   if loc.text and loc.text.strip()))
    except Exception:
        return "<b>Broken links</b>: couldn't read the sitemap."

    targets, cached, bad = {}, {}, []
    with ThreadPoolExecutor(max_workers=8) as pool:
        page_jobs = {url: pool.submit(fetch_page, url) for url in pages}
        for url, job in page_jobs.items():
            try:
                final_url, page = job.result()
            except Exception:
                bad.append(link_label(url))
                cached[url] = None
                continue
            cached[url] = cached[final_url] = page.ids
            for link in page.links:
                try:
                    target, fragment = urllib.parse.urldefrag(urllib.parse.urljoin(final_url, link))
                    parts = urllib.parse.urlsplit(target)
                    if parts.scheme not in ("http", "https"):
                        continue
                    if not parts.hostname:
                        raise ValueError("Missing link hostname")
                except ValueError:
                    bad.append(short_value(link))
                    continue
                targets.setdefault(target, set())
                if fragment:
                    targets[target].add(urllib.parse.unquote(fragment))

        link_jobs = []
        for url, fragments in targets.items():
            if url not in cached:
                link_jobs.append(pool.submit(check_target, url, fragments))
            elif cached[url] is not None:
                bad.extend(missing_fragments(url, fragments, cached[url]))
        for job in link_jobs:
            bad.extend(job.result())

    if not bad:
        return f"<b>Broken links</b>: none ({html_value(len(targets))} URLs checked)."
    return f"<b>Broken links</b>: {html_value(len(bad))}: " + ", ".join(bad[:5])


def cert_date():
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((HOST, 443), timeout=15) as s, ctx.wrap_socket(s, server_hostname=HOST) as t:
            end = datetime.strptime(t.getpeercert()["notAfter"], "%b %d %H:%M:%S %Y %Z").date()
        return f"<b>Security certificate</b>: OK until {html_value(f'{end:%b %d, %Y}')} (GitHub renews it automatically)."
    except Exception as e:
        return f"<b>Security certificate</b>: PROBLEM ({html_value(type(e).__name__)}). Check the site."


def domain_date():
    try:
        _, body = get(f"https://rdap.verisign.com/com/v1/domain/{HOST}")
        ev = {e["eventAction"]: e["eventDate"][:10] for e in json.loads(body).get("events", [])}
        end = date.fromisoformat(ev["expiration"])
        days = (end - date.today()).days
        warn = " Please check GoDaddy auto-renew and payment card." if days < 60 else ""
        return f"<b>Domain</b>: registry expiry {html_value(f'{end:%b %d, %Y}')} ({html_value(days)} days).{warn}"
    except Exception:
        return "<b>Domain</b>: couldn't look up the renewal date."


def keep_schedules_alive():
    success = True
    for wf in ("uptime.yml", "monthly-report.yml"):
        try:
            req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/actions/workflows/{wf}/enable", method="PUT",
                                         headers={"Authorization": f"Bearer {GH}", "Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=20) as response:
                if response.status != 204:
                    raise RuntimeError("Workflow enable did not succeed")
        except Exception:
            print(f"::error::Couldn't refresh schedule for {wf}.")
            success = False
    return success


def trim_message(lines):
    kept = []
    length = 0
    for line in lines:
        length += len(line) + bool(kept)
        if length > MESSAGE_LIMIT:
            break
        kept.append(line)
    return "\n".join(kept)


def main():
    schedules_refreshed = keep_schedules_alive()
    if not (USER and TOKEN):
        print("::error::Add the Pushover secrets in GitHub to send the monthly report.")
        return 1
    prev_start, last_start, last_end = month_bounds(date.today())
    lines = [downtime_section(last_start, last_end), broken_links(), cert_date(), domain_date()]
    lines += visitors_section(prev_start, last_start, last_end)
    lines.append("Google's own Search Console email shows what people searched for.")
    data = urllib.parse.urlencode({"token": TOKEN, "user": USER, "html": 1, "priority": 0,
                                   "title": f"{html_value(NAME)}: {html_value(f'{last_start:%B}')} report",
                                   "message": trim_message(lines),
                                   "url": "https://dash.cloudflare.com/?to=/:account/web-analytics", "url_title": "Full numbers in Cloudflare"}).encode()
    _, body = get("https://api.pushover.net/1/messages.json", data=data, timeout=20)
    if json.loads(body).get("status") != 1:
        raise RuntimeError("Pushover did not accept the report")
    print("Report sent.")
    return int(not schedules_refreshed)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print("::error::The monthly report workflow couldn't complete.")
        raise SystemExit(1)
