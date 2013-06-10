import os

from decimal import Decimal
from unittest import TestCase

import syra

class SimpleTest(TestCase):

    def setUp(self):
        reseller_id = os.environ.get('RESELLER_ID')
        api_key = os.environ.get('API_KEY')
        self.api = syra.TestAPI(reseller_id, api_key)

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_balance_string(self):
        balance = self.api.balance(as_decimal=False)
        self.assertEqual(balance, '$5.72 AUD')

    def test_balance_decimal(self):
        balance = self.api.balance()
        self.assertEqual(balance, Decimal('5.72'))

    def test_domain_list(self):
        domains = self.api.domain_list()
        self.assertEqual(domains, [])
