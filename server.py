import http.server
import socketserver
import json
import urllib.parse
import os
import random
import engine
import database
import json
import urllib.parse
import os
import engine
import database

PORT = 3000

class Handler(http.server.SimpleHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
        self.end_headers()
        
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_GET(self):
        if self.path == '/api/history':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            rows = database.get_recent_submissions(5)
            self.wfile.write(json.dumps(rows).encode())
            return
            
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            stats = engine.get_stats()
            self.wfile.write(json.dumps(stats).encode())
            return
            
        elif self.path == '/api/incidents':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            incidents = database.get_incidents()
            self.wfile.write(json.dumps(incidents).encode())
            return
            
        elif self.path == '/api/stream':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            try:
                with open('dataset.json', 'r') as f:
                    dataset = json.load(f)
                tweet = random.choice(dataset)
                self.wfile.write(json.dumps({'text': tweet}).encode())
            except Exception as e:
                self.wfile.write(json.dumps({'error': str(e)}).encode())
            return
            
        # Serve frontend file directly if requested
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
    def do_POST(self):
        if self.path == '/api/analyze':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.end_headers()
                return
                
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                text = data.get('text', '')
                result = engine.analyze_text(text)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                print(e)
                self.send_response(500)
                self.end_headers()
            return
            
if __name__ == '__main__':
    database.init_db()
    # Ensure serving from the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Backend API Server running at http://localhost:{PORT}")
        httpd.serve_forever()
