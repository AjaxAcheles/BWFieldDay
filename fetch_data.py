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


def create_admin_info_table(current_admin_info=None):
    connection = get_db()
    sql = connection.cursor()
    sql.execute("""
                create table if not EXISTS admin_info (
                    key TEXT,
                    value BLOB
                )
                """)
    connection.commit()
    if sql.execute("SELECT * FROM admin_info").fetchall() == []:
        insert_into_event_table("events", {"Empty Event": {"Empty Position": 1}})
        insert_into_event_table("t_shirt_sizes", ["Youth S", "Youth M", "Youth L", "Youth XL", "XS", "S", "M", "L", "XL", "XXL", "XXXL"])
        if current_admin_info is None:
            insert_into_event_table("admin", {"email": "imargo4507@outlook.com", "password": "imargo4507"})
            insert_into_event_table("admin", {"email": "huiwon1280@hotmail.com", "password": "huiwon1280"})
        else:
            insert_into_event_table("admin", {"email": current_admin_info[0], "password": current_admin_info[1]})


def create_volunteers_info_table():
    connection = get_db()
    sql = connection.cursor()
    sql.execute("""
                create table if not EXISTS volunteers_info (
                    event_position_name TEXT PRIMARY KEY,
                    volunteer_name TEXT,
                    volunteer_parent_id INTEGER
                )
                """)
    connection.commit()


def get_parent_info_with_parent_id(parent_id):
    connection = get_db()
    sql = connection.cursor()
    parent_info = sql.execute("SELECT * FROM parent_info WHERE parent_id = ?", (parent_id,)).fetchall()
    parent_info_list = []
    for row in parent_info:
        parent_info_list.append(dict(zip([column[0] for column in sql.description], row)))
    if str(parent_info_list[0]["is_parent_1_volunteering"]) == "1":
        parent_info_list[0]["is_parent_1_volunteering"] = True
    else:
        parent_info_list[0]["is_parent_1_volunteering"] = False

    if str(parent_info_list[0]["is_parent_2_volunteering"]) == "1":
        parent_info_list[0]["is_parent_2_volunteering"] = True
    else:
        parent_info_list[0]["is_parent_2_volunteering"] = False
    return parent_info_list[0]

def get_email_with_parent_id(parent_id):
    connection = get_db()
    sql = connection.cursor()
    email = sql.execute("SELECT parent_email FROM parent_info WHERE parent_id = ?", (parent_id,)).fetchone()
    if email:
        return email[0]
    else:
        return None
    
def get_parent_t_shirts():
    connection = get_db()
    sql = connection.cursor()
    t_shirts = sql.execute("SELECT parent_1_t_shirt_size, parent_2_t_shirt_size FROM parent_info").fetchall()
    return t_shirts

def get_child_t_shirts():
    connection = get_db()
    sql = connection.cursor()
    t_shirts = sql.execute("SELECT child_t_shirt_size FROM child_info").fetchall()
    return t_shirts


def get_child_info():
    connection = get_db()
    sql = connection.cursor()
    return sql.execute("SELECT * FROM child_info").fetchall()

def get_volunteers_info():
    connection = get_db()
    sql = connection.cursor()
    return sql.execute("SELECT * FROM volunteers_info").fetchall()

def get_children_info_with_parent_id(parent_id):
    connection = get_db()
    sql = connection.cursor()
    children_info = sql.execute("SELECT * FROM child_info WHERE parent_id = ?", (parent_id,)).fetchall()
    children_info_dict = []
    for child in children_info:
        child_dict = dict(zip([column[0] for column in sql.description], child))
        children_info_dict.append(child_dict)
    return children_info_dict

def get_value_from_admin_info(key):
    connection = get_db()
    sql = connection.cursor()
    value = sql.execute("SELECT value FROM admin_info WHERE key = ?", (key,)).fetchone()
    return value

def get_events_from_admin_info():
    connection = get_db()
    sql = connection.cursor()
    events_tuple = sql.execute("SELECT value FROM admin_info WHERE key = ?", ("events",)).fetchone()
    events = json.loads(events_tuple[0])
    return events

def update_events_in_admin_info(events):
    connection = get_db()
    sql = connection.cursor()
    sql.execute("UPDATE admin_info SET value = ? WHERE key = ?", (json.dumps(events), "events"))
    connection.commit()


def add_valid_admin(email, password):
    connection = get_db()
    sql = connection.cursor()
    sql.execute("INSERT INTO admin_info (key, value) VALUES (?, ?)", ("admin", json.dumps({"email": email, "password": password})))
    connection.commit()


def is_valid_admin(email, password):
    email = email.lower().strip()
    password = password.strip()
    connection = get_db()
    sql = connection.cursor()
    admin_info = sql.execute("SELECT * FROM admin_info WHERE key = ?", ("admin",)).fetchall()
    for admin in admin_info:
        credentials_dict = json.loads(admin[1])
        admin_email = credentials_dict["email"]
        admin_password = credentials_dict["password"]
        if admin_email == email and admin_password == password:
            return True
    return False


def is_admin(email):
    email = email.lower().strip()
    connection = get_db()
    sql = connection.cursor()
    admin_info = sql.execute("SELECT * FROM admin_info WHERE key = ?", ("admin",)).fetchall()
    for admin in admin_info:
        credentials_dict = json.loads(admin[1])
        admin_email = credentials_dict["email"]
        if admin_email == email:
            return True
    return False


def remove_admin(email, password):
    connection = get_db()
    sql = connection.cursor()
    sql.execute("DELETE FROM admin_info WHERE key = 'admin' AND value = ?", (json.dumps({"email": email, "password": password}),))
    connection.commit()


def remove_admin_blind(email):
    connection = get_db()
    sql = connection.cursor()
    # delete account without knowing the password.
    sql.execute("DELETE FROM admin_info WHERE key = 'admin' AND value LIKE ?", ('%' + email + '%',))
    connection.commit()


def get_t_shirt_sizes_from_admin_info():
    connection = get_db()
    sql = connection.cursor()
    t_shirt_sizes_tuple = sql.execute("SELECT value FROM admin_info WHERE key = ?", ("t_shirt_sizes",)).fetchone()
    t_shirt_sizes_string = t_shirt_sizes_tuple[0][1:-1]
    t_shirt_sizes_ugly_list = t_shirt_sizes_string.replace('"', "").replace("'", "").split(',')
    t_shirt_sizes = [size.strip() for size in t_shirt_sizes_ugly_list]
    return t_shirt_sizes

def insert_into_event_table(key, value):
    connection = get_db()
    sql = connection.cursor()
    sql.execute("INSERT INTO admin_info (key, value) VALUES (?, ?)", (key, json.dumps(value)))
    connection.commit()


def insert_parent_info(parent_1_name, parent_email, parent_phone_number, parent_1_t_shirt_size, is_parent_1_volunteering, parent_2_name, parent_2_t_shirt_size, is_parent_2_volunteering, number_of_children):
    connection = get_db()
    sql = connection.cursor()
    sql.execute("""INSERT INTO parent_info (parent_1_name, parent_email, parent_phone_number, parent_1_t_shirt_size, is_parent_1_volunteering, parent_2_name, parent_2_t_shirt_size, is_parent_2_volunteering, number_of_children)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                (parent_1_name, parent_email, parent_phone_number, parent_1_t_shirt_size, is_parent_1_volunteering, parent_2_name, parent_2_t_shirt_size, is_parent_2_volunteering, number_of_children)
                )
    connection.commit()

def edit_parent_info(parent_id, parent_1_name, parent_email, parent_phone_number, parent_1_t_shirt_size, is_parent_1_volunteering, parent_2_name, parent_2_t_shirt_size, is_parent_2_volunteering, number_of_children):
    connection = get_db()
    sql = connection.cursor()
    if parent_2_name is None and parent_2_t_shirt_size is None and is_parent_2_volunteering is None:
        sql.execute("""UPDATE parent_info SET parent_1_name = ?, parent_email = ?, parent_phone_number = ?, parent_1_t_shirt_size = ?, is_parent_1_volunteering = ?, parent_2_name = ?, parent_2_t_shirt_size = ?, is_parent_2_volunteering = ?, number_of_children = ? WHERE parent_id = ?""", 
                    (parent_1_name, parent_email, parent_phone_number, parent_1_t_shirt_size, is_parent_1_volunteering, None, None, None, number_of_children, parent_id)
                    )
    else:
        sql.execute("""UPDATE parent_info SET parent_1_name = ?, parent_email = ?, parent_phone_number = ?, parent_1_t_shirt_size = ?, is_parent_1_volunteering = ?, parent_2_name = ?, parent_2_t_shirt_size = ?, is_parent_2_volunteering = ?, number_of_children = ? WHERE parent_id = ?""", 
                    (parent_1_name, parent_email, parent_phone_number, parent_1_t_shirt_size, is_parent_1_volunteering, parent_2_name, parent_2_t_shirt_size, is_parent_2_volunteering, number_of_children, parent_id)
                    )
    connection.commit()


def insert_child_info(child_name, child_age, child_t_shirt_size, parent_id):
    connection = get_db()
    sql = connection.cursor()
    sql.execute("""INSERT INTO child_info (child_name, child_age, child_t_shirt_size, parent_id)
                VALUES (?, ?, ?, ?)""", 
                (child_name, child_age, child_t_shirt_size, parent_id)
                )
    connection.commit()
    child_id = sql.lastrowid
    return child_id


def manage_volunteer_info(event_position_name, volunteer_name, volunteer_parent_id):
    connection = get_db()
    sql = connection.cursor()
    # check if volunteer already exists. if so then delete position that the volunteer is currently holding then continue the func
    is_volunteer_exists = sql.execute("SELECT * FROM volunteers_info WHERE volunteer_name = ? AND volunteer_parent_id = ?", (volunteer_name, volunteer_parent_id)).fetchall()
    if is_volunteer_exists:
        sql.execute("DELETE FROM volunteers_info WHERE volunteer_name = ? AND volunteer_parent_id = ?", (volunteer_name, volunteer_parent_id))
        connection.commit()
    
    # manage info 
    try:
        sql.execute("""INSERT INTO volunteers_info (event_position_name, volunteer_name, volunteer_parent_id)
                VALUES (?, ?, ?)""", 
                (event_position_name, volunteer_name, volunteer_parent_id)
                )
    except:
        sql.execute("""UPDATE volunteers_info SET volunteer_name = ?, volunteer_parent_id = ? WHERE event_position_name = ?""", 
                (event_position_name, volunteer_name, volunteer_parent_id)
                )
    connection.commit()


def get_occupied_positions():
    connection = get_db()
    sql = connection.cursor()
    occupied_positions = sql.execute("SELECT event_position_name, volunteer_name FROM volunteers_info").fetchall()
    occupied_positions_dict = {}
    for event_position in occupied_positions:
        event_position_name = event_position[0].replace("_", "-")
        volunteer_name = event_position[1]
        occupied_positions_dict[event_position_name] = volunteer_name
    return occupied_positions_dict


def edit_child_info(child_id, child_name, child_age, child_t_shirt_size):
    connection = get_db()
    sql = connection.cursor()
    sql.execute("""
                UPDATE child_info SET child_name = ?, child_age = ?, child_t_shirt_size = ? WHERE child_id = ?""", 
                (child_name, child_age, child_t_shirt_size, child_id)
                )
    connection.commit()


def get_parent_id_with_email(parent_email):
    connection = get_db()
    sql = connection.cursor()
    sql.execute("SELECT parent_id FROM parent_info WHERE parent_email = ?", (parent_email,))
    parent_id = sql.fetchone()
    if parent_id:
        return parent_id[0]
    else:
        return None


def get_phone_number_with_parent_id(parent_id):
    connection = get_db()
    sql = connection.cursor()
    phone_number = sql.execute("SELECT parent_phone_number FROM parent_info WHERE parent_id = ?", (parent_id,)).fetchone()
    if phone_number:
        return phone_number[0]
    else:
        return None

def get_admin_password_with_email(email):
    connection = get_db()
    sql = connection.cursor()
    accounts = sql.execute("SELECT * FROM admin_info WHERE key = 'admin'").fetchall()
    if accounts:
        for account in accounts:
            credentials_dict = json.loads(account[1])
            if credentials_dict["email"] == email:
                return credentials_dict["password"]
    else:
        return None



def get_parent_id_and_children_id_with_phone_number(parent_phone_number):
    connection = get_db()
    sql = connection.cursor()
    sql.execute("SELECT parent_id FROM parent_info WHERE parent_phone_number = ?", (parent_phone_number,))
    parent_id = sql.fetchone()
    if parent_id:
        parent_id = int(parent_id[0])
    else:
        return None
    children_info = sql.execute("SELECT child_name, child_id FROM child_info WHERE parent_id = ?", (parent_id,)).fetchall()
    children_info_dict = {}
    for child in children_info:
        # children_info_dict[child_name] = child_id
        children_info_dict[child[0]] = child[1]
    return {"parent_id": parent_id, "children_info_dict": children_info_dict}


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
        return volunteering_parents_list
    else:
        return None
    

def get_family(parent_id):
    connection = get_db()
    sql = connection.cursor()
    parents = sql.execute("SELECT * FROM parent_info WHERE parent_id = ?", (parent_id,)).fetchone()
    children = sql.execute("SELECT * FROM child_info WHERE parent_id = ?", (parent_id,)).fetchall()
    return {"parents": parents, "children": children}


def is_parent_exits(parent_phone_number):
    connection = get_db()
    sql = connection.cursor()
    sql.execute("SELECT parent_id FROM parent_info WHERE parent_phone_number = ?", (parent_phone_number,))
    parent_id = sql.fetchone()
    if parent_id:
        return True
    else:
        return False    


def get_all_tables():
    connection = get_db()
    sql = connection.cursor()
    database_dict = {}
    tables = sql.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall() 
    tables = [table[0] for table in tables]
    for table in tables:
        rows = sql.execute("SELECT * FROM " + table).fetchall()
        database_dict[table] = rows
    print(database_dict)
    return database_dict


def get_all_volunteering_parent_names():
    connection = get_db()
    sql = connection.cursor()
    parent_1_names = sql.execute("SELECT parent_1_name FROM parent_info WHERE is_parent_1_volunteering = 1").fetchall()
    parent_2_names = sql.execute("SELECT parent_2_name FROM parent_info WHERE is_parent_2_volunteering = 1").fetchall()
    parent_1_names = [name[0] for name in parent_1_names if name[0] is not None]
    parent_2_names = [name[0] for name in parent_2_names if name[0] is not None]
    all_volunteering_parent_names = parent_1_names + parent_2_names
    return all_volunteering_parent_names




def reset_all_databases(current_admin_info):
    connection = get_db()
    sql = connection.cursor()

    # get all tables in database.
    sql.execute("DROP TABLE IF EXISTS parent_info")
    sql.execute("DROP TABLE IF EXISTS child_info")
    sql.execute("DROP TABLE IF EXISTS volunteers_info")
    sql.execute("DROP TABLE IF EXISTS admin_info")
    connection.commit()
    create_parent_info_table()
    create_child_info_table()
    create_volunteers_info_table()
    create_admin_info_table(current_admin_info)
    connection.commit()

    