import falcon
import mylibrary.api.user

# gunicorn expects the WSGI application to be called 'application' by default
application = falcon.API()

user = mylibrary.api.user.UserAPI()
application.add_route('/user', user)
