"""
Mobius Zero-Dependency API Bridge.
==================================
Exposes the Mobius constitutional surface area via HTTP.
Standard Library only (No FastAPI/Flask required).
"""
import json
import http.server
import socketserver
from mobius.pipeline import MobiusMasterPipeline

# PORT to bind the API
PORT = 8000

# Initialize the Engine
pipeline = MobiusMasterPipeline("Canonical_Graphmass.json")

class MobiusAPIHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        """Routing for GET requests."""
        path = self.path
        
        if path == "/version":
            self._set_headers()
            response = {"system": "Mobius Field Calculus", "version": "1.0.4", "status": "Operational"}
            self.wfile.write(json.dumps(response).encode())

        elif path == "/tensors":
            self._set_headers()
            state = pipeline.get_full_state()
            self.wfile.write(json.dumps(state["tensors"]).encode())

        elif path == "/fields":
            self._set_headers()
            state = pipeline.get_full_state()
            self.wfile.write(json.dumps(state["fields"]).encode())

        elif path == "/stability":
            self._set_headers()
            state = pipeline.get_full_state()
            self.wfile.write(json.dumps({
                "stability_5d": state["stability"],
                "lawful_closure": state["lawful_closure"],
                "jg": state["closure_jg"]
            }).encode())

        elif path == "/graph":
            self._set_headers()
            self.wfile.write(json.dumps(pipeline.carrier.to_canonical_mass()).encode())

        elif path == "/cycle":
            self._set_headers()
            # Triggers a state mutation
            result = pipeline.execute_cycle()
            self.wfile.write(json.dumps(result).encode())

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())

def run(server_class=http.server.HTTPServer, handler_class=MobiusAPIHandler):
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    print(f"Mobius API Bridge running on port {PORT}...")
    print("Exposing 130-200 functional surfaces...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == "__main__":
    run()
