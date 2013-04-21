from unittest import TestCase

import syra

class SimpleTest(TestCase):

    def setUp(self):
        self.api = syra.TestAPI(TEST_RESELLER_ID, TEST_API_KEY)

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_balance_string(self):
        balance = self.api.balance(as_decimal=False)
        self.assertEqual(balance, '$5.72 AUD')
