from .types import HttpStatusCodes
from .enums import HttpContentTypeHeaders

class Response:
  def __init__(self, body="", status:HttpStatusCodes = 200, headers=None):
    self.body = body
    self.statusCode = status
    self.headers = headers or {"Content-Type": "text/plain"}
    
  def status(self, status: HttpStatusCodes):
    self.statusCode = status
    print(self.statusCode)
    return self
  
  def send(self, body: str | dict):
    if isinstance(body, dict):
      self.headers['Content-Type'] = HttpContentTypeHeaders.JSON_COTENT_TYPE.value
    self.body = body
    return self

  def httpResponse(self):
    statusMessages = {200: "OK", 404: "Not Found", 500: "Internal Server Error"}
    statusLine = f"HTTP/1.1 {self.statusCode} {statusMessages.get(self.statusCode, 'Unknown')}"
    headers = "\r\n".join(f"{k}: {v}" for k, v in self.headers.items())
    return f"{statusLine}\r\n{headers}\r\n\r\n{self.body}"
