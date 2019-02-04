# MyLibrary
An exercise to a small service which offers a REST API which manages a set
of books. This implementation allows users to self register, and then store
details of books in their personal library. They can loan out their books
to other registered users, and borrow books from them. The service keeps
track of loans, including the owner of the book, to whom a book is loaned,
and the due date.

## Design Considerations

I recently implemented a simple REST API to retrieve diagnostic information
from a C++ service using the mongoose embedded web server. I've used mongoose
for a few projects in the past; however, I chose to write this implementation
in Python since I believe that it is better suited for this project.
This was my first time using the Falcon web framework and peewee
object-relational mapping tool (ORM) which are used to interact with clients
over HTTP and a SQL database respectively.

Since this is just an exercise, peewee is configured to use an in-memory
SQLite database that is initialized each time the service starts. To create
a persistent database, a filename can be supplied to `SqliteDatabase()`
in `model/__init__.py`.

The list of the API endpoints supported is defined in `model/routes.py`:

    routes = {
        # GET:  Retrieves information for all users
        #       (schema: mylibrary.schema.get_user)
        # POST: Creates a new user
        #       (schema: mylibrary.schema.create_user)
        "users": "/v1/users",
        # GET:  Retrieves information for a specific user, including the books
        #       that they own
        #       (schema: mylibrary.schema.get_user)
        "user": "/v1/users/{username_or_id}",
        # GET:  Retrieves information for all books
        #       (schema: mylibrary.schema.get_book)
        # POST: Creates a new book owned by the authenticated user
        #       (schema: mylibrary.schema.create_book)
        "books": "/v1/books",
        # GET:   Retrieves information for a specific book
        #        (schema: mylibrary.schema.get_book)
        "book": "/v1/books/{id}",
        # GET:   Retrieves all current and past loans (for admin),
        #        or all loans for which the authenticated user is the owner or borrower
        #        (schema: mylibrary.schema.get_loan)
        # POST:  Creates a new loan; the book being lent must be owned by the
        #        authenticated user
        #        (schema: mylibrary.schema.create_loan)
        "loans": "/v1/loans",
    }

For a production API, it would be useful to document all REST API endpoints
using OpenAPI; however, for this exercise the endpoints are documented
with comments and in the following sections.

Well written software must be designed to evolve over time, thus it is
a good practice to version public APIs. The endpoints above contain the API version number, currently set to `v1.` In this implementation, the API
version has been included as part of the endpoint name for simplicity.
Alternatively, the version of API that the client wishes to use could be
passed as an accept header or custom request header.

The body of all `POST` and `GET` requests is JSON and is described in
`mylibrary/schemas.py`. All input is validating on the server, and
all output is validating in unit tests against the schemas using JSON Schema.
References to entities in the system are represented in output from the
server using hyperlinks for easy navigation.

Users and books are stored in the `user` and `book` tables respectively and
represented in Python by the `model.user.UserModel` and `model.book.BookModel`
classes. The `loan` table stores information about all current and past loans.
Foreign keys are used to map *users* to *books* (as owners), and *loans* to
*books*, *owners* and *borrowers*. This approach minimizes duplication of information
in the database making it easier to maintain.

## Setup

You should have received the source in an archive containing a virtualenv
directory called `venv`. Open a terminal and `cd` to the directory where
you extracted the archive. Then you can run the service using `gunicorn` from the
virtualenv:

    $ source venv/bin/activate
    $ gunicorn mylibrary.app

Now open a second terminal in order and activate the virtualenv again. You can
interact with the service using `httpie` from the virtualenv. To test that your
setup is working, try to get a list of all books:

    $ source venv/bin/activate
    $ http localhost:8000/v1/books

If everything is working correctly, you should see the output similar to the following:

    HTTP/1.1 401 Unauthorized
    Connection: close
    Date: Mon, 04 Feb 2019 05:38:23 GMT
    Server: gunicorn/19.9.0
    content-length: 76
    content-type: application/json; charset=UTF-8
    vary: Accept

    {
        "description": "Missing Authorization Header",
        "title": "401 Unauthorized"
    }

If that didn't work, you can try to recreate your virtualenv directory using
the provided setup script:

    $ ./setup.sh

## Usage

This implementation allows users to self register, and then store
details of books in their personal library. They can loan out their books
to other registered users, and borrow books from them. The service keeps
track of loans, including the owner of the book, to whom a book is loaned,
and the due date.

In the following steps, we will create users, add books, and track a loan.

### Creating a User

An administrator user with username `admin` and password `passw0rd` is
automatically created on startup. The `/v1/users` endpoint enables us
to create regular unprivileged users. Let's create a new user
with username 'bob' and password 'icecream':

    $ http localhost:8000/v1/users username=bob password=icecream

You should get a `HTTP 201 Created` status. Usernames must be unique. Running
the command a second time will give you a `HTTP 400 Bad Request` status
with an informative error message.

Creating a user is the only command that can be performed by unauthenticated
users. Go ahead and try to retrieve the list of registered users without
first authenticating:

    $ http localhost:8000/v1/users

You will receive a `HTTP 401 Unauthorized` status and message telling you
that the authorization header is missing. With `httpie`, you can add the
authorization header with the `-a` flag:

    $ http -a bob:icecream localhost:8000/v1/users

This time you should see the following:

    HTTP/1.1 200 OK
    Connection: close
    Date: Mon, 04 Feb 2019 05:51:44 GMT
    Server: gunicorn/19.9.0
    content-length: 289
    content-type: application/json; charset=UTF-8

    {
        "href": "http://localhost:8000/v1/users",
        "items": [
            {
                "href": "http://localhost:8000/v1/users/1",
                "id": 1,
                "join_date": "2019-02-04 05:34:57.887931",
                "username": "admin"
            },
            {
                "href": "http://localhost:8000/v1/users/2",
                "id": 2,
                "join_date": "2019-02-04 05:45:00.805275",
                "username": "bob"
            }
        ]
    }

Take a look at the unit tests in `tests/test_app.py` to see what else the
users endpoint can do.

### Adding a Book

Books can be added to the system using the `/v1/books` endpoint. It works
very similar to `/v1/users`. Books require a title and an author. Ownership
will be assigned to the authenticated user automatically:

    $ http -a bob:icecream localhost:8000/v1/books title="On Liberty" author="John Stuart Mill"

Like with the users endpoint, you should receive a `HTTP 201 Created` status.

The JSON Schema for the output of 'GET /v1/users' includes an optional "books"
array. When requesting details of an individual user, their list of books
is also returned:

    {
        "href": "http://localhost:8000/v1/users/bob",
        "items": [
            {
                "books": [
                    "http://localhost:8000/v1/books/1"
                ],
                "href": "http://localhost:8000/v1/users/2",
                "id": 2,
                "join_date": "2019-02-04 05:45:00.805275",
                "username": "bob"
            }
        ]
    }

Information about individual books can be retrieved the same way as information
about individual users. Try following the the link from the `books` array above:

    $ http -a bob:icecream localhost:8000/v1/books/1

You should see the book that we just created:

    {
        "href": "http://localhost:8000/v1/books/1",
        "items": [
            {
                "author": "John Stuart Mill",
                "date_added": "2019-02-04 05:58:15.691484",
                "href": "http://localhost:8000/v1/books/1",
                "id": 1,
                "owner": "http://localhost:8000/v1/users/2",
                "title": "On Liberty"
            }
        ]
    }

You can also retrieve information about all books the same way you do for
all users. Try it as an exercise!

Take a look at the unit tests in `tests/test_app.py` to see what else the
books endpoint can do.

### Creating a Loan

Suppose Bob loans his copy of "On Liberty" to admin. We can track that using
the `/v1/loans` endpoint. If you've been following along, "On Liberty" should
have and `id` of 1 as shown in the output above. The admin user will always
have an `id` of 1. `httpie`'s shorthand syntax doesn't allow
us to pass integers, so this time we will supply our JSON from a file. You
should already have a file called 'myloan' in the current directory containing
the following:

    {
        "book_id":1,
        "user_id":1,
        "date_due":"2019-02-14"
    }

Use this file to loan the book to admin:

    $ http -a bob:icecream localhost:8000/v1/loans < myloan

The admin user can list all loans in the system, but users can only see
information about loans if the are the owner or borrower of the book. Just
like users and books, information about loans can be retrieved by issuing
a `GET` request to `/v1/loans`.

Checks are done to ensure that users can't loan books to users that don't
exist and can't loan books that they do not own. You can see examples of
this in the unit tests. Take a look at `tests/test_app.py`.

## Future Work

There's lots that could be done with this simple service! Some of the next
things to implement would be checks so that users can't create a book for a
book that is already lent out, and the ability to check a book back in by
issuing a `PATCH` request to the loans endpoint with a returned date.

There are lots of opportunities for making it easier for the users to query
exactly the information that they need. For example, a query string could
be used to filter the list of all books to those that are "over due":

    # Future command; not implemented yet
    $ http -a bob:icecream localhost:8000/v1/books?status=overdue

## Conclusion

If you have any questions about my implementation, please feel free to contact
me at apokluda AT gmail.com.
