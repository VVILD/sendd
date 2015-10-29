from core.fedex.config import FedexConfig

__author__ = 'vatsalshah'

#!/usr/bin/env python
"""
PostalCodeInquiryRequest classes are used to validate and receive additional
information about postal codes.
"""
import logging
from ..fedex.services.package_movement import PostalCodeInquiryRequest


FEDEX_CONFIG_INDIA = FedexConfig(key='jFdC6SAqFS9vz7gY',
                                     password='6bxCaeVdszjUo2iHw5R3tbrBu',
                                     account_number='677853204',
                                     meter_number='108284345',
                                     use_test_server=False)
# Set this to the INFO level to see the response from Fedex printed in stdout.
logging.basicConfig(level=logging.INFO)

# We're using the FedexConfig object from example_config.py in this dir.
inquiry = PostalCodeInquiryRequest(FEDEX_CONFIG_INDIA)
inquiry.PostalCode = '29631'
inquiry.CountryCode = 'US'

# Fires off the request, sets the 'response' attribute on the object.
inquiry.send_request()

# See the response printed out.
print inquiry.response