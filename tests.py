# Version: 0*
# Date: 6.1.18
# Time: 15:02 GMT+5

import unittest
import tasker

my_number_new = 2

class TestTables(unittest.TestCase):
    
    def setUp(self):
        self.my_number_new = 1

    def test_simple(self):
        self.assertEqual(self.my_number_new, 1)


if __name__ == '__main__':
    unittest.main()
