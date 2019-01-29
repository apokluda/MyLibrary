from peewee import SqliteDatabase

# AP 2019-01-29: Do we need to explicitly open/close the database connection for
# every request? So far I have not found a clear answer or recommended pattern.
# For example, see https://github.com/falconry/falcon/issues/639

db = SqliteDatabase(':memory:', pragmas={'foreign_keys': 1})
