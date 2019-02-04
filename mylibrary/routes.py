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
