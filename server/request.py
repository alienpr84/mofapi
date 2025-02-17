import re
import urllib.parse
from .enums import HttpHeadersContentType
import json

class Request:
  def __init__(self, rawRequest: bytes):
    self.rawRequest = rawRequest
    self.method, self.path, self.queryParams, self.body, self.files = self.extractRequestData(rawRequest)
  
  def extractRequestData(self, rawRequest: bytes):
    rawBodyParts = rawRequest.split(b"\r\n\r\n", 1)
    headerLines = rawBodyParts[0].split(b"\r\n")
    rawBody = rawBodyParts[1] if len(rawBodyParts) > 1 else b""

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
        headers[key.decode().strip().lower()] = value.decode().strip()
      elif line == b'':
        break
    
    # For now we support only JSON and FORM-DATA
    # Extract Body
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
    
    # Extract Files
    files = {}
    if contentTypeName == HttpHeadersContentType.FORMDATA.name:
      boundary = re.search(r"boundary=(.+)", headers["content-type"])
      if not boundary:
        return

      boundary = boundary.group(1).encode()
      rawBodyParts = rawBody.split(b"--" + boundary)

      for part in rawBodyParts:
        if b'Content-Disposition: form-data;' in part:
          headers, content = part.split(b"\r\n\r\n", 1)
          content = content.rsplit(b"\r\n", 1)[0]  # Remove trailing boundary

          # Check if it's a file
          filenameMatch = re.search(b'filename="(.+?)"', headers)
          nameMatch = re.search(b'name="(.+?)"', headers)

          if filenameMatch and nameMatch:
            filename = filenameMatch.group(1).decode()
            fieldName = nameMatch.group(1).decode()
            files[fieldName] = {"filename": filename, "content": content}
          elif nameMatch:
            fieldName = nameMatch.group(1).decode()
            queryParams[fieldName] = content.decode()
 
    return (method, path, queryParams, body, files)

  def getHttpHeaderContentType(self, headers, rawBody) -> str:
    contentType = headers.get('content-type', '').lower()
    
    #if it is a formdata we need to extract correctly the content type
    
    if 'multipart/form-data' in contentType:
      contentType = 'multipart/form-data'
    
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

  def file(self, fieldName):
    """Returns file content and filename for a given field."""
    return self.files.get(fieldName, None)
