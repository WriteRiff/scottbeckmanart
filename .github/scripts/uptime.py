"""Downtime alarm for the website. Runs on GitHub's computers every few minutes (no PC needed).

- Checks each address in SITES (secure https, real page content).
- Only calls it "down" after 3 failed checks about 45 seconds apart (no false alarms from one blip).
- Down: Pushover emergency alarm that repeats for up to 3 hours. Acknowledging it buys 12 quiet hours.
- Back up: cancels the repeating alarm and sends one normal "back up" message.
- Remembers whether the site is down in a small file on the `uptime-state` branch (not the live site).
Secrets PUSHOVER_USER and PUSHOVER_TOKEN are entered by the owner in GitHub; this script never prints them.
Nothing private is printed: the workflow logs of a public repository are public.
"""
import base64, json, os, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

SITES = [s.strip() for s in os.environ.get("SITES", "").split(",") if s.strip()]
MUST_CONTAIN = os.environ.get("MUST_CONTAIN", "")
NAME = os.environ.get("SITE_NAME", "the website")
USER, TOKEN = os.environ.get("PUSHOVER_USER", ""), os.environ.get("PUSHOVER_TOKEN", "")
GH, REPO = os.environ.get("GH_TOKEN", ""), os.environ.get("REPO", "")
TEST = os.environ.get("TEST_ALARM", "").lower() in ("yes", "true", "1")
BRANCH, PATH = "uptime-state", "state.json"
APEX_HOST = "scottbeckmanart.com"
API = "https://api.pushover.net/1"
ALARM_TAG = "scottbeckmanart-uptime"
ALARM_EXPIRE = 3 * 3600
ACK_QUIET_SECONDS = 12 * 3600


def now():
    return datetime.now(timezone.utc)


def pushover_request(path, data=None):
    encoded = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(f"{API}/{path}", data=encoded)
    with urllib.request.urlopen(req, timeout=20) as response:
        result = json.load(response)
    if result.get("status") != 1:
        raise RuntimeError("Pushover request failed")
    return result


def pushover(title, message, priority=0, url=None, *, tag=None):
    data = {"token": TOKEN, "user": USER, "title": title, "message": message, "priority": priority}
    if priority == 2:
        data.update(retry=216, expire=ALARM_EXPIRE, sound="siren")  # 50 intervals over 3 hours
        if tag:
            data["tags"] = tag
    if url:
        data.update(url=url, url_title="Open the site")
    result = pushover_request("messages.json", data)
    return result["receipt"] if priority == 2 else None


def cancel(receipt, *, tag=None):
    if receipt:
        path = f"receipts/{receipt}/cancel.json"
    elif tag:
        path = f"receipts/cancel_by_tag/{tag}.json"
    else:
        return False
    for _ in range(3):
        try:
            pushover_request(path, {"token": TOKEN})
            return True
        except Exception:
            continue
    return False


def alarm_due(state, t):
    if not state["down"] or not state.get("alarmed_at"):
        return True
    sent = datetime.fromisoformat(state["alarmed_at"])
    age = (t - sent).total_seconds()
    if age < ALARM_EXPIRE:
        return False
    receipt = state.get("receipt")
    if not receipt or age >= 7 * 86400:  # Pushover keeps receipts queryable for one week.
        return True
    query = urllib.parse.urlencode({"token": TOKEN})
    status = pushover_request(f"receipts/{receipt}.json?{query}")
    if status["acknowledged"]:
        ack = status.get("acknowledged_at")
        acknowledged = datetime.fromtimestamp(ack, timezone.utc) if ack else sent
        return (t - acknowledged).total_seconds() >= ACK_QUIET_SECONDS
    return bool(status["expired"])


def check_once(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "site-uptime-check (GitHub Actions)", "Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=25) as r:
            final = urllib.parse.urlsplit(r.geturl())
            if final.scheme != "https" or final.hostname != APEX_HOST:
                return "final URL is not on the secure apex host"
            if r.status != 200:
                return f"status {r.status}"
            if MUST_CONTAIN and MUST_CONTAIN not in r.read(400000).decode("utf-8", "replace"):
                return "page content missing"
            return None
    except urllib.error.HTTPError as e:
        return f"status {e.code}"
    except Exception as e:
        return type(e).__name__ + (": certificate problem" if "CERTIFICATE" in str(e).upper() else "")


def site_problem(url):
    problem = None
    for attempt in range(3):
        problem = check_once(url)
        if problem is None:
            return None
        if attempt < 2:
            time.sleep(45)
    return problem


def gh(method, path, body=None):
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}{path}", method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {GH}", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404 and method == "GET":
            return None
        raise


def load_state():
    f = gh("GET", f"/contents/{PATH}?ref={BRANCH}")
    if not f:
        return {"down": False, "incidents": []}, None
    return json.loads(base64.b64decode(f["content"])), f["sha"]


def save_state(state, sha):
    if not sha and not gh("GET", f"/branches/{BRANCH}"):
        main = gh("GET", "/git/ref/heads/main")
        gh("POST", "/git/refs", {"ref": f"refs/heads/{BRANCH}", "sha": main["object"]["sha"]})
    body = {"message": "Uptime state: " + ("down" if state["down"] else "up"), "branch": BRANCH,
            "content": base64.b64encode(json.dumps(state, indent=1).encode()).decode()}
    if sha:
        body["sha"] = sha
    return gh("PUT", f"/contents/{PATH}", body)["content"]["sha"]


def send_alarm(state, sha, t, detail):
    if not state["down"]:
        state["since"] = t.isoformat()
    state.update(down=True, alarmed_at=t.isoformat(), receipt=None)
    failed = False
    try:
        sha = save_state(state, sha)
    except Exception:
        print("::error::Couldn't save the down state before sending the alarm.")
        failed = True

    state["receipt"] = pushover(f"{NAME} is DOWN", f"Not loading: {detail}. Checked 3 times about 45 seconds apart.",
                               2, SITES[0], tag=ALARM_TAG)
    try:
        # A failed request may have reached GitHub. Get the current SHA before retrying.
        if failed:
            _, sha = load_state()
        save_state(state, sha)
    except Exception:
        print("::error::Couldn't save the alarm receipt.")
        failed = True
        try:
            _, sha = load_state()
            save_state(state, sha)
        except Exception:
            print("::error::Couldn't save the alarm receipt on retry.")
    return int(failed)


def main():
    if not (USER and TOKEN):
        print("::warning::The downtime alarm is not armed. Add the Pushover secrets in GitHub.")
        return 0
    if TEST:
        r = pushover(f"TEST: {NAME} is down", "This is a test of the downtime alarm. Acknowledge it in Pushover to stop it repeating.", 2, SITES[0])
        print("Test alarm sent. Waiting 60 seconds before the test 'back up' message.")
        time.sleep(60)
        if not cancel(r):
            print("::error::Couldn't cancel the test siren. Acknowledge the alarm in Pushover to silence it.")
            return 1
        pushover(f"TEST: {NAME} is back up", "Test finished. Real alarms work the same way.", 0, SITES[0])
        return 0

    with ThreadPoolExecutor(max_workers=2) as pool:
        problems = {url: problem for url, problem in zip(SITES, pool.map(site_problem, SITES)) if problem}
    state, sha = load_state()
    t = now()
    if problems:
        detail = "; ".join(f"{u} ({p})" for u, p in problems.items())
        print("One or more site addresses failed the checks.")
        if alarm_due(state, t):
            return send_alarm(state, sha, t, detail)
    else:
        print("All site addresses passed the checks.")
        if state["down"]:
            since = datetime.fromisoformat(state["since"])
            minutes = round((t - since).total_seconds() / 60)
            message = f"The site is loading again. It was down for about {minutes} minutes."
            if not cancel(state.get("receipt"), tag=ALARM_TAG):
                print("::warning::Couldn't cancel the emergency siren after three attempts.")
                message += " Please acknowledge the alarm in Pushover to silence it."
            pushover(f"{NAME} is back up", message, 0, SITES[0])
            state["incidents"] = (state.get("incidents", []) + [{"start": state["since"], "end": t.isoformat(), "minutes": minutes}])[-50:]
            state.update(down=False, since=None, alarmed_at=None, receipt=None)
            save_state(state, sha)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print("::error::The downtime alarm workflow couldn't complete.")
        raise SystemExit(1)
