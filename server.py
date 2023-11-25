from waitress import serve
from file_transfer.wsgi import application

if __name__ == '__main__':
    serve(application, port='8000')
    