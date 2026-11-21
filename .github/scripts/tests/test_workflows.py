import base64
import io
import json
import os
import sys
import unittest
import urllib.error
import urllib.parse
from contextlib import redirect_stdout
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
with patch.dict(os.environ, {"SITE_URL": "https://scottbeckmanart.com/"}, clear=True):
    import monthly_report as report
    import uptime


class UptimeTests(unittest.TestCase):
    def setUp(self):
        self.t = datetime(2026, 11, 1, 2, tzinfo=timezone.utc)
        self.state = {"down": False, "incidents": []}
        self.sha = "old-sha"
        self.events = []
        self.log = self.enterContext(redirect_stdout(io.StringIO()))
        self.enterContext(patch.multiple(uptime, USER="stub-user", TOKEN="stub-token", TEST=False,
                                         SITES=[report.SITE, "https://www.scottbeckmanart.com/"]))
        self.enterContext(patch.object(uptime, "now", return_value=self.t))
        self.probe = self.enterContext(patch.object(uptime, "site_problem", return_value="offline"))
        self.enterContext(patch.object(uptime, "load_state", side_effect=lambda: (self.state.copy(), self.sha)))
        self.send = self.enterContext(patch.object(uptime, "pushover", side_effect=self.send_message))

    def send_message(self, title, message, priority, url, **kwargs):
        self.events.append(("message", priority))
        return "receipt-id" if priority == 2 else None

    def save(self, state, sha):
        self.assertEqual(sha, self.sha)
        self.state = state.copy()
        self.sha += "+"
        return self.sha

    def test_failed_receipt_write_does_not_resend_emergency(self):
        def save(state, sha):
            self.events.append(("save", state["down"], state["receipt"]))
            if state["receipt"]:
                raise OSError("simulated write failure")
            self.assertEqual(state["since"], self.t.isoformat())
            self.assertEqual(state["alarmed_at"], self.t.isoformat())
            return self.save(state, sha)

        with patch.object(uptime, "save_state", side_effect=save):
            self.assertEqual(uptime.main(), 1)
            self.assertEqual(uptime.main(), 0)
        self.assertEqual(self.events, [("save", True, None), ("message", 2),
                                       ("save", True, "receipt-id"), ("save", True, "receipt-id")])

    def test_failed_first_write_still_sends_once_and_marks_run_failed(self):
        def save(state, sha):
            self.events.append(("save", state["receipt"]))
            if not state["receipt"]:
                raise OSError("simulated first write failure")
            return self.save(state, sha)

        with patch.object(uptime, "save_state", side_effect=save):
            self.assertEqual(uptime.main(), 1)
            self.assertEqual(uptime.main(), 0)
        self.assertEqual(self.events, [("save", None), ("message", 2), ("save", "receipt-id")])

    def test_test_alarm_is_canceled_before_finished_message(self):
        def cancel(path, data):
            self.assertEqual(path, "receipts/receipt-id/cancel.json")
            self.events.append(("cancel", path))

        with patch.object(uptime, "TEST", True), patch.object(uptime.time, "sleep") as sleep, \
                patch.object(uptime, "pushover_request", side_effect=cancel):
            self.assertEqual(uptime.main(), 0)
        sleep.assert_called_once_with(60)
        self.assertEqual(self.events, [("message", 2), ("cancel", "receipts/receipt-id/cancel.json"), ("message", 0)])

    def test_recovery_retries_receipt_before_sending_notice(self):
        self.probe.return_value = None
        start = (self.t - timedelta(minutes=20)).isoformat()
        self.state.update(down=True, since=start, alarmed_at=start, receipt="receipt-id")

        def cancel(path, data):
            self.events.append(("cancel", path))
            if len(self.events) < 3:
                raise OSError("simulated cancel failure")

        with patch.object(uptime, "pushover_request", side_effect=cancel), patch.object(uptime, "save_state", self.save):
            self.assertEqual(uptime.main(), 0)
        self.assertEqual(self.events, [("cancel", "receipts/receipt-id/cancel.json")] * 3 + [("message", 0)])
        self.assertFalse(self.state["down"])
        self.assertEqual(self.state["incidents"], [{"start": start, "end": self.t.isoformat(), "minutes": 20}])

    def test_recovery_notice_explains_how_to_silence_uncanceled_siren(self):
        self.probe.return_value = None
        self.state.update(down=True, since=self.t.isoformat(), receipt="receipt-id")
        with patch.object(uptime, "pushover_request", side_effect=OSError("simulated cancel failure")) as cancel, \
                patch.object(uptime, "save_state", self.save):
            self.assertEqual(uptime.main(), 0)
        self.assertEqual(cancel.call_count, 3)
        self.assertIn("acknowledge the alarm in Pushover to silence it", self.send.call_args.args[1])
        self.assertIn("Couldn't cancel", self.log.getvalue())

    def test_acknowledgment_suppresses_realarm_for_twelve_hours(self):
        sent = self.t - timedelta(hours=13)
        acknowledged = self.t - timedelta(hours=11)
        self.state.update(down=True, since=sent.isoformat(), alarmed_at=sent.isoformat(), receipt="receipt-id")
        status = {"acknowledged": 1, "acknowledged_at": int(acknowledged.timestamp()), "expired": 1}
        with patch.object(uptime, "pushover_request", return_value=status) as request:
            self.assertEqual(uptime.main(), 0)
            self.assertTrue(uptime.alarm_due(self.state, acknowledged + timedelta(hours=12)))
        self.assertTrue(request.call_args.args[0].startswith("receipts/receipt-id.json?"))
        self.send.assert_not_called()

    def test_expired_unacknowledged_receipt_is_replaced(self):
        sent = (self.t - timedelta(hours=3, minutes=5)).isoformat()
        self.state.update(down=True, since=sent, alarmed_at=sent, receipt="old-receipt")
        with patch.object(uptime, "pushover_request", return_value={"acknowledged": 0, "expired": 1}), \
                patch.object(uptime, "save_state", self.save):
            self.assertEqual(uptime.main(), 0)
        self.assertEqual(self.events, [("message", 2)])
        self.assertEqual(self.state["since"], sent)
        self.assertEqual(self.state["receipt"], "receipt-id")

    def test_missing_secrets_warn_without_probing(self):
        with patch.object(uptime, "TOKEN", ""):
            self.assertEqual(uptime.main(), 0)
        self.assertIn("::warning::The downtime alarm is not armed", self.log.getvalue())
        self.probe.assert_not_called()

    def test_www_probe_checks_the_final_host(self):
        www = uptime.SITES[1]
        cases = ((report.SITE, None), (www, "final URL is not on the secure apex host"))
        for final_url, expected in cases:
            with self.subTest(final_url=final_url), patch.object(uptime, "MUST_CONTAIN", "Scott"), \
                    patch.object(uptime.urllib.request, "urlopen", return_value=FakeResponse(final_url, b"Scott")):
                self.assertEqual(uptime.check_once(www), expected)


class FakeResponse(io.BytesIO):
    def __init__(self, url, body):
        super().__init__(body)
        self.url = url
        self.status = 200

    def geturl(self):
        return self.url


class MonthlyReportTests(unittest.TestCase):
    def state_response(self, state):
        return 200, json.dumps({"content": base64.b64encode(json.dumps(state).encode()).decode()}).encode()

    def test_downtime_counts_only_month_overlap(self):
        state = {"down": False, "incidents": [{"start": "2026-10-31T23:50:00+00:00",
                                                "end": "2026-11-01T00:20:00+00:00", "minutes": 30}]}
        with patch.object(report, "get", return_value=self.state_response(state)):
            october = report.downtime_section(date(2026, 10, 1), date(2026, 11, 1))
            november = report.downtime_section(date(2026, 11, 1), date(2026, 12, 1))
        self.assertIn("1 time(s), 10 minutes", october)
        self.assertIn("1 time(s), 20 minutes", november)

    def test_ongoing_downtime_ends_at_month_boundary_or_now(self):
        state = {"down": True, "since": "2026-10-31T23:50:00+00:00", "incidents": []}
        with patch.object(report, "get", return_value=self.state_response(state)), patch.object(report, "datetime") as clock:
            clock.combine.side_effect = datetime.combine
            clock.fromisoformat.side_effect = datetime.fromisoformat
            clock.min = datetime.min
            clock.now.return_value = datetime(2026, 11, 1, 0, 20, tzinfo=timezone.utc)
            october = report.downtime_section(date(2026, 10, 1), date(2026, 11, 1))
            november = report.downtime_section(date(2026, 11, 1), date(2026, 12, 1))
        self.assertIn("1 time(s), 10 minutes", october)
        self.assertIn("1 time(s), 20 minutes", november)
        self.assertIn("Down right now", november)

    def test_only_missing_state_is_reported_as_none_recorded(self):
        bounds = date(2026, 10, 1), date(2026, 11, 1)
        for status, expected in ((404, "none recorded"), (403, "couldn't read downtime record")):
            with self.subTest(status=status), patch.object(report, "get", side_effect=urllib.error.HTTPError(
                    report.SITE, status, "simulated state error", {}, None)):
                self.assertIn(expected, report.downtime_section(*bounds))
        with patch.object(report, "get", return_value=(200, b"invalid state")):
            self.assertIn("couldn't read downtime record", report.downtime_section(*bounds))

    def test_external_links_and_same_page_and_cross_page_fragments(self):
        site = report.SITE
        pages = {
            site + "sitemap.xml": f'<urlset><url><loc>{site}</loc></url><url><loc>{site}work/</loc></url></urlset>'.encode(),
            site: b'''<p id="here">Here</p><a href="#here">OK</a><a href="#missing&lt;">Bad</a>
                      <a href="work/#over%20there">OK</a><a href="work/#absent">Bad</a>
                      <a href="https://www.instagram.com/user/">Blocked</a>
                      <a href="https://elsewhere.example/missing">Bad</a><a href="mailto:hello@example.com">Skip</a>''',
            site + "work/": b'<p id="over there">There</p>',
        }
        errors = {"https://www.instagram.com/user/": 429, "https://elsewhere.example/missing": 403}

        def open_url(request, timeout):
            self.assertEqual(request.get_method(), "GET")
            self.assertEqual(timeout, 15)
            url = request.full_url
            if url in errors:
                raise urllib.error.HTTPError(url, errors[url], "simulated link error", {}, None)
            return FakeResponse(url, pages[url])

        with patch.object(report.urllib.request, "urlopen", side_effect=open_url) as fetch:
            message = report.broken_links()
        self.assertEqual(fetch.call_count, 5)
        self.assertEqual(message, "<b>Broken links</b>: 3: /#missing&lt;, /work/#absent, elsewhere.example/missing (403)")

    def test_message_trims_on_a_line_boundary_without_breaking_markup(self):
        first_line = "<b>Downtime</b>: none."
        second_line = "<b>Visitors</b>: " + "x" * (1023 - len(first_line) - len("<b>Visitors</b>: "))
        self.assertEqual(len(report.trim_message([first_line, second_line])), 1024)
        self.assertEqual(report.trim_message([first_line, second_line, "<b>Devices</b>: phones"]),
                         first_line + "\n" + second_line)
        self.assertEqual(report.trim_message([first_line, "<b>" + "x" * 1024 + "</b>"]), first_line)
        self.assertEqual(report.short_value("<" + "x" * 50), "&lt;" + "x" * 38 + "…")

    def test_schedule_failure_still_sends_report_then_returns_failure(self):
        with redirect_stdout(io.StringIO()) as log, \
                patch.multiple(report, USER="stub-user", TOKEN="stub-token"), \
                patch.object(report, "keep_schedules_alive", return_value=False), \
                patch.object(report, "downtime_section", return_value="downtime"), \
                patch.object(report, "broken_links", return_value="links"), \
                patch.object(report, "cert_date", return_value="certificate"), \
                patch.object(report, "domain_date", return_value="domain"), \
                patch.object(report, "visitors_section", return_value=["visitors"]), \
                patch.object(report, "get", return_value=(200, b'{"status": 1}')) as send:
            self.assertEqual(report.main(), 1)
        data = urllib.parse.parse_qs(send.call_args.kwargs["data"].decode())
        self.assertEqual(data["message"][0].splitlines()[:5], ["downtime", "links", "certificate", "domain", "visitors"])
        self.assertEqual(log.getvalue(), "Report sent.\n")

    def test_missing_secrets_still_refresh_schedules_and_fail_the_report(self):
        with redirect_stdout(io.StringIO()), patch.multiple(report, USER="", TOKEN=""), \
                patch.object(report, "keep_schedules_alive", return_value=True) as refresh, patch.object(report, "get") as get:
            self.assertEqual(report.main(), 1)
        refresh.assert_called_once_with()
        get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
