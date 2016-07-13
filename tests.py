import datetime
import os

from decimal import Decimal
from unittest import TestCase

import syra

class SimpleTest(TestCase):

    def setUp(self):
        self.api = syra.TestAPI()

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

    def test_domain_price_list(self):
        products = self.api.domain_price_list()
        com_au = products.get('com.au')
        co_uk = products.get('co.uk')
        self.assertEqual(com_au, {'MinimumPeriod': 2, 'Price': 10.0})
        self.assertEqual(co_uk, {'MinimumPeriod': 1, 'Price': 9.25})

class LiveTest(TestCase):

    def setUp(self):
        reseller_id = os.environ.get('RESELLER_ID')
        api_key = os.environ.get('API_KEY')
        self.api = syra.API(reseller_id, api_key)

    def test_domain_list(self):
        domains = self.api.domain_list()
        for domain, status, expiry in domains:
            self.assertEqual(isinstance(domain, basestring), True)
            self.assertEqual(isinstance(status, basestring), True)
            self.assertEqual(isinstance(expiry, datetime.date), True)
