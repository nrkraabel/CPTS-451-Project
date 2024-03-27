import json
import re
import psycopg2

def cleanStringForSQL(s):
    return s.replace("'","''").replace("\n"," ")

def getAttributes(attributes, attribute_set, business_attributes, business_id):
    for (attribute, value) in list(attributes.items()):
        if isinstance(value, dict):
            getAttributes(value, attribute_set, business_attributes, business_id)
        else:
            attribute_set.add(attribute)
            business_attribute = {}
            business_attribute['business_id'] = business_id
            business_attribute['attribute'] = attribute
            business_attribute['value'] = value
            business_attributes.append(business_attribute)

def insertReview(connection, business_id, review, funny, cool, useful, review_stars, review_date):
    sql_str = f"""
        INSERT INTO Review(BusinessID, Funny, Cool, Useful, ReviewStars, ReviewText, ReviewDate)
        VALUES('{business_id}', {funny}, {cool}, {useful}, {review_stars}, '{review}', '{review_date}');
    """
    connection.execute(sql_str)

def insertCheckIn(connection, business_id, day, time, count):
    sql_str = f"""
        INSERT INTO CheckIn(BusinessID, DAY, TIME, COUNT)
        VALUES('{business_id}', '{day}', '{time}', {count});
    """
    connection.execute(sql_str)

def insertBusiness(connection, business_id, business_name, stars, review_rating, check_ins, review_count, state, city, address, postal_code):
    sql_str = f"""
        INSERT INTO Business(BusinessID, BusinessName, Stars, ReviewRating, CheckIns, ReviewCount, State, City, Address, ZipCode)
        VALUES ('{business_id}', '{business_name}', {stars}, {review_rating}, {check_ins}, {review_count}, '{state}', '{city}', '{address}', {postal_code});
    """
    connection.execute(sql_str)

def insertAttribute(connection, attributes):
    # if performance is bad, do a bulk insert
    for attribute in attributes:
        sql_str = f"""
            INSERT INTO Attribute(AttributeName) VALUES ('{attribute}')
        """
        connection.execute(sql_str)


def insertCategory(connection, categories):
    for category in categories:
        #print(category)
        sql_str = f"""
            INSERT INTO Category(CategoryName) VALUES ('{category}')
        """
        connection.execute(sql_str)

def insertBusinessAttribute(connection, business_attributes):
    for business_attribute in business_attributes:
        value = None
        flag = None
        if(isinstance(business_attribute['value'], str)):
            value = f"'{business_attribute['value']}'"
            flag = "NULL"
        else:
            value = "NULL"
            flag = business_attribute['value'] == True
        sql_str = f"""
            INSERT INTO BusinessAttribute(BusinessID, AttributeID, AttributeValue, AttributeFlag) 
            SELECT 
                b.BusinessID,
                a.AttributeID, 
                {value} AS AttributeValue,
                {flag} AS AttributeFlag
            FROM Business AS b
            INNER JOIN Attribute AS a ON a.AttributeName = '{business_attribute['attribute']}'
            WHERE b.BusinessID = '{business_attribute['business_id']}'
        """
        connection.execute(sql_str)

def insertBusinessCategory(connection, business_categories):
    for business_category in business_categories:
        sql_str = f"""
            INSERT INTO BusinessCategory(BusinessID, CategoryID) 
            SELECT 
                b.BusinessID,
                c.CategoryID
            FROM Business b
            INNER JOIN Category AS c ON c.CategoryName = '{business_category['category']}'
            WHERE b.BusinessID = '{business_category['business_id']}'
        """
        connection.execute(sql_str)

def parseBusinessData(connection):
    attributes = set()
    categories = set()
    business_attributes = []
    business_categories = []

    with open('./data/yelp_business.JSON','r') as f:
        #business_outfile = open('./yelp_business.txt', 'w')
        #address_outfile = open('./yelp_address.txt', 'w')
        #category_outfile = open('./yelp_category.txt', 'w')
        line = f.readline()

        while line:
            data = json.loads(line)
            business = data['business_id']

            name = cleanStringForSQL(data['name'])
            address = cleanStringForSQL(data['address'])
            city = cleanStringForSQL(data['city'])
            state = cleanStringForSQL(data['state'])
            zipcode = cleanStringForSQL(data['postal_code'])
            stars = data['stars']
            review_count = data['review_count']
            check_ins = 0
            review_rating = 0

            insertBusiness(connection.cursor(), business, name, stars, review_rating, check_ins, review_count, state, city, address, zipcode)


            getAttributes(data['attributes'], attributes, business_attributes, business)

            for category in data['categories']:
                category = cleanStringForSQL(category)
                categories.add(category)
                business_category = {}
                business_category['business_id'] = business
                business_category['category'] = category
                business_categories.append(business_category)

            #address_str = f"'{business}','{address}','{city}','{data['state']}','{data['postal_code']}'"
            #business_str = f"'{business}','{name}',{data['stars']},{data['review_count'],{price_range_value},{is_open}}"

            #business_outfile.write(business_str + '\n')
            #address_outfile.write(address_str + '\n')

            #for category in data['categories']:
            #    category_str = "'{}','{}'".format(business, category)
            #    category_outfile.write(category_str + '\n')
            line = f.readline()
    
    insertCategory(connection.cursor(), categories)
    insertAttribute(connection.cursor(), attributes)
    insertBusinessAttribute(connection.cursor(), business_attributes)
    insertBusinessCategory(connection.cursor(), business_categories)
    connection.commit()
    
    #business_outfile.close()
    #address_outfile.close()
    #category_outfile.close()
    f.close()


def parseReviewData(connection):
    with open('./data/yelp_review.JSON','r') as f:
        #outfile =  open('./yelp_review.txt', 'w')
        line = f.readline()
        while line:
            data = json.loads(line)
            business_id = data['business_id']
            stars = data['stars']
            date = data['date']
            funny = data['funny']
            cool = data['cool']
            useful = data['useful']
            text = cleanStringForSQL(data['text'])

            #review_str = "'" + data['user_id'] + "'," + \
            #             "'" + data['business_id'] + "'," + \
            #             str(data['stars']) + "," + \
            #             "'" + data['date'] + "'," + \
            #             "'" + cleanStringForSQL(data['text']) + "'," +  \
            #             str(data['useful']) + "," +  \
            #             str(data['funny']) + "," + \
            #             str(data['cool'])
            #outfile.write(review_str +'\n')
            insertReview(connection.cursor(), business_id, text, funny, cool, useful, stars, date)
            line = f.readline()
    #outfile.close()
    connection.commit()
    f.close()

def parseCheckinData(connection):
    with open('./data/yelp_checkin.JSON','r') as f:  
        #outfile = open('yelp_checkin.txt', 'w')
        line = f.readline()
        while line:
            data = json.loads(line)
            business_id = data['business_id']
            for (dayofweek,time) in data['time'].items():
                for (hour,count) in time.items():
                    checkin_str = f"'{business_id}','{dayofweek}','{hour}',{count}"
                    #outfile.write(checkin_str + "\n")
                    insertCheckIn(connection.cursor(),business_id, dayofweek, hour, count)
            line = f.readline()
    #outfile.close()
    connection.commit()
    f.close()

try:
    conn = psycopg2.connect("dbname='yelpdb' user='postgres' host='localhost' password='postgres'")
except:
    print('Unable to connect to the database!')


#parseBusinessData(conn)
#parseCheckinData(conn)
parseReviewData(conn)

