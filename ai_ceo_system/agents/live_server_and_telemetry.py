import json
import os
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PRODUCT_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "product_site")
DATA_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "data")
METRICS_PATH = os.path.join(DATA_DIR, "metrics.json")
LEARNING_STATE_PATH = os.path.join(DATA_DIR, "learning_loop_state.json")
QA_REPORT_PATH = os.path.join(DATA_DIR, "qa_health_report.json")
LATEST_BOARD_MD_PATH = os.path.join(DATA_DIR, "board_meetings", "latest_board_meeting.md")


class TelemetryAndWebHandler(SimpleHTTPRequestHandler):
    """Webサイトの配信と同時に、PV・CTAクリック・購入意向イベントの記録、および司令室APIを提供するサーバー"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PRODUCT_DIR, **kwargs)

    @staticmethod
    def _read_json_safe(path: str) -> dict:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/command-center":
            state = self._read_json_safe(LEARNING_STATE_PATH)
            metrics = self._read_json_safe(METRICS_PATH)
            qa_report = self._read_json_safe(QA_REPORT_PATH)
            day = state.get("day") or metrics.get("day") or 12
            board_json_path = os.path.join(DATA_DIR, "board_meetings", f"day{day}_meeting.json")
            board_meeting = self._read_json_safe(board_json_path)

            payload = dict(state) if state else {}
            payload["metrics"] = metrics
            payload["qa_report"] = qa_report
            payload["raw_board_meeting"] = board_meeting
            if "board_meeting" not in payload:
                payload["board_meeting"] = board_meeting
            if os.path.exists(LATEST_BOARD_MD_PATH):
                try:
                    with open(LATEST_BOARD_MD_PATH, "r", encoding="utf-8") as f:
                        payload["latest_board_markdown"] = f.read()
                except Exception:
                    pass

            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return

        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/track":
            qs = parse_qs(parsed.query)
            event = qs.get("event", ["unknown"])[0]
            self._record_event(event)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "event": event}).encode("utf-8"))
            return
        self.send_response(404)
        self.end_headers()

    def _record_event(self, event: str):
        try:
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"product_kpis": {"page_views_today": 0, "diagnostic_completions": 0, "cta_clicks": 0, "checkout_intents": 0}}

        kpis = data.setdefault("product_kpis", {})
        if event == "pageview":
            kpis["page_views_today"] = kpis.get("page_views_today", 0) + 1
        elif event == "cta_click":
            kpis["cta_clicks"] = kpis.get("cta_clicks", 0) + 1
        elif event == "checkout_intent":
            kpis["checkout_intents"] = kpis.get("checkout_intents", 0) + 1
        data["timestamp"] = datetime.now().astimezone().isoformat()

        with open(METRICS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def run_server(port: int = 8765):
    server = ThreadingHTTPServer(("0.0.0.0", port), TelemetryAndWebHandler)
    print(f"[Live Server & Telemetry] Serving AutoFlow AI at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()

