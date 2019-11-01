import os
import re
import ssl
from decimal import Decimal
from operator import itemgetter

from dateutil.parser import parse
from first import first
from suds.client import Client
from suds.sax.element import Element
from suds.xsd.doctor import Import, ImportDoctor


class API(object):
    ENDPOINT = "https://soap.secureapi.com.au/API-1.2"
    WSDL = "https://soap.secureapi.com.au/wsdl/API-1.2.wsdl"

    def __init__(
        self, reseller_id=None, api_key=None, timeout=90, verify=True, *args, **kwargs
    ):
        if reseller_id is None:
            reseller_id = os.getenv("SYRA_RESELLER_ID")
        if api_key is None:
            api_key = os.getenv("SYRA_API_KEY")
        if verify is None:
            verify = True

        self.reseller_id = reseller_id
        self.api_key = api_key

        imp = Import("http://schemas.xmlsoap.org/soap/encoding/")
        imp.filter.add(self.ENDPOINT)
        doctor = ImportDoctor(imp)

        # create an XML authenticate block which will be passed in the
        # SOAP headers - this API does not make use of Basic HTTP auth
        token = Element("ns1:Authenticate").append(
            Element("AuthenticateRequest").append(
                [
                    Element("ResellerID").setText(reseller_id),
                    Element("APIKey").setText(api_key),
                ]
            )
        )

        if not verify and hasattr(ssl, "_create_unverified_https_context"):
            ssl._create_default_https_context = ssl._create_unverified_https_context

        # interrogate the WSDL and treat it with our doctor
        self.client = Client(self.WSDL, doctor=doctor, timeout=timeout)

        # attach our authentication XML
        self.client.set_options(soapheaders=token)

    ### generic api operations

    def authenticate(self, reseller_id=None, api_key=None):
        request = self.client.factory.create("AuthenticateRequest")
        request.ResellerID = reseller_id or self.reseller_id
        request.APIKey = api_key or self.api_key
        response = self.client.service.Authenticate(request)
        return getattr(response.APIResponse, "Success", False)

    def balance(self, as_decimal=True):
        response = self.client.service.GetBalance()
        result = response.APIResponse.Balance
        if as_decimal:
            result = Decimal(re.search(r"\d+\.\d{2}", result).group())
        return result

    def contact_list(self):
        request = self.client.service.GetContactIdentifierList()
        if hasattr(request.APIResponse, "ContactIdentifierList"):
            for identifier in request.APIResponse.ContactIdentifierList:
                yield self.contact_info(identifier)

    def domain_list(self):
        request = self.client.service.GetDomainList()
        domain_list = getattr(request.APIResponse, "DomainList", [])
        return [self._domain_list_item(each) for each in domain_list]

    ### contact operations

    def contact_info(self, identifier):
        request = self.client.factory.create("ContactInfoRequest")
        request.ContactIdentifier = identifier
        response = self.client.service.ContactInfo(request)
        return self._contact_details(response)

    ### domain operations

    def domain_check(self, *domains):
        request = self.client.factory.create("DomainCheckRequest")
        request.DomainNames.string = domains
        response = self.client.service.DomainCheck(request)
        return [
            self._availability_item(each)
            for each in response.APIResponse.AvailabilityList
        ]

    def _domain_info(self, domain):
        request = self.client.factory.create("DomainInfoRequest")
        request.DomainName = domain
        return self.client.service.DomainInfo(request)

    def domain_info(self, domain):
        return self._domain_details(self._domain_info(domain))

    def domain_create(self, domain, **kwargs):
        raise NotImplementedError

    def domain_update(
        self,
        domain,
        admin_contact_id=None,
        billing_contact_id=None,
        technical_contact_id=None,
        name_servers=None,
    ):
        info = self._domain_info(domain).APIResponse.DomainDetails
        request = self.client.factory.create("DomainUpdateRequest")
        request.DomainName = domain
        # Assign any provided values, keep existing ones as retrieved from
        # DomainInfo request, and get readt to assign them.
        request.AdminContactIdentifier = admin_contact_id or info.AdminContactIdentifier
        request.BillingContactIdentifier = (
            billing_contact_id or info.BillingContactIdentifier
        )
        request.TechContactIdentifier = (
            technical_contact_id or info.TechContactIdentifier
        )
        if name_servers:
            request.NameServers.item = []
            for host, ip in name_servers.items():
                ns = self.client.factory.create("NameServer")
                ns.Host = host
                ns.IP = ip
                request.NameServers.item.append(ns)
        else:
            request.NameServers = info.NameServers
        response = self.client.service.DomainUpdate(request)
        return self._domain_details(response)

    def domain_delete(self, domain):
        request = self.client.factory.create("DomainDeleteRequest")
        request.DomainName = domain
        response = self.client.service.DomainDelete(request)
        return response.APIResponse.Success

    def domain_renew(self, domain, period):
        request = self.client.factory.create("DomainRenewRequest")
        request.DomainName = domain
        request.RenewalPeriod = period
        response = self.client.service.DomainRenew(request)
        return self._domain_details(response)

    def domain_price_list(self):
        response = self.client.service.GetDomainPriceList()
        return self._domain_price_list(response)

    ### private methods

    def _availability_item(self, o):
        return (first(o.Item), first(o.Available))

    def _contact_details(self, response):
        c = {}
        for k, v in response.APIResponse.ContactDetails:
            c[k] = v
        return c

    def _domain_details(self, response):
        d = {}
        for k, v in response.APIResponse.DomainDetails:
            if k == "NameServers":
                d[k] = [dict(Host=first(o.Host), IP=first(o.IP)) for o in v]
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
            expiry_date = parse(first(o.Expiry)).date()
        except (AttributeError, TypeError):
            expiry_date = first(o.Expiry)
        return (first(o.DomainName), first(o.Status), expiry_date)

    def _domain_price_list(self, response):
        d = {}
        for item in response.APIResponse.DomainPriceList:
            data = dict((k, first(v)) for k, v in item)
            product = data.pop("Product")
            d[product] = data
        return d


class TestAPI(API):
    ENDPOINT = "http://soap-test.secureapi.com.au/API-1.2"
    WSDL = "http://soap-test.secureapi.com.au/wsdl/API-1.2.wsdl"

    def spawn_domains_for_transfer(self):
        # It seems as though this method is not working properly
        # at the server side?
        response = self.client.service.SpawnDomainsForTransfer()
        return response
