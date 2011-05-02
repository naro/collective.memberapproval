import unittest2 as unittest

from collective.memberapproval.tests.layer import MEMBERAPPROVAL_INTEGRATION_TESTING

class ApprovalTest(unittest.TestCase):
    
    layer = MEMBERAPPROVAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_one(self):
        self.assertEqual(1,2)