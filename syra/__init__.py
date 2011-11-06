from decimal import Decimal

import re

from suds.client import Client
from suds.sax.element import Element
from suds.xsd.doctor import ImportDoctor, Import


class API(object):

    ENDPOINT = 'http://soap.secureapi.com.au/API-1.0'
    WSDL = 'http://soap.secureapi.com.au/wsdl/API-1.0.wsdl'

    def __init__(self, reseller_id, api_key, *args, **kwargs):
        imp = Import('http://schemas.xmlsoap.org/soap/encoding/')
        imp.filter.add(self.ENDPOINT)
        doctor = ImportDoctor(imp)

        # create an XML authenticate block which will be passed in the
        # SOAP headers - this API does not make use of Basic HTTP auth
        token = Element('ns1:Authenticate').append(
            Element('AuthenticateRequest').append([
                Element('ResellerID').setText(reseller_id),
                Element('APIKey').setText(api_key),
                ])
            )

        # interogate the WSDL and treat it with our doctor
        self.client = Client(self.WSDL, doctor=doctor)

        # attach our authentication XML
        self.client.set_options(soapheaders=token)

    def balance(self):
        response = self.client.service.GetBalance()
        return Decimal(re.search(r'\d+\.\d{2}', response.APIResponse.Balance).group())

    def domain_check(self, *domains):
        request = self.client.factory.create('DomainCheckRequest')
        request.DomainNames.string = domains
        response = self.client.service.DomainCheck(request)
        return [(o.Item, o.Available) for o in response.APIResponse.AvailabilityList]


class TestAPI(API):

    ENDPOINT = 'http://soap-test.secureapi.com.au/API-1.0'
    WSDL = 'http://soap-test.secureapi.com.au/wsdl/API-1.0.wsdl'
