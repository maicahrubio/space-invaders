import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='space_invaders_db',
            user='root',
            password=''
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    return None

# 1. CREATE: Register a new user with a password
def register_user(username, password):
    connection = get_db_connection()
    if not connection:
        return False, "Database connection failed."

    cursor = connection.cursor()
    try:
        # Check if username already exists
        cursor.execute("SELECT id FROM players WHERE username = %s", (username,))
        if cursor.fetchone():
            return False, "Username already taken!"

        # Insert new user
        cursor.execute("INSERT INTO players (username, password, selected_ship) VALUES (%s, %s, %s)", (username, password, 'default'))
        connection.commit()
        return True, "Registration successful!"

    except Error as e:
        print(f"Database error: {e}")
        return False, str(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 2. READ: Verify login credentials
def verify_user(username, password):
    connection = get_db_connection()
    if not connection:
        return False, "Database connection failed."

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM players WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            return True, user
        else:
            return False, "Invalid username or password."
    except Error as e:
        print(f"Login error: {e}")
        return False, str(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 3. CREATE/SAVE: Register player score (for gameplay)
def register_player_and_score(username, score):
    connection = get_db_connection()
    if not connection:
        return

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id FROM players WHERE username = %s", (username,))
        result = cursor.fetchone()
        
        if result:
            player_id = result[0]
        else:
            cursor.execute("INSERT INTO players (username) VALUES (%s)", (username,))
            connection.commit()
            player_id = cursor.lastrowid

        cursor.execute("INSERT INTO scores (player_id, score) VALUES (%s, %s)", (player_id, score))
        connection.commit()
        print(f"Successfully saved score {score} for {username}!")

    except Error as e:
        print(f"Database error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 4. READ: Load Leaderboard (Shows each unique player's highest score)
def get_leaderboard(limit=10):
    connection = get_db_connection()
    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)
    try:
        query = """
            SELECT players.username, MAX(scores.score) as score, MAX(scores.achieved_at) as achieved_at 
            FROM scores 
            JOIN players ON scores.player_id = players.id 
            GROUP BY players.id, players.username
            ORDER BY score DESC 
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching leaderboard: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 5. UPDATE: Update player profile username
def update_player_username(old_username, new_username):
    connection = get_db_connection()
    if not connection:
        return False

    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE players SET username = %s WHERE username = %s", (new_username, old_username))
        connection.commit()
        if cursor.rowcount > 0:
            print(f"Updated username from {old_username} to {new_username}!")
            return True
        else:
            print("Player not found.")
            return False
    except Error as e:
        print(f"Error updating player: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()  

# 6. UPDATE: Update player's selected spaceship
def update_player_ship(username, ship_name):
    connection = get_db_connection()
    if not connection:
        return False

    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE players SET selected_ship = %s WHERE username = %s", (ship_name, username))
        connection.commit()
        return True
    except Error as e:
        print(f"Error updating ship: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()