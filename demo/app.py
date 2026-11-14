"""Offline ReserveWeek screen, using only the Python standard library."""
import argparse
import csv
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    with (ROOT / 'artifacts/validation_replay.csv').open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        parser.error('validation_replay.csv contains no dates')
    payload = json.dumps([{key: row[key] for key in
                          ('as_of', 'model_q80', 'training_q80', 'actual_gbp')}
                         for row in rows]).replace('<', '\\u003c')
    page = (ROOT / 'demo/index.html').read_text().replace('__REPLAY_DATA__', payload).encode()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in ('/', '/index.html'):
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(page)))
            self.end_headers()
            self.wfile.write(page)

    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'ReserveWeek: http://127.0.0.1:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
