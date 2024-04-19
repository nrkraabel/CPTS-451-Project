
import psycopg2

def connect_db():
    return psycopg2.connect(
        dbname="yelpdb",
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
        
def list_zipcodes(city, state):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT zipcode FROM business WHERE city=%s AND state=%s ORDER BY zipcode;", (city, state))
            zipcodes = cur.fetchall()
            return zipcodes

def list_categories(zipcode):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT DISTINCT CategoryName FROM Category
                           JOIN BusinessCategory ON Category.CategoryID = BusinessCategory.CategoryID
                           JOIN Business ON Business.BusinessID = BusinessCategory.BusinessID
                           WHERE Zipcode = %s ORDER BY CategoryName;""", (zipcode,))
            categories = cur.fetchall()
            return categories

def list_businesses_state_city_zip(state, city, zipcode):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT BusinessName, Address, City, State, Zipcode 
                           FROM Business
                           WHERE State = %s AND City = %s AND Zipcode = %s
                           ORDER BY BusinessName;""", (state, city, zipcode))
            businesses = cur.fetchall()
            return businesses
        
# def list_businesses_filtered(state, city, zipcode, category):
#     with connect_db() as conn:
#         with conn.cursor() as cur:
#             cur.execute("""SELECT BusinessName, Address, City, State, Zipcode, CategoryName 
#                            FROM Business
#                            INNER JOIN BusinessCategory ON Business.BusinessID = BusinessCategory.BusinessID
#                            INNER JOIN Category ON BusinessCategory.CategoryID = Category.CategoryID
#                            WHERE State = %s AND City = %s AND Zipcode = %s AND CategoryName = %s
#                            ORDER BY BusinessName;""",
#                         (state, city, zipcode, category))
#             businesses = cur.fetchall()
#             return businesses
def list_businesses_filtered(state, city, zipcode, category):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT b.BusinessName AS name, b.Address AS address, b.City AS city, 
                       b.ReviewRating AS review_rating, b.ReviewCount AS review_count, 
                       ci.Count AS num_checkins, cat.CategoryName AS category_name
                FROM Business b
                INNER JOIN BusinessCategory bc ON b.BusinessID = bc.BusinessID
                INNER JOIN Category cat ON bc.CategoryID = cat.CategoryID
                INNER JOIN Review r ON b.BusinessID = r.BusinessID
                INNER JOIN CheckIn ci ON b.BusinessID = ci.BusinessID
                WHERE b.State = %s AND b.City = %s AND b.Zipcode = %s AND cat.CategoryName = %s
                ORDER BY b.BusinessName;
            """, (state, city, zipcode, category))
            return cur.fetchall()

def get_popular_businesses(zipcode):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                WITH CategoryAverageCheckIns AS (
                    SELECT bc.CategoryID, AVG(ci.COUNT) AS AvgCheckIns
                    FROM CheckIn ci
                    JOIN BusinessCategory bc ON ci.BusinessID = bc.BusinessID
                    GROUP BY bc.CategoryID
                ),
                BusinessCheckIns AS (
                    SELECT ci.BusinessID, SUM(ci.COUNT) AS TotalCheckIns
                    FROM CheckIn ci
                    GROUP BY ci.BusinessID
                )
                SELECT Distinct b.BusinessName AS name, b.Address AS address, b.City AS city, b.Zipcode,
                      cat.CategoryName AS category_name
                FROM Business b
                JOIN BusinessCategory bc ON b.BusinessID = bc.BusinessID
                JOIN Category cat ON bc.CategoryID = cat.CategoryID
                JOIN BusinessCheckIns bci ON b.BusinessID = bci.BusinessID
                WHERE (bci.TotalCheckIns > (SELECT AvgCheckIns FROM CategoryAverageCheckIns WHERE CategoryID = bc.CategoryID))
                      AND b.Zipcode = %s
                ORDER BY b.BusinessName;
            """, (zipcode,))
            return cur.fetchall()

def get_average_checkins():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            select AVG(totalCheckin) from (
                select SUM(count) as totalCheckin from checkin
                group by businessid,count
            ) as fold_checkin_counts;
            """)
            return cur.fetchall()

def get_successful_businesses(zipcode):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            WITH CategoryAverageCheckIns AS (
                SELECT bc.CategoryID, AVG(c.COUNT) AS AvgCheckIns
                FROM CheckIn c
                JOIN BusinessCategory bc ON c.BusinessID = bc.BusinessID
                GROUP BY bc.CategoryID
            ),
            CategoryAverageReviews AS (
                SELECT bc.CategoryID, AVG(sub.ReviewCount) AS AvgReviewCount
                FROM BusinessCategory bc
                JOIN (
                    SELECT r.BusinessID, COUNT(*) AS ReviewCount
                    FROM Review r
                    GROUP BY r.BusinessID
                ) sub ON bc.BusinessID = sub.BusinessID
                GROUP BY bc.CategoryID
            ),
            BusinessCheckIns as (
                SELECT
                    c.BusinessID,
                    SUM(c.COUNT) AS TotalCheckIns
                FROM
                    CheckIn c
                GROUP BY
                    c.BusinessID
            )
            SELECT DISTINCT b.BusinessName, b.Address, b.City, b.State, b.Zipcode, cat.CategoryName
            FROM Business b
            inner JOIN BusinessCategory bc ON b.BusinessID = bc.BusinessID
            inner JOIN Category cat ON cat.CategoryID = bc.CategoryID
            inner JOIN Review r ON r.BusinessID = b.BusinessID
            inner JOIN CategoryAverageCheckIns caci ON bc.CategoryID = caci.CategoryID
            inner JOIN CategoryAverageReviews car ON bc.CategoryID = car.CategoryID
            inner JOIN BusinessCheckIns bci on bci.BusinessID = b.Businessid
            GROUP BY b.BusinessName, b.Address, b.City, b.State, b.Zipcode, cat.CategoryName, r.BusinessID, car.AvgReviewCount, bci.TotalCheckIns
            having COUNT(r.businessid) > car.AvgReviewCount and bci.TotalCheckIns > 29.5 AND b.Zipcode = %s
            ORDER BY b.BusinessName; 
            """, (zipcode,))
            return cur.fetchall()



def get_expensive_businesses(zipcode):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT DISTINCT
                b.BusinessName,
                b.Address,
                b.City,
                b.State,
                b.Zipcode,
                cat.CategoryName
            FROM
                Business b
            JOIN
                Review r ON b.BusinessID = r.BusinessID
            JOIN
                BusinessCategory bc ON b.BusinessID = bc.BusinessID
            JOIN
                Category cat ON bc.CategoryID = cat.CategoryID
            WHERE
                (LOWER(r.ReviewText) LIKE '% high priced %' OR
                LOWER(r.ReviewText) LIKE '% high cost %' OR
                LOWER(r.ReviewText) LIKE '% expensive %' OR
                LOWER(r.ReviewText) LIKE '% that’s a bit pricey %' OR
                LOWER(r.ReviewText) LIKE '% costs an arm and a leg %' OR
                LOWER(r.ReviewText) LIKE '% exorbitant %' OR
                LOWER(r.ReviewText) LIKE '% costly %' OR
                LOWER(r.ReviewText) LIKE '% high end %' OR
                LOWER(r.ReviewText) LIKE '% pricey %')
                AND b.Zipcode = %s
            ORDER BY
                b.BusinessName;
            """, (zipcode,))
            return cur.fetchall()

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

def get_zipcode_details(zipcode):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT population, meanIncome, COUNT(b.businessid) AS total_businesses
                FROM ZipcodeData zd
                JOIN Business b ON zd.zipcode = b.zipcode
                WHERE zd.zipcode = %s
                GROUP BY zd.zipcode, zd.population, zd.meanIncome;
            """, (zipcode,))
            basic_stats = cur.fetchone()

            cur.execute("""
                SELECT c.categoryname, COUNT(*) AS count
                FROM Business b
                JOIN BusinessCategory bc ON b.businessid = bc.businessid
                JOIN Category c ON bc.categoryid = c.categoryid
                WHERE b.zipcode = %s
                GROUP BY c.categoryName
                ORDER BY count DESC;
            """, (zipcode,))
            categories = cur.fetchall()

            return basic_stats, categories


