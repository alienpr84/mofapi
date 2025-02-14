import json
from urllib.parse import urlparse, parse_qs

class Request:
  def __init__(self, rawData):
    lines = rawData.split("\r\n")
    requestLine = lines[0].split(" ")

    self.method = requestLine[0]
    self.path = urlparse(requestLine[1]).path
    self.queryParams = parse_qs(urlparse(requestLine[1]).query)
    self.headers = {}

    bodyIndex = 0
    for i, line in enumerate(lines[1:]):
      if line == "":
        bodyIndex = i + 2
        break
      key, value = line.split(": ", 1)
      self.headers[key] = value
    
    rawBody = "\r\n".join(lines[bodyIndex:])
    try:
      self.body = json.loads(rawBody) if rawBody else None
    except json.JSONDecodeError:
      self.body = rawBody
      
    # print(f'method: {self.method}, path: {self.path}, queryParams: {self.queryParams}, headers: {self.headers}, body: {self.body}')
