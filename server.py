"""Small local API and static-file server for the figure skating project."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import re
import sqlite3


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "skating.db"
QUESTIONS = [
    {"id": 1, "question": "Which discipline features two skaters, lifts, and throw jumps?", "choices": ["Men's singles", "Women's singles", "Pair skating", "Ice dance"], "answer": 2},
    {"id": 2, "question": "Which discipline especially emphasizes dance steps, rhythm, and partnership?", "choices": ["Ice dance", "Men's singles", "Women's singles", "Pair skating"], "answer": 0},
    {"id": 3, "question": "What do men's and women's singles have in common?", "choices": ["One skater performs the program", "Both require lifts", "Two skaters perform together", "Neither includes jumps"], "answer": 0},
    {"id": 4, "question": "Besides technical elements, what else can you watch for in a program?", "choices": ["Musical expression and choreography", "The color of the ice", "The number of seats", "The outdoor temperature"], "answer": 0},
]


def connect_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        visitor_id TEXT NOT NULL,
        score INTEGER NOT NULL,
        total INTEGER NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )""")
    return db


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "web"), **kwargs)

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        origin = self.headers.get("Origin", "")
        if re.fullmatch(r"http://(?:localhost|127\.0\.0\.1):\d+", origin):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        origin = self.headers.get("Origin", "")
        if self.path != "/api/attempts" or not re.fullmatch(r"http://(?:localhost|127\.0\.0\.1):\d+", origin):
            return self.send_json(403, {"error": "Origin not allowed"})
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Vary", "Origin")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/questions":
            self.send_json(200, [{k: v for k, v in q.items() if k != "answer"} for q in QUESTIONS])
        elif self.path.startswith("/api/attempts?"):
            from urllib.parse import parse_qs, urlsplit

            visitor_id = parse_qs(urlsplit(self.path).query).get("visitor_id", [""])[0]
            if not re.fullmatch(r"[0-9a-f]{32}", visitor_id):
                return self.send_json(400, {"error": "Invalid visitor ID"})
            with connect_db() as db:
                rows = db.execute(
                    "SELECT score, total, created_at FROM attempts WHERE visitor_id = ? ORDER BY id DESC LIMIT 10",
                    (visitor_id,),
                ).fetchall()
            self.send_json(200, [dict(row) for row in rows])
        elif self.path.startswith("/api/"):
            self.send_json(404, {"error": "API endpoint not found"})
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != "/api/attempts":
            return self.send_json(404, {"error": "API endpoint not found"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size > 4096:
                raise ValueError()
            data = json.loads(self.rfile.read(size))
            visitor_id, answers = data["visitor_id"], data["answers"]
            if not re.fullmatch(r"[0-9a-f]{32}", visitor_id):
                raise ValueError()
            if not isinstance(answers, list) or len(answers) != len(QUESTIONS):
                raise ValueError()
            if any(type(answer) is not int or answer not in range(4) for answer in answers):
                raise ValueError()
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            return self.send_json(400, {"error": "Please answer every question before submitting"})

        score = sum(answer == q["answer"] for answer, q in zip(answers, QUESTIONS))
        with connect_db() as db:
            db.execute(
                "INSERT INTO attempts (visitor_id, score, total) VALUES (?, ?, ?)",
                (visitor_id, score, len(QUESTIONS)),
            )
        self.send_json(201, {"score": score, "total": len(QUESTIONS)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"Open http://localhost:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
