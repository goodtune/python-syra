import datetime
import os

from decimal import Decimal
from first import first
from unittest import TestCase

import syra

class SimpleTest(TestCase):

    def setUp(self):
        self.api = syra.TestAPI(timeout=3)

    def test_authenticate(self):
        self.assertTrue(self.api.authenticate())
        self.assertFalse(self.api.authenticate('Z1111'))

    def test_balance_string(self):
        balance = self.api.balance(as_decimal=False)
        self.assertEqual(balance, '$5.72 AUD')

    def test_balance_decimal(self):
        balance = self.api.balance()
        self.assertEqual(balance, Decimal('5.72'))

    def test_contact_list(self):
        contacts = self.api.contact_list()
        self.assertItemsEqual(contacts, [])

    def test_domain_check(self):
        domains = [
            ('example.com', None),
            ('google.com', None),
            ('python-syra.com', True),
        ]
        self.assertItemsEqual(
            self.api.domain_check(*map(first, domains)),
            domains)

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
        self.api = syra.API(timeout=3)

    def test_domain_list(self):
        domains = self.api.domain_list()
        for domain, status, expiry in domains:
            self.assertEqual(isinstance(domain, basestring), True)
            self.assertEqual(isinstance(status, basestring), True)
            self.assertEqual(isinstance(expiry, datetime.date), True)

    def test_domain_info(self):
        info = self.api.domain_info('touchtechnology.com.au')
        self.assertDictEqual(
            info['Eligibility'],
            {
                'BusinessType': "Company",
                'BusinessNumber': "109064039",
                'TradingNumberType': "ACN",
                'BusinessNumberType': "ACN",
                'TradingName': "Touch Technology Pty Ltd",
                'TradingNumber': "109064039",
                'PolicyReason': 1,
                'BusinessName': "Touch Technology Pty Ltd",
            })
