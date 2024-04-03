
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
            cur.execute("SELECT name, city, state FROM business WHERE city=%s AND state=%s ORDER BY name;", (city, state))
            businesses = cur.fetchall()
            return businesses
        
def list_businesses_state(state):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name, city, state FROM business WHERE state=%s ORDER BY name;", (state,))
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
        
def list_businesses_filtered(state, city, zipcode, category):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT BusinessName, Address, City, State, Zipcode, CategoryName 
                           FROM Business
                           INNER JOIN BusinessCategory ON Business.BusinessID = BusinessCategory.BusinessID
                           INNER JOIN Category ON BusinessCategory.CategoryID = Category.CategoryID
                           WHERE State = %s AND City = %s AND Zipcode = %s AND CategoryName = %s
                           ORDER BY BusinessName;""",
                        (state, city, zipcode, category))
            businesses = cur.fetchall()
            return businesses


def get_popular_businesses():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            WITH CategoryAverageCheckIns AS (
                SELECT bc.CategoryID, AVG(c.COUNT) AS AvgCheckIns
                FROM CheckIn c
                JOIN BusinessCategory bc ON c.BusinessID = bc.BusinessID
                GROUP BY bc.CategoryID
            ),
            BusinessCheckIns AS (
                SELECT c.BusinessID, SUM(c.COUNT) AS TotalCheckIns
                FROM CheckIn c
                GROUP BY c.BusinessID
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
            BusinessReviews AS (
                SELECT r.BusinessID, COUNT(*) AS TotalReviews
                FROM Review r
                GROUP BY r.BusinessID
            )
            SELECT DISTINCT b.BusinessName, b.Address, b.City, b.State, b.Zipcode, cat.CategoryName, br.TotalReviews
            FROM Business b
            JOIN BusinessCategory bc ON b.BusinessID = bc.BusinessID
            JOIN Category cat ON bc.CategoryID = cat.CategoryID
            JOIN BusinessCheckIns bci ON b.BusinessID = bci.BusinessID
            JOIN BusinessReviews br ON b.BusinessID = br.BusinessID
            JOIN CategoryAverageCheckIns caci ON bc.CategoryID = caci.CategoryID
            JOIN CategoryAverageReviews car ON bc.CategoryID = car.CategoryID
            WHERE bci.TotalCheckIns > caci.AvgCheckIns AND br.TotalReviews > car.AvgReviewCount
            ORDER BY b.BusinessName;
            """)
            return cur.fetchall()

        
def get_successful_businesses():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            WITH BusinessAge AS (
                SELECT
                    b.BusinessID,
                    MIN(r.ReviewDate) AS FirstReviewDate,
                    EXTRACT(YEAR FROM AGE(TIMESTAMP '2023-04-01', MIN(r.ReviewDate))) AS YearsInOperation
                FROM
                    Business b
                JOIN
                    Review r ON b.BusinessID = r.BusinessID
                GROUP BY
                    b.BusinessID
                HAVING
                    EXTRACT(YEAR FROM AGE(TIMESTAMP '2023-04-01', MIN(r.ReviewDate))) >= 3
            ),
            CategoryAverageCheckIns AS (
                SELECT
                    bc.CategoryID,
                    AVG(c.COUNT) AS AvgCheckIns
                FROM
                    CheckIn c
                JOIN
                    BusinessCategory bc ON c.BusinessID = bc.BusinessID
                GROUP BY
                    bc.CategoryID
            ),
            BusinessCheckIns AS (
                SELECT
                    c.BusinessID,
                    SUM(c.COUNT) AS TotalCheckIns
                FROM
                    CheckIn c
                GROUP BY
                    c.BusinessID
            ),
            FilteredBusinesses AS (
                SELECT
                    b.BusinessID,
                    b.BusinessName,
                    b.Address,
                    b.City,
                    b.State,
                    b.Zipcode,
                    COUNT(r.ReviewID) AS TotalReviews,
                    SUM(c.COUNT) AS TotalCheckIns
                FROM
                    Business b
                JOIN
                    BusinessAge ba ON b.BusinessID = ba.BusinessID
                JOIN
                    BusinessCheckIns bci ON b.BusinessID = bci.BusinessID
                JOIN
                    Review r ON b.BusinessID = r.BusinessID
                JOIN
                    CheckIn c ON b.BusinessID = c.BusinessID
                GROUP BY
                    b.BusinessID, b.BusinessName, b.Address, b.City, b.State, b.Zipcode
            )
            SELECT
                DISTINCT fb.BusinessName,
                fb.Address,
                fb.City,
                fb.State,
                fb.Zipcode,
                cat.CategoryName,
                fb.TotalReviews,
                fb.TotalCheckIns
            FROM
                FilteredBusinesses fb
            JOIN
                BusinessCategory bc ON fb.BusinessID = bc.BusinessID
            JOIN
                Category cat ON bc.CategoryID = cat.CategoryID
            JOIN
                CategoryAverageCheckIns cai ON bc.CategoryID = cai.CategoryID
            WHERE
                fb.TotalCheckIns > cai.AvgCheckIns
            GROUP BY
                fb.BusinessName, fb.Address, fb.City, fb.State, fb.Zipcode, cat.CategoryName, fb.TotalReviews, fb.TotalCheckIns
            HAVING
                fb.TotalReviews > 100
            ORDER BY
                fb.TotalReviews DESC;
            """)
            return cur.fetchall()



def get_expensive_businesses():
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
                LOWER(r.ReviewText) LIKE '%high priced%' OR
                LOWER(r.ReviewText) LIKE '%high cost%' OR
                LOWER(r.ReviewText) LIKE '%expensive%' OR
                LOWER(r.ReviewText) LIKE '%that’s a bit pricey%' OR
                LOWER(r.ReviewText) LIKE '%costs an arm and a leg%' OR
                LOWER(r.ReviewText) LIKE '%exorbitant%' OR
                LOWER(r.ReviewText) LIKE '%costly%' OR
                LOWER(r.ReviewText) LIKE '%high end%' OR
                LOWER(r.ReviewText) LIKE '%pricey%'
            ORDER BY
                b.BusinessName;
            """)
            return cur.fetchall()
