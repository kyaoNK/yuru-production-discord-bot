import unittest

def suite():
    loader = unittest.TestLoader()
    test_suite = loader.discover(start=".", pattern="test_*.py")
    return test_suite

if __name__=="__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())