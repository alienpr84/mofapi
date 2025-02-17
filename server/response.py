from .types import HttpStatusCodes
from .enums import HttpHeadersContentType
import json

class Response:
  def __init__(self, body="", status:HttpStatusCodes = 200, headers=None):
    self.body = body
    self.statusCode = status
    self.headers = headers or {"Content-Type": "text/plain"}
    
  def status(self, status: HttpStatusCodes):
    self.statusCode = status
    return self
  
  def send(self, body: str | dict):
    if isinstance(body, dict):
      self.headers['Content-Type'] = HttpHeadersContentType.JSON.value
      self.body = json.dumps(body)  # Convert dictionary to JSON
    else:
      # Check if the content type is form-data
      if self.headers.get('Content-Type') == HttpHeadersContentType.FORMDATA.value:
        self.body = body  # Do not convert to JSON
      else:
        self.body = json.dumps(body)  # Convert to JSON for other content types
    return self

  def httpResponse(self):
    statusMessages = {200: "OK", 404: "Not Found", 500: "Internal Server Error"}
    statusLine = f"HTTP/1.1 {self.statusCode} {statusMessages.get(self.statusCode, 'Unknown')}"
    self.headers["Content-Length"] = str(len(self.body.encode("utf-8")))
    headers = "\r\n".join(f"{k}: {v}" for k, v in self.headers.items())
    result = f"{statusLine}\r\n{headers}\r\n\r\n{self.body}"
    return result