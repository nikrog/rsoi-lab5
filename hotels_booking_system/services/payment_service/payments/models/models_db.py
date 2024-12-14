import os
from peewee import Model, PostgresqlDatabase

postgres_db = PostgresqlDatabase(
    os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT'))
)


class BaseModel(Model):
    class Meta:
        database = postgres_db
