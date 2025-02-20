import re
import urllib.parse
from .enums import HttpHeadersContentType, HttpMethods
import json

class Request:
  def __init__(self):
    self.method = None
    self.path = None
    self.queryParams = None
    self.headers = None
    self.body = None
    self.files = None
    self.isRequestValid = {
      'state': True,
      'status': 200,
      'message': 'Successful'
    }

  def splitRawRequest(self, rawRequest):
    rawRequestSplitted = rawRequest.split(b"\r\n\r\n", 1)
    rawRequestLineAndHeaders = rawRequestSplitted[0].split(b"\r\n")
    rawRequestLine = rawRequestLineAndHeaders[0].decode()
    rawHeaders = rawRequestLineAndHeaders[1:]
    rawBody = rawRequestSplitted[1] if len(rawRequestSplitted) > 1 else b""
    return rawRequestLine, rawHeaders, rawBody
  
  def extractRequestLineData(self, rawRequestLine: str):
    method, fullPath, _ = rawRequestLine.split(" ")
    parsedUrl = urllib.parse.urlparse(fullPath)
    path = parsedUrl.path
    queryParams = urllib.parse.parse_qs(parsedUrl.query)
    return method, path, queryParams
      
  def processRawRequest(self, rawRequest: bytes):
    try:
      rawRequestLine, rawHeaders, rawBody = self.splitRawRequest(rawRequest)      
      self.method, self.path, self.queryParams = self.extractRequestLineData(rawRequestLine)
      self.headers = self.extractHeaders(rawHeaders)
      contentType = self.headers.get('content-type', '')  
      
      if(self.method == HttpMethods.GET.value):
        if(HttpHeadersContentType.FORMDATA.value in contentType):
          self.isRequestValid['state'] = False
          self.isRequestValid['status'] = 400
          self.isRequestValid['message'] = {'message': 'Not allowed multipart/form-data for http GET method.' }
      elif(self.method == HttpMethods.POST.value): 
        self.body = self.extractBodyData(contentType, rawBody)
        self.files = self.extractFilesData(contentType, self.headers, rawBody, self.queryParams)

    except Exception as e:
      print(f"Error extracting request data: {e}")

  def extractHeaders(self, rawHeaders):
    headers = {}
    for header in rawHeaders:
      if b':' in header:
        key, value = header.split(b':', 1)
        headers[key.decode().strip().lower()] = value.decode().strip()
      elif header == b'':
        break
    return headers

  def extractBodyData(self, contentType, rawBody):
    if contentType == HttpHeadersContentType.JSON.value:
      try:
        return json.loads(rawBody.decode('utf-8'))
      except json.JSONDecodeError as e:
        print(f'Json decode error: {e}')
      except AttributeError as e:
        print(f"Attribute Error: {e}")
    return {}

  def extractFilesData(self, contentType, headers, rawBody, queryParams):
    files = {}
    if HttpHeadersContentType.FORMDATA.value in contentType:
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

  def file(self, fieldName):
    """Returns file content and filename for a given field."""
    return self.files.get(fieldName, None)