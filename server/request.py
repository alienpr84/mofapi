import re
import urllib.parse
from .enums import HttpHeadersContentType
import json

class Request:
  def __init__(self, rawRequest: bytes):
    self.rawRequest = rawRequest
    self.method, self.path, self.queryParams, self.body = self.extractRequestData(rawRequest)
    self.files = {}

  
  def extractRequestData(self, rawRequest: bytes):
    parts = rawRequest.split(b"\r\n\r\n", 1)
    headerLines = parts[0].split(b"\r\n")
    rawBody = parts[1] if len(parts) > 1 else b""

    # Extract the request line (e.g., "POST /upload?name=John HTTP/1.1")
    requestLine = headerLines[0].decode()
    method, fullPath, _ = requestLine.split(" ")

    # Extract path and query parameters
    parsedUrl = urllib.parse.urlparse(fullPath)
    path = parsedUrl.path
    
    queryParams = urllib.parse.parse_qs(parsedUrl.query)
    
    # extract headers
    headers = {}
    for line in headerLines:
      if b':' in line:
        key, value = line.split(b':', 1)
        headers[key.decode().strip()] = value.decode().strip()
      elif line == b'':
        break
    
    # extract body, file and parameters depending on the content type. For now we support only JSON and FORM-DATA
    contentTypeName = self.getHttpHeaderContentType(headers, rawBody)
    body = {}
    if contentTypeName == HttpHeadersContentType.JSON.name:
      try:
        body = json.loads(rawBody.decode('utf-8'))
      except json.JSONDecodeError as e:
        print(f'Json decode error: {e}')
        body = None
      except AttributeError as e:
        print(f"Attribute Error: {e}")  # If self.rawBody is None
        body = None
        
      return (method, path, queryParams, body)

  def getHttpHeaderContentType(self, headers, rawBody) -> str:
    contentType = headers.get('Content-Type', '').lower()
    
    if not rawBody:
      return None
    applicationXml, textXml = HttpHeadersContentType.XML.value
    if HttpHeadersContentType.FORMDATA.value in contentType:
      return HttpHeadersContentType.FORMDATA.name
    elif HttpHeadersContentType.JSON.value in contentType:
      return HttpHeadersContentType.JSON.name
    elif HttpHeadersContentType.X_WWW_FORM_URLENCODED.value in contentType:
      return HttpHeadersContentType.X_WWW_FORM_URLENCODED.name
    elif HttpHeadersContentType.TEXT.value in contentType:
      return HttpHeadersContentType.TEXT.name
    elif HttpHeadersContentType.JAVASCRIPT.value in contentType:
      return HttpHeadersContentType.JAVASCRIPT.name
    elif HttpHeadersContentType.HTML.value in contentType:
      return HttpHeadersContentType.HTML.name
    elif applicationXml in contentType or textXml in contentType:
      return HttpHeadersContentType.XML.name
    elif HttpHeadersContentType.GRAPHQL.value in contentType:
      return HttpHeadersContentType.GRAPHQL.name
    elif HttpHeadersContentType.BINARY.value in contentType:
      return HttpHeadersContentType.BINARY.name
    else:
      return "unknown"  # Content-Type is not recognized  

  # def parseRequest(self):
    # """Parses the raw HTTP request."""
    # try:
    #   # Split headers and body
    #   parts = self.rawRequest.split(b"\r\n\r\n", 1)
    #   headerLines = parts[0].split(b"\r\n")
    #   self.body = parts[1] if len(parts) > 1 else b""

    #   # Extract the request line (e.g., "POST /upload?name=John HTTP/1.1")
    #   requestLine = headerLines[0].decode()
    #   method, fullPath, _ = requestLine.split(" ")

    #   # Extract path and query parameters
    #   parsedUrl = urllib.parse.urlparse(fullPath)
    #   self.method = method
    #   self.path = parsedUrl.path
    #   self.queryParams = urllib.parse.parse_qs(parsedUrl.query)

    #   # Extract headers
    #   for line in headerLines[1:]:
    #     key, value = line.decode().split(": ", 1)
    #     self.headers[key.lower()] = value

    #   # Handle multipart form-data (for file uploads)
    #   if "content-type" in self.headers and "multipart/form-data" in self.headers["content-type"]:
    #     self.parseMultipartBody()

    # except Exception as e:
    #   print(f"Error parsing request: {e}")

  # def parseMultipartBody(self):
  #   """Parses multipart form-data (files and fields)."""
  #   boundary = re.search(r"boundary=(.+)", self.headers["content-type"])
  #   if not boundary:
  #     return

  #   boundary = boundary.group(1).encode()
  #   parts = self.body.split(b"--" + boundary)

  #   for part in parts:
  #     if b'Content-Disposition: form-data;' in part:
  #       headers, content = part.split(b"\r\n\r\n", 1)
  #       content = content.rsplit(b"\r\n", 1)[0]  # Remove trailing boundary

  #       # Check if it's a file
  #       filenameMatch = re.search(b'filename="(.+?)"', headers)
  #       nameMatch = re.search(b'name="(.+?)"', headers)

  #       if filenameMatch and nameMatch:
  #         filename = filenameMatch.group(1).decode()
  #         fieldName = nameMatch.group(1).decode()
  #         self.files[fieldName] = {"filename": filename, "content": content}
  #       elif nameMatch:
  #         fieldName = nameMatch.group(1).decode()
  #         self.queryParams[fieldName] = content.decode()

  # def json(self):
  #   """Returns JSON-decoded body (if applicable)."""
  #   import json
  #   try:
  #     return json.loads(self.body.decode())
  #   except json.JSONDecodeError:
  #     return None

  # def form(self):
  #   """Parses `application/x-www-form-urlencoded` form data."""
  #   if "content-type" in self.headers and "application/x-www-form-urlencoded" in self.headers["content-type"]:
  #     return urllib.parse.parse_qs(self.body.decode())
  #   return {}

  def file(self, fieldName):
    """Returns file content and filename for a given field."""
    return self.files.get(fieldName, None)
