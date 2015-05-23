from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from accounting.resources import app as accounting
from client.application import app as client

application = DispatcherMiddleware(accounting, {
    '/client': client
})
if __name__ == '__main__':
    run_simple('localhost', 5000, application,
               use_reloader=True, use_debugger=True, use_evalex=True)