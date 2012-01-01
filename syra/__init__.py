from decimal import Decimal
from operator import itemgetter

import re

from dateutil.parser import parse
from suds.client import Client
from suds.sax.element import Element
from suds.xsd.doctor import ImportDoctor, Import


class API(object):

    ENDPOINT = 'http://soap.secureapi.com.au/API-1.0'
    WSDL = 'http://soap.secureapi.com.au/wsdl/API-1.0.wsdl'

    def __init__(self, reseller_id, api_key, *args, **kwargs):
        self.reseller_id = reseller_id
        self.api_key = api_key

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

    ### generic api operations
    
    def authenticate(self, reseller_id=None, api_key=None):
        request = self.client.factory.create('AuthenticateRequest')
        request.ResellerID = reseller_id or self.reseller_id
        request.APIKey = api_key or self.api_key
        response = self.client.service.Authenticate(request)
        return response.APIResponse.Success
        
    def balance(self, as_decimal=True):
        response = self.client.service.GetBalance()
        result = response.APIResponse.Balance
        if as_decimal:
            result = Decimal(re.search(r'\d+\.\d{2}', result).group())
        return result

    def domain_list(self):
        request = self.client.service.GetDomainList()
        return map(self._domain_list_item, request.APIResponse.DomainList)

    ### domain operations
    
    def domain_check(self, *domains):
        request = self.client.factory.create('DomainCheckRequest')
        request.DomainNames.string = domains
        response = self.client.service.DomainCheck(request)
        return map(self._availability_item, response.APIResponse.AvailabilityList)

    def domain_info(self, domain):
        request = self.client.factory.create('DomainInfoRequest')
        request.DomainName = domain
        response = self.client.service.DomainInfo(request)
        return self._domain_details(response)
    
    def domain_create(self, domain, **kwargs):
        raise NotImplementedError
    
    def domain_update(self, domain, **kwargs):
        raise NotImplementedError
    
    def domain_delete(self, domain):
        request = self.client.factory.create('DomainDeleteRequest')
        request.DomainName = domain
        response = self.client.service.DomainDelete(request)
        return response.APIResponse.Success
    
    def domain_renew(self, domain, period):
        request = self.client.factory.create('DomainRenewRequest')
        request.DomainName = domain
        request.RenewalPeriod = period
        response = self.client.service.DomainRenew(request)
        return self._domain_details(response)
    
    ### private methods
    
    def _availability_item(self, o):
    	return (o.Item, o.Available)

    def _domain_details(self, response):
        d = {}
        for k, v in response.APIResponse.DomainDetails:
            if k == "NameServers":
                d[k] = [(o.Host, o.IP) for o in v]
            elif k == "Eligibility":
                d[k] = dict(zip(v.__keylist__, itemgetter(*v.__keylist__)(v)))
            elif k == "Expiry":
                try:
                    d[k] = parse(v).date()
                except (AttributeError, TypeError):
                    d[k] = v
            else:
                d[k] = v
        return d

    def _domain_list_item(self, o):
        try:
            expiry_date = parse(o.Expiry).date()
        except (AttributeError, TypeError):
            expiry_date = o.Expiry
        return (o.DomainName, o.Status, expiry_date)


class TestAPI(API):

    ENDPOINT = 'http://soap-test.secureapi.com.au/API-1.0'
    WSDL = 'http://soap-test.secureapi.com.au/wsdl/API-1.0.wsdl'

    def spawn_domains_for_transfer(self):
        # it seems as though this method is not working properly at the server side
        response = self.client.service.SpawnDomainsForTransfer()
        return response