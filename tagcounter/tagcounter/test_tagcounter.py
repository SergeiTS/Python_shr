import unittest
from tagcounter import *

class TestTagCounter(unittest.TestCase):
    
    def test_alias_correctness(self):
        self.assertEqual(sites_aliases("lcf"), "learn.chef.io")
        #self.assertEqual(sites_aliases("ggl"), "google.com")
    
    def test_link_correctness(self):
        self.assertEqual(link_checker("google.com"), "http://google.com")

    def test_blocked_sites(self):
        with self.assertRaises(TimeoutError):
            test = TagCounter()
            test.read_url_content("http://yandex.ru")

if __name__ == '__main__': unittest.main()
