from server.router import Router
from server.response import Response
from server.server import Server



router = Router()

@router.get("/")
def home(request):
    return Response("Welcome to my API!")

@router.get("/hello")
def hello(request):
    return Response("Hello, World!")

server = Server(router)
server.listen(3000, 'The server is running.')
