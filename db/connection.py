import pymysql

def get_connection():
    try:
        connection = pymysql.connect(
            host='10.245.230.93',
            user='user',
            password='password',
            db='CALL_CENTER_NATURA',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error de conexión: {e}")
        return None



