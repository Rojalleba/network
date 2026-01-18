import requests
import time
import socket

def send_localhost_requests():
    for _ in range(20):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", 8000))
            s.send(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
            s.close()
        except:
            pass
        time.sleep(0.1)

def send_web_requests():
    url = "http://example.com"   # safe, harmless domain
    for _ in range(20):
        try:
            requests.get(url)
        except:
            pass
        time.sleep(0.1)

print("Starting traffic generator...")

end = time.time() + 20

while time.time() < end:
    send_localhost_requests()
    send_web_requests()

print("Traffic generation finished.")
