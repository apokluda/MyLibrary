id = {
    "type": "integer",
    "minimum": 0
}

username = {
    "type": "string",
    "minLength": 1,
    "pattern": "^[^\\d\\s]"
}

password = {
    "type": "string",
    "minLength": 6,
}

link = {
    "type": "string",
    "format": "uri"
}

date_time = {
    "type": "string",
    "format": "date-time"
}

create_user = {
    "type": "object",
    "properties": {
        "username": username,
        "password": password
    },
    "required": ["username", "password"]
}

get_user = {
    "type": "object",
    "properties" : {
        "href": link,
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": id,
                    "username": username,
                    "join_date": date_time,
                    "href": link,
                    "books": { "type": "array", "items": link}
                },
                "required": ["id", "username", "join_date", "href"]
            },
        },
    },
    "required": ["href", "items"]
}

create_book = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "author": {"type": "string"}
    },
    "required": ["title", "author"]
}

book = {
    "type": "object",
    "properties": {
        "id": id,
        "title": {"type": "string"},
        "author": {"type": "string"},
        "date_added": date_time,
        "href": link,
        "owner": link,
    },
    "required": ["id", "title", "author", "date_added", "href", "owner"]
}

get_book = {
    "type": "object",
    "properties": {
        "href": link,
        "items": {
            "type": "array",
            "items": book
        }
    },
    "required": ["href", "items"]
}

create_loan = {
    "type": "object",
    "properties": {
        "book_id": id,
        "user_id": id,
        "date_due": date_time
    },
    "required": ["book_id", "user_id", "date_due"]
}
