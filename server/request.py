import json
from urllib.parse import urlparse, parse_qs

class Request:
  def __init__(self, raw_data):
    lines = raw_data.split("\r\n")
    request_line = lines[0].split(" ")

    self.method = request_line[0]
    self.path = urlparse(request_line[1]).path
    self.queryParams = parse_qs(urlparse(request_line[1]).query)
    self.headers = {}

    body_index = 0
    for i, line in enumerate(lines[1:]):
      if line == "":
        body_index = i + 2
        break
      key, value = line.split(": ", 1)
      self.headers[key] = value
    
    raw_body = "\r\n".join(lines[body_index:])
    try:
      self.body = json.loads(raw_body) if raw_body else None
    except json.JSONDecodeError:
      self.body = raw_body
      
    print(f'method: {self.method}, path: {self.path}, queryParams: {self.queryParams}, headers: {self.headers}, body: {self.body}')
