from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import hashlib
import hmac
import json
import os
import secrets
import sys
import time

from generate_dashboard import parse_dashboard

ROOT = Path(__file__).resolve().parent
HOST = '0.0.0.0'
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
PASSWORD = os.environ.get('DASHBOARD_PASSWORD', 'rahman')
SESSION_COOKIE = 'm268_dashboard_session'
SESSION_DURATION_SECONDS = 20 * 60
ACTIVE_SESSIONS = {}
LOGIN_PAGE = """<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>M268 Dashboard - Izin Akses</title>
  <style>
    body{margin:0;min-height:100vh;display:grid;place-items:center;background:#101827;color:#f5f7fb;font:16px system-ui,sans-serif}
    form{width:min(360px,calc(100% - 40px));padding:28px;border-radius:18px;background:#18243a;box-shadow:0 12px 40px #0006}
    h1{font-size:1.35rem;margin:0 0 8px}p{color:#aab7cc;font-size:.92rem}label{display:block;margin:20px 0 7px}
    input,button{box-sizing:border-box;width:100%;padding:12px;border-radius:9px;border:1px solid #43536d;font:inherit}
    input{background:#0e1727;color:#fff}button{margin-top:18px;background:#2f8cff;color:#fff;border:0;font-weight:700;cursor:pointer}
    #error{color:#ff9e9e;min-height:1.3em;margin-top:12px}
  </style>
</head>
<body><form id="login"><h1>M268 Dashboard</h1><p>Masukkan kata sandi untuk meminta izin akses.</p>
<label for="password">Kata sandi</label><input id="password" name="password" type="password" autocomplete="current-password" required>
<button type="submit">Minta izin akses</button><div id="error"></div></form>
<script>
document.getElementById('login').addEventListener('submit', async event => {
  event.preventDefault();
  const error = document.getElementById('error');
  error.textContent = '';
  const response = await fetch('/login', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({password:document.getElementById('password').value})});
  if (response.ok) { window.location.href = '/Mr.RI'; } else { error.textContent = 'Kata sandi salah.'; }
});
</script></body></html>"""


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _authorized(self):
        cookie = self.headers.get('Cookie', '')
        for part in cookie.split(';'):
            name, separator, value = part.strip().partition('=')
            if name != SESSION_COOKIE or not separator:
                continue
            expires_at = ACTIVE_SESSIONS.get(value)
            if not expires_at:
                return False
            if time.time() >= expires_at:
                ACTIVE_SESSIONS.pop(value, None)
                return False
            return True
        return False

    def _redirect_login(self):
        self.send_response(302)
        self.send_header('Location', '/login')
        self.end_headers()

    def do_POST(self):
        if self.path.split('?', 1)[0] != '/login':
            self.send_error(404)
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            body = json.loads(self.rfile.read(length) or b'{}')
            supplied = str(body.get('password', ''))
        except (ValueError, json.JSONDecodeError):
            supplied = ''
        if hmac.compare_digest(hashlib.sha256(supplied.encode()).digest(),
                               hashlib.sha256(PASSWORD.encode()).digest()):
            self.send_response(204)
            token = secrets.token_urlsafe(32)
            ACTIVE_SESSIONS[token] = time.time() + SESSION_DURATION_SECONDS
            self.send_header(
                'Set-Cookie',
                f'{SESSION_COOKIE}={token}; Max-Age={SESSION_DURATION_SECONDS}; '
                'HttpOnly; SameSite=Lax; Path=/'
            )
            self.end_headers()
        else:
            self.send_error(401)

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/login':
            payload = LOGIN_PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if not self._authorized():
            self._redirect_login()
            return
        if path in ('/Mr.RI', '/Mr.RI/'):
            self.path = '/index.html'
        if path == '/dashboard_data.js':
            payload = f"window.DASHBOARD_DATA = {json.dumps(parse_dashboard(), ensure_ascii=False)};\n".encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript; charset=utf-8')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        super().do_GET()


if __name__ == '__main__':
    print(f'Dashboard running at http://localhost:{PORT}/Mr.RI')
    print('Set DASHBOARD_PASSWORD in the hosting environment to change the default password.')
    ThreadingHTTPServer((HOST, PORT), DashboardHandler).serve_forever()
