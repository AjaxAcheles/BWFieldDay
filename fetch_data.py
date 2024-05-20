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
                    number_of_children INTEGER, 
                    parent_2_name TEXT,
                    parent_2_t_shirt_size TEXT
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



#parent name, parent email, parent phone number, number of children, parent t-shirt size if any
#for each child, (child name, child age, child t-shirt size if t-shirt)
#if parent not live and homeschool in brunswick county, then parent can not sign up