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
    statusMessages = {
      # 1xx: Informational Responses
      100: "Continue",
      101: "Switching Protocols",
      102: "Processing",
      103: "Early Hints",

      # 2xx: Success
      200: "OK",
      201: "Created",
      202: "Accepted",
      203: "Non-Authoritative Information",
      204: "No Content",
      205: "Reset Content",
      206: "Partial Content",
      207: "Multi-Status",
      208: "Already Reported",
      226: "IM Used",

      # 3xx: Redirection
      300: "Multiple Choices",
      301: "Moved Permanently",
      302: "Found",
      303: "See Other",
      304: "Not Modified",
      305: "Use Proxy",
      306: "Unused",  # Reserved
      307: "Temporary Redirect",
      308: "Permanent Redirect",

      # 4xx: Client Errors
      400: "Bad Request",
      401: "Unauthorized",
      402: "Payment Required",
      403: "Forbidden",
      404: "Not Found",
      405: "Method Not Allowed",
      406: "Not Acceptable",
      407: "Proxy Authentication Required",
      408: "Request Timeout",
      409: "Conflict",
      410: "Gone",
      411: "Length Required",
      412: "Precondition Failed",
      413: "Payload Too Large",
      414: "URI Too Long",
      415: "Unsupported Media Type",
      416: "Range Not Satisfiable",
      417: "Expectation Failed",
      418: "I'm a Teapot",
      421: "Misdirected Request",
      422: "Unprocessable Entity",
      423: "Locked",
      424: "Failed Dependency",
      425: "Too Early",
      426: "Upgrade Required",
      428: "Precondition Required",
      429: "Too Many Requests",
      431: "Request Header Fields Too Large",
      451: "Unavailable For Legal Reasons",

      # 5xx: Server Errors
      500: "Internal Server Error",
      501: "Not Implemented",
      502: "Bad Gateway",
      503: "Service Unavailable",
      504: "Gateway Timeout",
      505: "HTTP Version Not Supported",
      506: "Variant Also Negotiates",
      507: "Insufficient Storage",
      508: "Loop Detected",
      510: "Not Extended",
      511: "Network Authentication Required"
    }
    statusLine = f"HTTP/1.1 {self.statusCode} {statusMessages.get(self.statusCode, 'Unknown')}"
    self.headers["Content-Length"] = str(len(self.body.encode("utf-8")))
    headers = "\r\n".join(f"{k}: {v}" for k, v in self.headers.items())
    result = f"{statusLine}\r\n{headers}\r\n\r\n{self.body}"
    return result