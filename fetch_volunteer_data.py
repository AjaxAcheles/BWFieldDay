import sqlite3
import json

DATABASE = "volunteers.db"

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row  # So we can use column names
    return connection

# ––– Database Table Creation –––

def create_events_table():
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            event_name TEXT,
            role_ids TEXT
        )
    """)
    connection.commit()
    connection.close()

def create_roles_table():
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            role_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            role_name TEXT,
            event_id INTEGER,
            position_ids TEXT,
            FOREIGN KEY(event_id) REFERENCES events(event_id)
        )
    """)
    connection.commit()
    connection.close()

def create_positions_table():
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            position_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            position_holder_name TEXT,
            role_id INTEGER,
            parent_id INTEGER,
            FOREIGN KEY(role_id) REFERENCES roles(role_id)
        )
    """)
    connection.commit()
    connection.close()

# ––– Helper Functions –––

def list_to_json(lst):
    return json.dumps(lst)

def json_to_list(json_str):
    if json_str:
        return json.loads(json_str)
    return []

# ––– Event Functions –––

def add_event(event_name):
    connection = get_db()
    cursor = connection.cursor()
    # Initially, no roles are attached: we store an empty JSON list.
    cursor.execute("INSERT INTO events (event_name, role_ids) VALUES (?, ?)", (event_name, list_to_json([])))
    connection.commit()
    event_id = cursor.lastrowid
    connection.close()
    return event_id

def update_event(event_id, event_name):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("UPDATE events SET event_name = ? WHERE event_id = ?", (event_name, event_id))
    connection.commit()
    connection.close()

def delete_event(event_id):
    connection = get_db()
    cursor = connection.cursor()
    # First, remove any roles (and their positions) linked to this event.
    cursor.execute("SELECT role_ids FROM events WHERE event_id = ?", (event_id,))
    row = cursor.fetchone()
    if row:
        role_ids = json_to_list(row["role_ids"])
        for role_id in role_ids:
            delete_role(role_id)
    cursor.execute("DELETE FROM events WHERE event_id = ?", (event_id,))
    connection.commit()
    connection.close()

def update_event_role_ids(event_id, role_ids):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("UPDATE events SET role_ids = ? WHERE event_id = ?", (list_to_json(role_ids), event_id))
    connection.commit()
    connection.close()

def get_max_event_id():
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(event_id) AS max_id FROM events")
    max_id = cursor.fetchone()[0]
    connection.close()
    if max_id is None:
        return 0
    else:
        return max_id

# ––– Role Functions –––

def add_role(event_id, role_name):
    connection = get_db()
    cursor = connection.cursor()
    # Create the role with no positions yet.
    cursor.execute("INSERT INTO roles (role_name, event_id, position_ids) VALUES (?, ?, ?)",
                   (role_name, event_id, list_to_json([])))
    connection.commit()
    role_id = cursor.lastrowid
    connection.close()
    try:
        # Add the new role_id to the corresponding event’s list.
        event = get_event(event_id)
        role_ids = json_to_list(event["role_ids"])
        role_ids.append(role_id)
        update_event_role_ids(event_id, role_ids)
    except:
        pass
    return role_id

def update_role(role_id, role_name):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("UPDATE roles SET role_name = ? WHERE role_id = ?", (role_name, role_id))
    connection.commit()
    connection.close()

def delete_role(role_id):
    connection = get_db()
    cursor = connection.cursor()
    # Remove any positions attached to this role.
    cursor.execute("SELECT event_id, position_ids FROM roles WHERE role_id = ?", (role_id,))
    row = cursor.fetchone()
    if row:
        event_id = row["event_id"]
        position_ids = json_to_list(row["position_ids"])
        for pos_id in position_ids:
            delete_position(pos_id)
        # Remove this role from the event’s role_ids list.
        event = get_event(event_id)
        role_ids = json_to_list(event["role_ids"])
        if role_id in role_ids:
            role_ids.remove(role_id)
            update_event_role_ids(event_id, role_ids)
    cursor.execute("DELETE FROM roles WHERE role_id = ?", (role_id,))
    connection.commit()
    connection.close()

def update_role_position_ids(role_id, position_ids):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("UPDATE roles SET position_ids = ? WHERE role_id = ?", (list_to_json(position_ids), role_id))
    connection.commit()
    connection.close()

def get_event(event_id):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
    event = cursor.fetchone()
    connection.close()
    return event

def get_role(role_id):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM roles WHERE role_id = ?", (role_id,))
    role = cursor.fetchone()
    connection.close()
    return role

def get_max_role_id():
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(role_id) AS max_id FROM roles")
    max_id = cursor.fetchone()[0]
    connection.close()
    if max_id is None:
        return 0
    else:
        return max_id

# ––– Position Functions ––– 

def add_position(role_id, position_holder_name, parent_id):
    connection = get_db()
    cursor = connection.cursor()
    # New position: no volunteer has claimed it yet.
    cursor.execute("INSERT INTO positions (position_holder_name, role_id, parent_id) VALUES (?, ?, ?)",
                   (position_holder_name, role_id, parent_id))
    connection.commit()
    position_id = cursor.lastrowid
    connection.close()
    try:
        # Update the role to include this new position.
        role = get_role(role_id)
        position_ids = json_to_list(role["position_ids"])
        position_ids.append(position_id)
        update_role_position_ids(role_id, position_ids)
    except:
        pass
    return position_id

def update_position(position_id, position_holder_name, parent_id):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("UPDATE positions SET position_holder_name = ?, parent_id = ? WHERE position_id = ?", (position_holder_name, parent_id, position_id))
    connection.commit()
    connection.close()

def toggle_position_with_volunteer_data(role_id, position_holder_name, parent_id):
    connection = get_db()
    cursor = connection.cursor()
    # check to see if user has a position already
    filled_position = cursor.execute("SELECT position_id FROM positions WHERE role_id = ? AND position_holder_name = ? AND parent_id = ?", (role_id, position_holder_name, parent_id)).fetchone()
    if filled_position:
        # if exists, empty the position
        position_id = filled_position['position_id']
        cursor.execute("UPDATE positions SET position_holder_name = NULL, parent_id = NULL WHERE position_id = ?", (position_id,))
    else:  
        # if position doesn't exist  
        empty_position = cursor.execute("SELECT position_id FROM positions WHERE role_id = ? AND parent_id IS NULL", (role_id,)).fetchone()
        if empty_position:
            position_id = empty_position['position_id']
            cursor.execute("UPDATE positions SET position_holder_name = ?, parent_id = ? WHERE position_id = ?", (position_holder_name, parent_id, position_id))
    connection.commit()
    connection.close()
    

def delete_position(position_id):
    connection = get_db()
    cursor = connection.cursor()
    # Find the role for this position.
    cursor.execute("SELECT role_id FROM positions WHERE position_id = ?", (position_id,))
    row = cursor.fetchone()
    if row:
        role_id = row["role_id"]
        role = get_role(role_id)
        position_ids = json_to_list(role["position_ids"])
        if position_id in position_ids:
            position_ids.remove(position_id)
            update_role_position_ids(role_id, position_ids)
    cursor.execute("DELETE FROM positions WHERE position_id = ?", (position_id,))
    connection.commit()
    connection.close()

def delete_position_with_volunteer_data(role_id, position_holder_name, parent_id):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM positions WHERE role_id = ? AND position_holder_name = ? AND parent_id = ?", (role_id, position_holder_name, parent_id))
    connection.commit()
    connection.close()
    

def update_position_volunteer(position_id, volunteer_name):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("UPDATE positions SET position_holder_name = ? WHERE position_id = ?", (volunteer_name, position_id))
    connection.commit()
    connection.close()

def get_position(position_id):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM positions WHERE position_id = ?", (position_id,))
    position = cursor.fetchone()
    connection.close()
    return position

def get_positions_by_parent_id(parent_id):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM positions WHERE parent_id = ?", (parent_id,))
    positions = cursor.fetchall()
    connection.close()
    return positions

def get_max_position_id():
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(position_id) AS max_id FROM positions")
    max_id = cursor.fetchone()[0]
    connection.close()
    if max_id is None:
        return 0
    else:
        return max_id


# ––– Retrieval: Nested Data for Templates –––

def get_all_events_nested():
    """
    Returns a list of events where each event is a dictionary
    with a key "roles" that is a list of role dictionaries, each of which
    has a key "positions" that is a list of position dictionaries.
    """
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    events_list = []
    for event in events:
        event_dict = dict(event)
        # Get all roles attached to this event.
        cursor.execute("SELECT * FROM roles WHERE event_id = ?", (event['event_id'],))
        roles = cursor.fetchall()
        roles_list = []
        for role in roles:
            role_dict = dict(role)
            # Get all positions for this role.
            cursor.execute("SELECT * FROM positions WHERE role_id = ?", (role['role_id'],))
            positions = cursor.fetchall()
            role_dict["positions"] = [dict(pos) for pos in positions]
            roles_list.append(role_dict)
        event_dict["roles"] = roles_list
        events_list.append(event_dict)
    connection.close()
    return events_list


def reset_all_volunteer_databases():
    connection = get_db()
    sql = connection.cursor()

    # get all tables in database.
    sql.execute("DROP TABLE IF EXISTS events")
    sql.execute("DROP TABLE IF EXISTS roles")
    sql.execute("DROP TABLE IF EXISTS positions")
    connection.commit()
    create_events_table()
    create_roles_table()
    create_positions_table()
    
def get_all_tables():
    connection = get_db()
    sql = connection.cursor()
    database_dict = {}
    tables = sql.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall() 
    tables = [table[0] for table in tables]
    for table in tables:
        rows = sql.execute("SELECT * FROM " + table).fetchall()
        database_dict[table] = rows
    return database_dict