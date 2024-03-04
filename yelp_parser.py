import json
import re


def cleanStringForSQL(s):
    return s.replace("'","''").replace("\n"," ")

def getAttributes(attributes):
    L = []
    for (attribute, value) in list(attributes.items()):
        if isinstance(value, dict):
            L += getAttributes(value)
        else:
            L.append((attribute,value))
    return L



def parseBusinessData():
    with open('./yelp_business.JSON','r') as f:
        business_outfile = open('./yelp_business.txt', 'w')
        address_outfile = open('./yelp_address.txt', 'w')
        category_outfile = open('./yelp_category.txt', 'w')
        line = f.readline()

        name_size = 0
        address_size = 0
        business_size = 0
        city_size = 0

        while line:
            data = json.loads(line)
            business = data['business_id']

            name = cleanStringForSQL(data['name'])
            address = cleanStringForSQL(data['address'])
            city = cleanStringForSQL(data['city'])
            price_range_value = data['attributes'].get('RestaurantsPriceRange2')
            is_open = data['attributes'].get('is_open')

            name_size = max(name_size, len(name))
            address_size = max(address_size, len(address))
            city_size = max(city_size, len(city))
            business_size = max(business_size, len(business))

            address_str = f"'{business}','{address}','{city}','{data['state']}','{data['postal_code']}'"
            business_str = f"'{business}','{name}',{data['stars']},{data['review_count'],{price_range_value},{is_open}}"

            business_outfile.write(business_str + '\n')
            address_outfile.write(address_str + '\n')

            for category in data['categories']:
                category_str = "'{}','{}'".format(business, category)
                category_outfile.write(category_str + '\n')

            line = f.readline()
    business_outfile.close()
    address_outfile.close()
    category_outfile.close()
    f.close()


def parseReviewData():
    with open('./yelp_review.JSON','r') as f:
        outfile =  open('./yelp_review.txt', 'w')
        line = f.readline()
        while line:
            data = json.loads(line)
            review_str = "'" + data['user_id'] + "'," + \
                         "'" + data['business_id'] + "'," + \
                         str(data['stars']) + "," + \
                         "'" + data['date'] + "'," + \
                         "'" + cleanStringForSQL(data['text']) + "'," +  \
                         str(data['useful']) + "," +  \
                         str(data['funny']) + "," + \
                         str(data['cool'])
            outfile.write(review_str +'\n')
            line = f.readline()
    outfile.close()
    f.close()

def parseUserData():
    with open('./yelp_user.JSON','r') as f:
        outfile =  open('./yelp_user.txt', 'w')
        line = f.readline()
        while line:
            data = json.loads(line)
            user_id = data['user_id']
            user_str = \
                      "'" + user_id + "'," + \
                      "'" + cleanStringForSQL(data["name"]) + "'," + \
                      "'" + cleanStringForSQL(data["yelping_since"]) + "'," + \
                      str(data["review_count"]) + "," + \
                      str(data["fans"]) + "," + \
                      str(data["average_stars"]) + "," + \
                      str(data["funny"]) + "," + \
                      str(data["useful"]) + "," + \
                      str(data["cool"])
            outfile.write(user_str+"\n")

            for friend in data["friends"]:
                friend_str = "'" + user_id + "'" + "," + "'" + friend + "'" + "\n"
                outfile.write(friend_str)
            line = f.readline()

    outfile.close()
    f.close()

def parseCheckinData():
    with open('./yelp_checkin.JSON','r') as f:  
        outfile = open('yelp_checkin.txt', 'w')
        line = f.readline()
        while line:
            data = json.loads(line)
            business_id = data['business_id']
            for (dayofweek,time) in data['time'].items():
                for (hour,count) in time.items():
                    checkin_str = f"'{business_id}','{dayofweek}','{hour}',{count}"
                    outfile.write(checkin_str + "\n")
            line = f.readline()
    outfile.close()
    f.close()


parseBusinessData()
parseUserData()
parseCheckinData()
parseReviewData()

