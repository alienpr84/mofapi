class Router:
  def __init__(self):
    self.__routes = {}

  def get(self, path: str):
    def decorator(func):
      self.__routes[(path, "GET")] = func
      return func
    return decorator

  def post(self, path: str):
    def decorator(func):
      self.__routes[(path, "POST")] = func
      return func
    return decorator

  def put(self, path: str):
    def decorator(func):
      self.__routes[(path, "PUT")] = func
      return func
    return decorator

  def delete(self, path: str):
    def decorator(func):
      self.__routes[(path, "DELETE")] = func
      return func
    return decorator
  
  def find_handler(self, method, path):
      print(f'method: {method}, path: {path}')
      return self.__routes.get((path, method), None)
  
  # def handleRequest(self, request: Request):
  #   path = request.path
  #   method = request.method
  #   route = self.__routes.get(path)
    
  #   if route and route['method'] == method:
  #     return route['handler'](request)
  #   return Response(404, { 'error':'Route not found.'})
  
  @property
  def routes(self):
      return self.__routes.copy()