import re
import urllib.parse
from .enums import HttpHeadersContentType, HttpMethods
import json

class Request:
  def __init__(self, rawRequest: bytes):
    self.rawRequest = rawRequest
    self.isRequestValid = {
      'state': True,
      'status': 200,
      'message': 'Successful'
    }
    self.method, self.path, self.queryParams, self.body, self.files = self.extractRequestData(rawRequest)
  
  def extractRequestData(self, rawRequest: bytes):
    method = None
    path = None
    queryParams = None
    body = None
    files = None

    try:
      rawRequestSplitted = rawRequest.split(b"\r\n\r\n", 1)
      rawHeaders = rawRequestSplitted[0].split(b"\r\n")
      rawBody = rawRequestSplitted[1] if len(rawRequestSplitted) > 1 else b""

      # Extract the request line (e.g., "POST /upload?name=John HTTP/1.1")
      httpRequest = rawHeaders[0].decode()
      headers = rawHeaders[1:]
      method, fullPath, _ = httpRequest.split(" ")

      # Extract path and query parameters
      parsedUrl = urllib.parse.urlparse(fullPath)
      path = parsedUrl.path
      queryParams = urllib.parse.parse_qs(parsedUrl.query)
      
      # Extract headers
      headers = self.extractHeaders(headers)
      contentTypeName = self.getHttpHeaderContentType(headers, rawBody)  
      
      if(method == HttpMethods.GET.value):
        if(contentTypeName == HttpHeadersContentType.FORMDATA.name):
          self.isRequestValid['state'] = False
          self.isRequestValid['status'] = 400
          self.isRequestValid['message'] = {'message': 'Not allowed multipart/form-data for http GET method.' }
      elif(method == HttpMethods.POST.value): 
        body = self.extractBody(contentTypeName, rawBody)
        files = self.extractFiles(contentTypeName, headers, rawBody, queryParams)

    except Exception as e:
      print(f"Error extracting request data: {e}")
    finally:
      return (method, path, queryParams, body, files)

  def extractHeaders(self, rawHeaders):
    headers = {}
    for header in rawHeaders:
      if b':' in header:
        key, value = header.split(b':', 1)
        headers[key.decode().strip().lower()] = value.decode().strip()
      elif header == b'':
        break
    return headers

  def extractBody(self, contentTypeName, rawBody):
    if contentTypeName == HttpHeadersContentType.JSON.name:
      try:
        return json.loads(rawBody.decode('utf-8'))
      except json.JSONDecodeError as e:
        print(f'Json decode error: {e}')
      except AttributeError as e:
        print(f"Attribute Error: {e}")
    return {}

  def extractFiles(self, contentTypeName, headers, rawBody, queryParams):
    files = {}
    if contentTypeName == HttpHeadersContentType.FORMDATA.name:
      boundary = re.search(r"boundary=(.+)", headers.get("content-type", ""))
      if not boundary:
        print("Boundary not found in Content-Type header")
        return files

      boundary = boundary.group(1).encode()
      rawRequestSplitted = rawBody.split(b"--" + boundary)

      for part in rawRequestSplitted:
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
    return files

  def getHttpHeaderContentType(self, headers, rawBody) -> str:
    contentType = headers.get('content-type', '').lower()
    
    # If it is a form-data we need to extract correctly the content type
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