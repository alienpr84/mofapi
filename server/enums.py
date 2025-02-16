from enum import Enum

class HttpMethods(Enum):
  GET='GET'
  POST='POST'
  PUT='PUT'
  DELETE='DELETE'
  PATCH='PATCH'
  
class HttpHeadersContentType(Enum):
  JSON = 'application/json'
  TEXT = 'text/plain'
  FORMDATA = 'multipart/form-data'
  X_WWW_FORM_URLENCODED = 'application/x-www-form-urlencoded'
  JAVASCRIPT = 'text/javascript'
  HTML = 'text/html'
  XML = ('application/xml', 'text/xml')
  GRAPHQL = 'application/graphql'
  BINARY = 'application/octet-stream'
  