__author__ = 'vatsalshah'

#!/usr/bin/env python
"""
This example shows how to use the FedEx RateRequest service.
The variables populated below represents the minimum required values.
You will need to fill all of these, or risk seeing a SchemaValidationError
exception thrown by suds.
TIP: Near the bottom of the module, see how to check the if the destination
     is Out of Delivery Area (ODA).
"""
import logging
from ..fedex.config import FedexConfig
from ..fedex.services.rate_service import FedexRateServiceRequest

# Set this to the INFO level to see the response from Fedex printed in stdout.
logging.basicConfig(level=logging.INFO)

# Change these values to match your testing account/meter number.
FEDEX_CONFIG_OBJ = FedexConfig(key='jFdC6SAqFS9vz7gY',
                               password='6bxCaeVdszjUo2iHw5R3tbrBu',
                               account_number='677853204',
                               meter_number='108284345',
                               use_test_server=False)
# This is the object that will be handling our tracking request.
# We're using the FedexConfig object from example_config.py in this dir.
rate_request = FedexRateServiceRequest(FEDEX_CONFIG_OBJ)

# This is very generalized, top-level information.
# REGULAR_PICKUP, REQUEST_COURIER, DROP_BOX, BUSINESS_SERVICE_CENTER or STATION
rate_request.RequestedShipment.DropoffType = 'REGULAR_PICKUP'

# See page 355 in WS_ShipService.pdf for a full list. Here are the common ones:
# STANDARD_OVERNIGHT, PRIORITY_OVERNIGHT, FEDEX_GROUND, FEDEX_EXPRESS_SAVER
rate_request.RequestedShipment.ServiceType = 'STANDARD_OVERNIGHT'

# What kind of package this will be shipped in.
# FEDEX_BOX, FEDEX_PAK, FEDEX_TUBE, YOUR_PACKAGING
rate_request.RequestedShipment.PackagingType = 'YOUR_PACKAGING'

# rate_request.RequestedShipment.TotalWeight.Value = 15

# Shipper contact info.
rate_request.RequestedShipment.Shipper.Contact.PersonName = 'Ganesh shelar'
rate_request.RequestedShipment.Shipper.Contact.CompanyName = 'Sender Company Name'
rate_request.RequestedShipment.Shipper.Contact.PhoneNumber = '0805522713'

# Shipper address.
rate_request.RequestedShipment.Shipper.Address.StreetLines = ['Address Line 1']
rate_request.RequestedShipment.Shipper.Address.City = 'Mumbai'
rate_request.RequestedShipment.Shipper.Address.StateOrProvinceCode = 'MH'
rate_request.RequestedShipment.Shipper.Address.PostalCode = '400076'
rate_request.RequestedShipment.Shipper.Address.CountryCode = 'IN'
# rate_request.RequestedShipment.Shipper.Address.Residential = True

# Recipient contact info.
rate_request.RequestedShipment.Recipient.Contact.PersonName = 'Manoj Sharma'
rate_request.RequestedShipment.Recipient.Contact.CompanyName = 'Recipient Company Name'
rate_request.RequestedShipment.Recipient.Contact.PhoneNumber = '9012637906'

# Recipient address
rate_request.RequestedShipment.Recipient.Address.StreetLines = ['Recipient Address Line 1']
rate_request.RequestedShipment.Recipient.Address.City = 'Mumbai'
rate_request.RequestedShipment.Recipient.Address.StateOrProvinceCode = 'MH'
rate_request.RequestedShipment.Recipient.Address.PostalCode = '400093'
rate_request.RequestedShipment.Recipient.Address.CountryCode = 'IN'
# This is needed to ensure an accurate rate quote with the response.
# rate_request.RequestedShipment.Recipient.Address.Residential = True
rate_request.RequestedShipment.EdtRequestType = None

rate_request.RequestedShipment.ShippingChargesPayment.Payor.ResponsibleParty.AccountNumber = FEDEX_CONFIG_OBJ.account_number
# Who pays for the rate_request?
# RECIPIENT, SENDER or THIRD_PARTY
# rate_request.RequestedShipment.ShippingChargesPayment.PaymentType = 'SENDER'
# rate_request.RequestedShipment.ShippingChargesPayment.Payor.ResponsibleParty.Address.CountryCode = 'US'


rate_request.RequestedShipment.SpecialServicesRequested = rate_request.create_wsdl_object_of_type('PackageSpecialServicesRequested')
rate_request.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = 'COD'
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail = rate_request.create_wsdl_object_of_type('CodDetail')
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount = rate_request.create_wsdl_object_of_type('Money')
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount.Currency = 'INR'
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount.Amount = 100
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CollectionType = 'CASH'
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress = rate_request.create_wsdl_object_of_type('Party')
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact = rate_request.create_wsdl_object_of_type('Contact')
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address = rate_request.create_wsdl_object_of_type('Address')
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact.PersonName = 'Sumeet Wadhwa'
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact.CompanyName = 'Crazymind Technologies Pvt. Ltd.'
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact.PhoneNumber = '8879475752'
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.StreetLines = ['303, Building no 5, Lake Heights, Adi Shankaracharya marg', ', Rambaug, IIT-Mumbai, Powai']
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.City = 'Mumbai'
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.StateOrProvinceCode = 'MH'
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.PostalCode = '400076'
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.CountryCode = 'IN'
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.CountryName = 'INDIA'
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.RemitToName = 'Crazymind Technologies Pvt. Ltd.'
rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.ReferenceIndicator = None

rate_request.RequestedShipment.CustomsClearanceDetail.DutiesPayment.PaymentType = 'SENDER'
rate_request.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.AccountNumber = FEDEX_CONFIG_OBJ.account_number
rate_request.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.Contact = ''
rate_request.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.Address.CountryCode = 'IN'
rate_request.RequestedShipment.CustomsClearanceDetail.DocumentContent = 'NON_DOCUMENTS'
rate_request.RequestedShipment.CustomsClearanceDetail.CustomsValue.Currency = 'INR'
rate_request.RequestedShipment.CustomsClearanceDetail.CustomsValue.Amount = 400
rate_request.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.Purpose = 'SOLD'
rate_request.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.TaxesOrMiscellaneousChargeType = None
rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.NumberOfPieces = 1
rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.Description = 'Bedsheets'
rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.CountryOfManufacture = 'IN'
rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.Weight.Value = 1
rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.Weight.Units = "KG"
rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.Quantity = 1
rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.QuantityUnits = 'EA'
rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.UnitPrice.Currency = 'INR'
rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.UnitPrice.Amount = 100
rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.CustomsValue.Currency = 'INR'
rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.CustomsValue.Amount = 400
rate_request.RequestedShipment.CustomsClearanceDetail.ExportDetail.B13AFilingOption = 'NOT_REQUIRED'
rate_request.RequestedShipment.CustomsClearanceDetail.ClearanceBrokerage = None
rate_request.RequestedShipment.CustomsClearanceDetail.FreightOnValue = None

package1_weight = rate_request.create_wsdl_object_of_type('Weight')
# Weight, in pounds.
package1_weight.Value = 15
package1_weight.Units = "KG"

package1 = rate_request.create_wsdl_object_of_type('RequestedPackageLineItem')
package1.SequenceNumber = 1
package1.PhysicalPackaging = None
package1.Weight = package1_weight
# Un-comment this to see the other variables you may set on a package.
#print package1
# package1.GroupNumber = 0  # default is 0
# The result will be found in RatedPackageDetail, with specified GroupNumber.
package1.GroupPackageCount = 1
# Un-comment this to see the other variables you may set on a package.
#print package1

# This adds the RequestedPackageLineItem WSDL object to the rate_request. It
# increments the package count and total weight of the rate_request for you.
rate_request.add_package(package1)

# If you'd like to see some documentation on the ship service WSDL, un-comment
# this line. (Spammy).
#print rate_request.client

# Un-comment this to see your complete, ready-to-send request as it stands
# before it is actually sent. This is useful for seeing what values you can
# change.
#print rate_request.RequestedShipment

# Fires off the request, sets the 'response' attribute on the object.
rate_request.send_request()

# This will show the reply to your rate_request being sent. You can access the
# attributes through the response attribute on the request object. This is
# good to un-comment to see the variables returned by the FedEx reply.
#print rate_request.response

# Here is the overall end result of the query.
print "HighestSeverity:", rate_request.response.HighestSeverity

# RateReplyDetails can contain rates for multiple ServiceTypes if ServiceType was set to None
for service in rate_request.response.RateReplyDetails:
    for detail in service.RatedShipmentDetails:
        for surcharge in detail.ShipmentRateDetail.Surcharges:
            if surcharge.SurchargeType == 'OUT_OF_DELIVERY_AREA':
                print "%s: ODA rate_request charge %s" % (service.ServiceType, surcharge.Amount.Amount)

    for rate_detail in service.RatedShipmentDetails:
        print "%s: Net FedEx Charge %s %s" % (
            service.ServiceType, rate_detail.ShipmentRateDetail.TotalNetFedExCharge.Currency,
            rate_detail.ShipmentRateDetail.TotalNetFedExCharge.Amount)