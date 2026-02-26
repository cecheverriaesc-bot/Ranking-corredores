from http.server import BaseHTTPRequestHandler
import json
import statistics

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            mean_val = statistics.mean([1, 2, 3])
            response = {
                "status": "OK",
                "message": "Minimal v2 with statistics works!",
                "mean": mean_val
            }
        except Exception as e:
            response = {
                "status": "ERROR",
                "error": str(e)
            }
        
        self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
