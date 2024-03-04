import unittest
from unittest.mock import patch
import psycopg2
from SQLaccess import *

# In theory we would have a seperate test database but given this is a school project there was no need
def connect_test_db():
    """Function to connect to the test database."""
    return psycopg2.connect(
        dbname="milestone1db",  
        user="postgres",  
        password="8991",  
        host="localhost"
    )
'''
building unit test out so they can easily be used in the future as we add 
more things I realize there not really needed for just the three functions
'''
class TestDatabaseFunctions(unittest.TestCase):

    @patch('SQLaccess.connect_db', side_effect=connect_test_db)
    def test_list_states(self, mock_connect_db):
        expected_states = [('AZ  ',), ('IL  ',), ('NC  ',), ('NV  ',), ('PA  ',), ('SC  ',), ('WI  ',)]
        states = list_states()
        self.assertEqual(states, expected_states)

    @patch('SQLaccess.connect_db', side_effect=connect_test_db)
    def test_list_cities(self, mock_connect_db):
        test_state = 'AZ  '
        expected_cities = [('Ahwatukee',), ('Anthem',)]
        cities = list_cities(test_state)
        self.assertEqual(sorted(cities)[0:2], sorted(expected_cities))

    @patch('SQLaccess.connect_db', side_effect=connect_test_db)
    def test_list_businesses(self, mock_connect_db):
        test_state = 'AZ  '
        test_city = 'Ahwatukee'
        expected_businesses = [("Cupz N' Crepes", 'Ahwatukee', 'AZ  '), ('Desert Dog Pet Care', 'Ahwatukee', 'AZ  '), ('Florencia Pizza Bistro', 'Ahwatukee', 'AZ  '), ('Hi-Health', 'Ahwatukee', 'AZ  '), ('My Wine Cellar', 'Ahwatukee', 'AZ  ')]
        businesses = list_businesses_state_city(test_city, test_state)
        self.assertTrue(set(expected_businesses).issubset(set(businesses)))


if __name__ == '__main__':
    unittest.main()