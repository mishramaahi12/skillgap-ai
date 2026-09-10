import psycopg2


def get_connection():
    connection = psycopg2.connect(
        host="localhost",
        port=5432,
        database="skillgap",
        user="skillgap_user",
        password="skillgap_password"
    )

    return connection