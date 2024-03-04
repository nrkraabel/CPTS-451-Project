
import psycopg2

def connect_db():
    return psycopg2.connect(
        dbname="milestone1db",
        user="postgres",  # my local username
        password="8991",  #my local password
        host="localhost"
    )

def executeQuery(self, sql_str):
    try:
        conn=connect_db()
    except:
        print('Unable to connect')
    cur = conn.cursor()
    cur.execute(sql_str)
    conn.commit()
    result = cur.fetchall()
    conn.close()
    return result

def list_states():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT state FROM business ORDER BY state;")
            states = cur.fetchall()
            return states

def list_cities(state):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT city FROM business WHERE state=%s ORDER BY city;", (state,))
            cities = cur.fetchall()
            return cities

def list_businesses_state_city(city, state):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name, city, state FROM business WHERE city=%s AND state=%s ORDER BY name;", (city, state))
            businesses = cur.fetchall()
            return businesses
        
def list_businesses_state(state):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name, city, state FROM business WHERE state=%s ORDER BY name;", (state,))
            businesses = cur.fetchall()
            return businesses