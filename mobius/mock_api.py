"""
Mobius ZERO-DEPENDENCY Mock API Engine.
=======================================
This engine DOES NOT require numpy.
It uses simulated mathematical kernels to expose the full Mobius API surface.
Perfect for UI testing and environment bootstrapping.
"""
import json
import http.server
import uuid
import random

PORT = 8000

class MockPipeline:
    """Simulated Mobius Brain without numpy requirements."""
    def __init__(self):
        self.t = 0.0
        self.nodes = ["BE.P1", "BL.D5", "BP.D1", "BEv.D1", "BR.P1", "BT.D1"]
        self.tensors = {
            "P1_SATYA": [0.8, 0.1, 0.05],
            "P2_NOISE": [0.2, 0.8, 0.1],
            "P3_KNOWLEDGE": [0.9, 0.9, 0.9],
            "S1_TRUST": [0.7, 0.6, 0.8]
        }
        self.fields = {"PHI_T": 0.85, "PHI_S": 0.72, "PHI_B": 0.6, "PHI_M": 0.44}
        self.stability = {"s_g": 0.95, "s_t": 0.88, "s_b": 1.0, "s_m": 0.92, "s_psi": 1.0}

    def execute_cycle(self):
        self.t += 0.01
        # Randomize values to simulate "evolution"
        for k in self.tensors:
            self.tensors[k] = [max(0, min(1, v + random.uniform(-0.05, 0.05))) for v in self.tensors[k]]
        return self.get_state()

    def get_state(self):
        return {
            "time": self.t,
            "tensors": self.tensors,
            "fields": self.fields,
            "stability": self.stability,
            "lawful_closure": True,
            "morphisms_active": 2
        }

pipeline = MockPipeline()

class MockMobiusHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        path = self.path
        if path == "/version":
            self._set_headers()
            self.wfile.write(json.dumps({"system": "Mobius Mock Engine", "status": "SIMULATED"}).encode())
        elif path == "/s1/nodes":
            self._set_headers()
            self.wfile.write(json.dumps(pipeline.nodes).encode())
        elif path == "/s2/tensors":
            self._set_headers()
            self.wfile.write(json.dumps(pipeline.tensors).encode())
        elif path == "/s3/fields":
            self._set_headers()
            self.wfile.write(json.dumps(pipeline.fields).encode())
        elif path == "/s4/stability":
            self._set_headers()
            self.wfile.write(json.dumps(pipeline.stability).encode())
        elif path == "/cycle":
            self._set_headers()
            self.wfile.write(json.dumps(pipeline.execute_cycle()).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())

def run():
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, MockMobiusHandler)
    print(f"MOCK Mobius API Bridge running on port {PORT}...")
    print("NO NUMPY REQUIRED. Open http://localhost:8000/s2/tensors")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
