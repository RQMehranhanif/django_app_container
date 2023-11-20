import json
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error

def load_database_settings():
    # Load database settings from the JSON file (if it exists)
    settings_filename = 'record_files/database_settings.json'
    try:
        with open(settings_filename, 'r') as settings_file:
            database_settings = json.load(settings_file)
            return database_settings

    except FileNotFoundError:
        return False

def db_connection( db_type, Test = False ):

    database_settings = load_database_settings()
    if not database_settings or not database_settings[db_type].get("hostname", ""):
        return False
    
    db_config = {
        "host": database_settings[db_type].get("hostname", ""),
        "user": database_settings[db_type].get("username", ""),
        "password": database_settings[db_type].get("password", ""),
        "database": database_settings[db_type].get("database", ""),
        "port": database_settings[db_type].get("port", "")
    }

    
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Connected to MySQL database")
            if Test:
                messagebox.showinfo("Test Connection", "Connected to MySQL database.")
            else:
                return connection
    except Error as e:
        if e.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist. You may need to create it.")
            messagebox.showerror("Error", "Database does not exist. You may need to create it.")
        elif e.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied. Check your username and password.")
            messagebox.showerror("Error", "Access denied. Check your username and password.")
        else:
            print(f"Error: {e}")
            messagebox.showerror("Error", e)
            exit()
    
    return None
