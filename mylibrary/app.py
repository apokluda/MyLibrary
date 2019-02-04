import falcon
from falcon_auth import FalconAuthMiddleware, BasicAuthBackend
import mylibrary.api.user
import mylibrary.api.book
import mylibrary.model.auth
from .routes import routes

# Setup following falcon-auth usage example:
user_loader = mylibrary.model.auth.authenticate
auth_backend = BasicAuthBackend(user_loader)
auth_middleware = FalconAuthMiddleware(auth_backend)

# gunicorn expects the WSGI application to be called 'application' by default
application = falcon.API(middleware=[auth_middleware])

# In almost every real world application, APIs will necessarily evolve over time.
# The current version of the API is called v1 and included in the routes below.
# Alternatively, we could allow the version to be specified in a custom
# request or accept header but this would introduce more complexity since we
# would have to write custom routing code for falcon.

application.add_route(routes['users'], mylibrary.api.user.Users())
application.add_route(routes['user'], mylibrary.api.user.User())
application.add_route(routes['books'], mylibrary.api.book.Books())
application.add_route(routes['book'], mylibrary.api.book.Book())
