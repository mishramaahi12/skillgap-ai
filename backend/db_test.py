import psycopg2


connection = psycopg2.connect(
    host="localhost",
    port=5432,
    database="skillgap",
    user="skillgap_user",
    password="skillgap_password"
)


print("Database connected successfully!")


connection.close()