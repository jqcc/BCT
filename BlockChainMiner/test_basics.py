import unittest
from blockChainMiner import app

class MinerTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_f1(self):
        rv = self.app.get('/')
        assert b'SunJQ Graduation Design - BCTS' in rv.data

    def test_f2(self):
        rv = self.app.get('/chain')
        print(rv.data)


if __name__ == '__main__':
    unittest.main()