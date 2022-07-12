import unittest

from core.keys import keys_show
from modules.auth.query import (
    query_account,
)

class TestQueryAccount(unittest.TestCase):

    def test_query_account(self):
        address = keys_show("account1", "acc")[1]["address"]
        status, response = query_account(address)
        self.assertTrue(status)

    def test_query_account_fail(self):
        status, response = query_account("cosmos1xpcfd7pxfmv6gd50y9mwjq50kwqpqrh5mmw72h")
        self.assertFalse(status)

    def test_query_account_fail_fake(self):
        status, response = query_account("cosmos1xpcfd7pxfmv6gd50y9mwjq50kwqpqrh5mmw72h")
        self.assertTrue(status)

if __name__ == '__main__':
    unittest.main()
