import os
import unittest
from unittest import TestCase
from app import *
from get_data import *

class Basic_url_tests(TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_directions(self):
        resp = requests.post("""http://localhost:5000/directions?postA=53.3037056%2C-6.2169088&postB=O%27Connell%20Street%20Upper%2C%20Dublin%201%2C%20Ireland&htmlDepArr=dep&htmlTime=17%3A21&htmlDate=2019-08-16""")
        self.assertIn("geocoded_waypoints",resp.text) 
    
    def test_amenities(self):
        resp = requests.post(""" http://localhost:5000/amenities?htmlAmenities=bar""")
        self.assertIn("geometry",resp.text) 
    
        
    def test_events(self):
        resp = requests.post("""http://localhost:5000/events""")
        self.assertIn("https://cdn.dublin.ie",resp.text)
    
        
if __name__ == "__main__":
    unittest.main()