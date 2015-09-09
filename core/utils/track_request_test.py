__author__ = 'vatsalshah'

#!/usr/bin/env python
"""
This example shows how to track shipments.
"""
import logging
from ..fedex.config import FedexConfig
from ..fedex.services.track_service import FedexTrackRequest

# Set this to the INFO level to see the response from Fedex printed in stdout.
logging.basicConfig(level=logging.INFO)

# Change these values to match your testing account/meter number.
CONFIG_OBJ = FedexConfig(key='jFdC6SAqFS9vz7gY',
                         password='6bxCaeVdszjUo2iHw5R3tbrBu',
                         account_number='677853204',
                         meter_number='108284345',
                         use_test_server=False)

# NOTE: TRACKING IS VERY ERRATIC ON THE TEST SERVERS. YOU MAY NEED TO USE
# PRODUCTION KEYS/PASSWORDS/ACCOUNT #.
# We're using the FedexConfig object from example_config.py in this dir.
track = FedexTrackRequest(CONFIG_OBJ)
track.TrackPackageIdentifier.Type = 'TRACKING_NUMBER_OR_DOORTAG'
track.TrackPackageIdentifier.Value = '781044578507'

# Fires off the request, sets the 'response' attribute on the object.
track.send_request()

# See the response printed out.
print track.response

# Look through the matches (there should only be one for a tracking number
# query), and show a few details about each shipment.
print "== Results =="
for match in track.response.TrackDetails:
    print "Tracking #:", match.TrackingNumber
    print "Status:", match.StatusDescription