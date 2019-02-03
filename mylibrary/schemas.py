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

create_user_schema = {
    "type": "object",
    "properties": {
        "username": username,
        "password": password
    },
    "required": ["username", "password"]
}

get_user_schema = {
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
                }
            },
            "required": ["username", "join_date", "href"]
        },
    },
    "required": ["href", "items"]
}
