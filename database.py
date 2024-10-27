import mysql.connector

def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Mặc định MySQL trên XAMPP không có mật khẩu
            database="TicketSystem"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Lỗi kết nối: {err}")
        return None
