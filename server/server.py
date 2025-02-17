from .request import Request
from .response import Response
import socket
from socket import socket as Socket
import threading
from .router import Router
import select

class Server:
  def __init__(self, router: Router, host: str = '127.0.0.1'):
    self.host = host
    self.router = router

  def handleClient(self, clientSocket: Socket) -> None:
    try:
      rawRequest = clientSocket.recv(1024)
      request = Request(rawRequest)
      response = Response("Not Found", 404)
      handler = self.router.findHandler(request.method, request.path)
      response = handler(request, response) if handler else response
      clientSocket.sendall(response.httpResponse().encode())
    finally:
      clientSocket.close()

  def listen(self, port: int = None, msg: str = None) -> None:
    port = port if port is not None else 8000
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((self.host, port))
    serverSocket.listen(5)
    serverSocket.setblocking(False)  # Set the server socket to non-blocking mode
    isRunning = True
    listenMessage = msg if msg is not None else f"Server running on {self.host}:{port}... (Press Ctrl+C to stop)"
    print(listenMessage)

    try:
      while isRunning:
        # Use select to handle socket readiness and avoid blocking forever
        readable, _, _ = select.select([serverSocket], [], [], 1)

        if readable:
          clientSocket, _ = serverSocket.accept()
          clientThread = threading.Thread(target=self.handleClient, args=(clientSocket, ))
          clientThread.start()
    except KeyboardInterrupt:
      print("\nServer shutting down gracefully...")
      isRunning = False
    finally:
      serverSocket.close()
