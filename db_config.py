import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="latha@1234",
        database="hospital_data"
    )
