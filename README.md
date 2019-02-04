# MyLibrary
An exercise to a small service which offers a REST API which manages a set
of books. This implementation allows users to self register, and then store
details of books in their personal library. They can loan out their books
to other registered users, and borrow books from them. The service keeps
track of loans, including the owner of the book, to whom a book is loaned,
and the due date.

## Design Considerations

I recently implemented a simple REST API to retrieve diagnostic information
from a C++ service using the mongoose embeded web server. I've used mongoose
for a few projects in the past; however, I chose to write this implementation
in Python since I belive that it is better suited for this project.
This was my first time using the Falcon web framework and peewee
object-relational mapping tool (ORM) which are used to interact with clients
over HTTP and a SQL database respectively.

Since this is just an exercise, peewee is confiured to use an in-memory
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
using OpenAPI; however, for this exersise the endpoints are documented
with commensd and in the following sections.

Well written software must be designed to evolve over time, thus it is
a good practice to version public APIs. The endpoints above contain the API version number, currently set to `v1.` In this implementation, the API
version has been included as part of the entpoint name for simplicity.
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
Foreign keys are used to map *users* to books (as owners), and *loans* to
books, owners and borrowers. This approach minimizes duplication of information
in the database making it easier to maintain.

## Setup

Dependencies:
- falcon
- peewee
- pytest
- falcon-auth
