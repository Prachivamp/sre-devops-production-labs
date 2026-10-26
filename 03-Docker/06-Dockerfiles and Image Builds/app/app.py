from http.server import BaseHTTPRequestHandler, HTTPServer
import os

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Hello from my Dockerized application!")

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args), flush=True)

port = int(os.environ.get("APP_PORT", "8000"))
server = HTTPServer(("0.0.0.0", port), HealthHandler)
print(f"Application listening on port {port}", flush=True)
server.serve_forever()
