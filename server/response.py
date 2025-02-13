from .types import HttpStatusCodes

class Response:
  def __init__(self, body="", status:HttpStatusCodes = 200, headers=None):
    self.body = body
    self.status = status
    self.headers = headers or {"Content-Type": "text/plain"}
    
  def status(self, status: HttpStatusCodes):
    self.status = status
    return self

  def to_http_response(self):
    statusMessages = {200: "OK", 404: "Not Found", 500: "Internal Server Error"}
    statusLine = f"HTTP/1.1 {self.status} {statusMessages.get(self.status, 'Unknown')}"
    headers = "\r\n".join(f"{k}: {v}" for k, v in self.headers.items())
    return f"{statusLine}\r\n{headers}\r\n\r\n{self.body}"
