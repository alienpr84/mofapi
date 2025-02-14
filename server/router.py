from .enums import HttpMethods

class Router:
  def __init__(self):
    self.__routes = {}

  def get(self, path: str):
    def decorator(func):
      self.__routes[(path, HttpMethods.GET.value)] = func
      return func
    return decorator

  def post(self, path: str):
    def decorator(func):
      self.__routes[(path, HttpMethods.POST.value)] = func
      return func
    return decorator

  def put(self, path: str):
    def decorator(func):
      self.__routes[(path, HttpMethods.PUT.value)] = func
      return func
    return decorator

  def delete(self, path: str):
    def decorator(func):
      self.__routes[(path, HttpMethods.DELETE.value)] = func
      return func
    return decorator
  
  def findHandler(self, method, path):
      return self.__routes.get((path, method), None)
  
  @property
  def routes(self):
      return self.__routes.copy()