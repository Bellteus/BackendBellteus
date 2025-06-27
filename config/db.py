#Conectar a base de datos y realizar consultas
import pymysql

def connect_to_db():
    """Connect to the MySQL database."""
    try:
        connection = pymysql.connect(
            host='10.245.230.93',
            user='user',
            password='password',
            db='CALL_CENTER_NATURA'
        )
        print("Connection to the database was successful.")
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to the database: {e}")
        return None