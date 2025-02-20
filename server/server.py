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
      rawRequest = b""
      total_bytes_received = 0  # Track total received bytes

      # 🔹 Keep receiving data until client stops sending
      while True:
        part = clientSocket.recv(4096)  # Read in chunks
        if not part:
          break  # 🔸 Client closed connection

        rawRequest += part
        total_bytes_received += len(part)
        print(f"Received chunk: {len(part)} bytes (Total: {total_bytes_received} bytes)")

        # 🔹 Stop reading if headers are received
        if b"\r\n\r\n" in rawRequest:
          break  # 🔸 Headers received

      print(f"Headers received, total size: {total_bytes_received} bytes")

      # 🔹 Extract Content-Length (if exists)
      request = Request()
      _, rawHeaders, _ = request.splitRawRequest(rawRequest)      
      headers = request.extractHeaders(rawHeaders)
      content_length = headers.get("content-length", '')
      if content_length and content_length.isdigit():
        content_length = int(content_length)

        # 🔹 Find where body starts
        body_start = rawRequest.find(b"\r\n\r\n") + 4
        body_length = len(rawRequest) - body_start

        print(f"Content-Length: {content_length}, Body received so far: {body_length}")

        # 🔹 Keep reading until full body is received
        while body_length < content_length:
          part = clientSocket.recv(min(4096, content_length - body_length))
          if not part:
            break
          rawRequest += part
          body_length += len(part)
          print(f"Received body chunk: {len(part)} bytes (Total: {body_length}/{content_length})")

      print(f"Final request size: {len(rawRequest)} bytes")

      request.processRawRequest(rawRequest)
      # 🔹 Process request
      response = Response("Not Found", 404)
      if not request.isRequestValid.get('state'):
        status = request.isRequestValid.get('status')
        message = request.isRequestValid.get('message')
        response.status(status).send(message)
      else:
        handler = self.router.findHandler(request.method, request.path)
        response = handler(request, response) if handler else response

      # 🔹 Send response
      clientSocket.sendall(response.httpResponse().encode())
      print("Response sent!")

    except Exception as e:
      print(f"Error handling client: {e}")
    finally:
      clientSocket.close()
      print("Connection closed")


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