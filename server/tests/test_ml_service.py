import unittest
import numpy as np
from krutrim_cloud import some_function  # Replace with actual function to test

class TestMLService(unittest.TestCase):
    def test_krutrim_functionality(self):
        result = some_function(np.array([1, 2, 3]))
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, (3,))  # Adjust based on expected output shape

if __name__ == '__main__':
    unittest.main()