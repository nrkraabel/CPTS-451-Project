
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
            cur.execute("SELECT businessname AS name, city, state FROM business WHERE city=%s AND state=%s ORDER BY name;", (city, state))
            businesses = cur.fetchall()
            return businesses
        
def list_businesses_state(state):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT businessname AS name, city, state FROM business AS b WHERE b.state=%s ORDER BY b.businessname;", (state,))
            businesses = cur.fetchall()
            return businesses

def list_category():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("select distinct c.categoryname from category c ")
            categories = cur.fetchall()
            return categories

def list_category_for_business(business_name):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(""" select distinct c.categoryname from business b 
                inner join businesscategory bc on bc.businessid = b.businessid 
                inner join category c on c.categoryid = bc.categoryid 
                where b.businessname = %s""", (business_name))
            categories = cur.fetchall()
            return categories

def getOverallMedianIncome():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("select PERCENTILE_CONT(0.5) within GROUP(order by medianIncome) from zipcodeData;")
            result = cur.fetchall()
            return result

"""
Gets businesses that have more than 5 reviews calling them overpriced, expensive, etc and that are in a low income zipcode
"""
def get_overpriced_businesses():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            select b.businessname AS name, b.state, b.city, count(r.reviewid) as bad_reviews from review r 
                inner join business b on b.businessid = r.businessid 
                inner join zipcodeData z on z.zipcode = b.zipcode 
                where z.medianincome < 46501.5 and r.reviewtext not like '%% cheap %%' and (r.reviewtext like '%% expensive%%' or r.reviewtext like '%% overpriced%%' or r.reviewtext like '%% waste of money%%')
                group by b.businessname, b.state, b.city
                having count(r.reviewid) > 5
            """)
            result = cur.fetchall()
            return result