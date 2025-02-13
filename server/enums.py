from enum import Enum

class HttpMethods(Enum):
  GET='GET'
  POST='POST'
  PUT='PUT'
  DELETE='DELETE'
  PATCH='PATCH'
  
class HttpContentTypeHeaders(Enum):
  JSON_COTENT_TYPE = 'application/json'
  TEXT_COTENT_TYPE = 'text/plain'