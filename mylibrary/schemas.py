username = {
    "description": "Desired username",
    "type": "string",
    "minLength": 1,
    "pattern": "^[^\\d\\s]"
}

password = {
    "description": "Your chosen password",
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
                    "username": username,
                    "join_date": date_time,
                    "href": link,
                    "books": { "type": "array", "items": link}
                }
            },
            "required": ["username", "join_date", "href"]
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
        "author": {"type": "string"},
        "date_added": date_time,
        "href": link,
        "owner": link,
        "title": {"type": "string"}
    }
}

get_book = {
    "type": "object",
    "properties": {
        "href": link,
        "items": {
            "type": "array",
            "items": book
        }
    }
}
