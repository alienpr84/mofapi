class Response:
  def __init__(self, body="", status=200, headers=None):
    self.body = body
    self.status = status
    self.headers = headers or {"Content-Type": "text/plain"}

  def to_http_response(self):
    status_messages = {200: "OK", 404: "Not Found", 500: "Internal Server Error"}
    status_line = f"HTTP/1.1 {self.status} {status_messages.get(self.status, 'Unknown')}"
    headers = "\r\n".join(f"{k}: {v}" for k, v in self.headers.items())
    return f"{status_line}\r\n{headers}\r\n\r\n{self.body}"
