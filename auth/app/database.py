import os
import mysql.connector
from mysql.connector import Error
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            # localhost when app is running locally
            host=os.getenv('DB_HOST', 'auth-db'), # auth-db for when it's dockerized
            user=os.getenv('DB_USER', 'auth_user'),
            password=os.getenv('DB_PASSWORD', 'auth_password'),
            database=os.getenv('DB_NAME', 'auth_db')
        )
        return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL Database: {e}")
        return None

def get_user_by_email(email):
    connection = get_db_connection()
    if connection is None:
        return None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        return user
    except Error as e:
        logger.error(f"Error querying database: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_user_password(email, hashed_password):
    connection = get_db_connection()
    if connection is None:
        return False

    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE email = %s",
            (hashed_password, email)
        )
        connection.commit()
        return cursor.rowcount > 0
    except Error as e:
        logger.error(f"Error updating user password: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
