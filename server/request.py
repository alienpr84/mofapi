import re
import urllib.parse

class Request:
  def __init__(self, rawRequest: bytes):
    self.rawRequest = rawRequest
    self.method = None
    self.path = None
    self.queryParams = {}
    self.headers = {}
    self.body = None
    self.files = {}
    # print(rawRequest)
    self.parseRequest()

  def parseRequest(self):
    """Parses the raw HTTP request."""
    try:
      # Split headers and body
      parts = self.rawRequest.split(b"\r\n\r\n", 1)
      headerLines = parts[0].split(b"\r\n")
      self.body = parts[1] if len(parts) > 1 else b""

      # Extract the request line (e.g., "POST /upload?name=John HTTP/1.1")
      requestLine = headerLines[0].decode()
      method, fullPath, _ = requestLine.split(" ")

      # Extract path and query parameters
      parsedUrl = urllib.parse.urlparse(fullPath)
      self.method = method
      self.path = parsedUrl.path
      self.queryParams = urllib.parse.parse_qs(parsedUrl.query)

      # Extract headers
      for line in headerLines[1:]:
        key, value = line.decode().split(": ", 1)
        self.headers[key.lower()] = value

      # Handle multipart form-data (for file uploads)
      if "content-type" in self.headers and "multipart/form-data" in self.headers["content-type"]:
        self.parseMultipartBody()

    except Exception as e:
      print(f"Error parsing request: {e}")

  def parseMultipartBody(self):
    """Parses multipart form-data (files and fields)."""
    boundary = re.search(r"boundary=(.+)", self.headers["content-type"])
    if not boundary:
      return

    boundary = boundary.group(1).encode()
    parts = self.body.split(b"--" + boundary)

    for part in parts:
      if b'Content-Disposition: form-data;' in part:
        headers, content = part.split(b"\r\n\r\n", 1)
        content = content.rsplit(b"\r\n", 1)[0]  # Remove trailing boundary

        # Check if it's a file
        filenameMatch = re.search(b'filename="(.+?)"', headers)
        nameMatch = re.search(b'name="(.+?)"', headers)

        if filenameMatch and nameMatch:
          filename = filenameMatch.group(1).decode()
          fieldName = nameMatch.group(1).decode()
          self.files[fieldName] = {"filename": filename, "content": content}
        elif nameMatch:
          fieldName = nameMatch.group(1).decode()
          self.queryParams[fieldName] = content.decode()

  def json(self):
    """Returns JSON-decoded body (if applicable)."""
    import json
    try:
      return json.loads(self.body.decode())
    except json.JSONDecodeError:
      return None

  def form(self):
    """Parses `application/x-www-form-urlencoded` form data."""
    if "content-type" in self.headers and "application/x-www-form-urlencoded" in self.headers["content-type"]:
      return urllib.parse.parse_qs(self.body.decode())
    return {}

  def file(self, field_name):
    """Returns file content and filename for a given field."""
    return self.files.get(field_name, None)
