from .request import Request
from .response import Response
import socket
import threading
from .router import Router
import select

class Server:
  def __init__(self, router: Router, host: str = '127.0.0.1'):
    self.host = host
    self.port = 8000
    self.listenMessage = f"Server running on {self.host}:{self.port}... (Press Ctrl+C to stop)"
    self.router = router


  def handle_client(self, client_socket):
    try:
      raw_request = client_socket.recv(1024).decode()
      request = Request(raw_request)

      handler = self.router.find_handler(request.method, request.path)
      response = handler(request) if handler else Response("Not Found", 404)

      client_socket.sendall(response.to_http_response().encode())
    finally:
        client_socket.close()

  def listen(self, port: int = None, msg: str = None):
    self.port = port if port is not None else self.port
    self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.server_socket.bind((self.host, self.port))
    self.server_socket.listen(5)
    self.server_socket.setblocking(False)  # Set the server socket to non-blocking mode
    self.running = True
    self.listenMessage = msg if msg is not None else self.listenMessage
    print(self.listenMessage)

    try:
      while self.running:
        # Use select to handle socket readiness and avoid blocking forever
        readable, _, _ = select.select([self.server_socket], [], [], 1)

        if readable:
            client_socket, _ = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, ))
            client_thread.start()

    except KeyboardInterrupt:
        print("\nServer shutting down gracefully...")
        self.running = False
    finally:
        self.server_socket.close()
