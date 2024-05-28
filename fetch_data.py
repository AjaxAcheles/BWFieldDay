import sqlite3
from flask import *

def get_db():
    g.db = sqlite3.connect("database.db")
    return g.db

def create_parent_info_table():
    connection = get_db()
    sql = connection.cursor()
    sql.execute("""
                CREATE TABLE IF NOT EXISTS
                parent_info (
                    parent_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    parent_1_name TEXT, 
                    parent_email TEXT,
                    parent_phone_number INTEGER, 
                    parent_1_t_shirt_size TEXT,
                    is_parent_1_volunteering BOOLEAN,
                    parent_2_name TEXT,
                    parent_2_t_shirt_size TEXT,
                    is_parent_2_volunteering BOOLEAN,
                    number_of_children INTEGER
                )""")
    connection.commit()


def create_child_info_table():
    connection = get_db()
    sql = connection.cursor()
    sql.execute("""
                CREATE TABLE IF NOT EXISTS
                child_info (
                    child_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    child_name TEXT, 
                    child_age INTEGER, 
                    child_t_shirt_size TEXT,
                    parent_id INTEGER
                )""")
    connection.commit()


def get_parent_info():
    connection = get_db()
    sql = connection.cursor()
    return sql.execute("SELECT * FROM parent_info").fetchall()

def get_child_info():
    connection = get_db()
    sql = connection.cursor()
    return sql.execute("SELECT * FROM child_info").fetchall()

def insert_parent_info(parent_1_name, parent_email, parent_phone_number, parent_1_t_shirt_size, is_parent_1_volunteering, parent_2_name, parent_2_t_shirt_size, is_parent_2_volunteering, number_of_children):
    connection = get_db()
    sql = connection.cursor()
    sql.execute("""INSERT INTO parent_info (parent_1_name, parent_email, parent_phone_number, parent_1_t_shirt_size, is_parent_1_volunteering, parent_2_name, parent_2_t_shirt_size, is_parent_2_volunteering, number_of_children)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                (parent_1_name, parent_email, parent_phone_number, parent_1_t_shirt_size, is_parent_1_volunteering, parent_2_name, parent_2_t_shirt_size, is_parent_2_volunteering, number_of_children)
                )
    connection.commit()

def insert_child_info(child_dict, parent_id):
    connection = get_db()
    sql = connection.cursor()
    child_name = child_dict["name"]
    child_age = child_dict["age"]
    child_t_shirt_size = child_dict["t_shirt_size"]
    sql.execute("""INSERT INTO child_info (child_name, child_age, child_t_shirt_size, parent_id)
                VALUES (?, ?, ?, ?)""", 
                (child_name, child_age, child_t_shirt_size, parent_id)
                )
    connection.commit()

def get_parent_id_with_email(parent_email):
    connection = get_db()
    sql = connection.cursor()
    sql.execute("SELECT parent_id FROM parent_info WHERE parent_email = ?", (parent_email,))
    parent_id = sql.fetchone()
    if parent_id:
        return parent_id
    else:
        return None

def get_parent_id_with_phone_number(parent_phone_number):
    connection = get_db()
    sql = connection.cursor()
    sql.execute("SELECT parent_id FROM parent_info WHERE parent_phone_number = ?", (parent_phone_number,))
    parent_id = sql.fetchone()
    if parent_id:
        return int(parent_id[0])
    else:
        return None

def get_volunteering_parents_with_parent_id(parent_id):
    connection = get_db()
    sql = connection.cursor()
    parent_data = sql.execute("SELECT parent_1_name, is_parent_1_volunteering, parent_2_name, is_parent_2_volunteering FROM parent_info WHERE parent_id = ?", (parent_id,))
    parent_data = parent_data.fetchone() 
    if parent_data:
        volunteering_parents_list = [] 
        if str(parent_data[1]) == "1":
            volunteering_parents_list.append(parent_data[0])
        if str(parent_data[3]) == "1":
            volunteering_parents_list.append(parent_data[2])
        print(volunteering_parents_list)
        return volunteering_parents_list
    else:
        return None



