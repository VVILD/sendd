__author__ = 'vatsalshah'

import logging
from ..fedex.config import FedexConfig
from ..fedex.services.pickup_service import FedexCreatePickupRequest

FEDEX_CONFIG_OBJ = FedexConfig(key='jFdC6SAqFS9vz7gY',
                               password='6bxCaeVdszjUo2iHw5R3tbrBu',
                               account_number='677853204',
                               meter_number='108284345',
                               express_region_code='APAC',
                               use_test_server=False)

# Set this to the INFO level to see the response from Fedex printed in stdout.
logging.basicConfig(level=logging.INFO)

# This is the object that will be handling our tracking request.
# We're using the FedexConfig object from example_config.py in this dir.
pickup = FedexCreatePickupRequest(FEDEX_CONFIG_OBJ)

pickup.OriginDetail.UseAccountAddress = False
pickup.OriginDetail.PickupDateType = None
pickup.OriginDetail.PickupLocation.Contact.PersonName = "Vatsal Shah"
pickup.OriginDetail.PickupLocation.Contact.CompanyName = "Sendd"
pickup.OriginDetail.PickupLocation.Contact.PhoneNumber = "7738500880"
pickup.OriginDetail.PickupLocation.Address.StreetLines = ["107 Classique Center"]
pickup.OriginDetail.PickupLocation.Address.City = "Mumbai"
pickup.OriginDetail.PickupLocation.Address.StateOrProvinceCode = "Mumbai"
pickup.OriginDetail.PickupLocation.Address.PostalCode = "400093"
pickup.OriginDetail.PickupLocation.Address.CountryCode = "IN"
pickup.OriginDetail.PickupLocation.Address.Residential = False
pickup.OriginDetail.PackageLocation = "FRONT"
pickup.OriginDetail.BuildingPart = "BUILDING"
pickup.OriginDetail.BuildingPartDescription = "1FL"
pickup.OriginDetail.ReadyTimestamp = "2015-10-29T11:00:00"
pickup.OriginDetail.CompanyCloseTime = "20:00:00"

pickup.PackageCount = 1

pickup.TotalWeight.Units = "KG"
pickup.TotalWeight.Value = 1

pickup.CarrierCode = "FDXE"
pickup.OversizePackageCount = 0
pickup.Remarks = "This is a test.  Do not pickup"
pickup.CommodityDescription = "Test Package"
pickup.CountryRelationship = "DOMESTIC"

pickup.send_request()

print(pickup.response)
