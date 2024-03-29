#!/usr/bin/env python
"""
This example shows how to create shipments. The variables populated below
represents the minimum required values. You will need to fill all of these, or
risk seeing a SchemaValidationError exception thrown.

Near the bottom of the module, you'll see some different ways to handle the
label data that is returned with the reply.
"""
import logging
import binascii
from django.core.files.base import ContentFile

from ..fedex.config import FedexConfig
from ..fedex.services.ship_service import FedexProcessShipmentRequest


# Change these values to match your testing account/meter number.
FEDEX_CONFIG_OBJ = FedexConfig(key='Ha8gotyUoTHURYW6',
                               password='ueU6dTNMxL0uPsJfxadWBhhjW',
                               account_number='510087640',
                               meter_number='118685245',
                               use_test_server=True)

# Set this to the INFO level to see the response from Fedex printed in stdout.
logging.basicConfig(level=logging.INFO)

# This is the object that will be handling our tracking request.
# We're using the FedexConfig object from example_config.py in this dir.
shipment = FedexProcessShipmentRequest(FEDEX_CONFIG_OBJ)

# This is very generalized, top-level information.
# REGULAR_PICKUP, REQUEST_COURIER, DROP_BOX, BUSINESS_SERVICE_CENTER or STATION
shipment.RequestedShipment.DropoffType = 'REGULAR_PICKUP'

# See page 355 in WS_ShipService.pdf for a full list. Here are the common ones:
# STANDARD_OVERNIGHT, PRIORITY_OVERNIGHT, FEDEX_GROUND, FEDEX_EXPRESS_SAVER
shipment.RequestedShipment.ServiceType = 'PRIORITY_OVERNIGHT'

# What kind of package this will be shipped in.
# FEDEX_BOX, FEDEX_PAK, FEDEX_TUBE, YOUR_PACKAGING
shipment.RequestedShipment.PackagingType = 'YOUR_PACKAGING'

# shipment.RequestedShipment.TotalWeight.Value = 15

# Shipper contact info.
shipment.RequestedShipment.Shipper.Contact.PersonName = 'Ganesh shelar'
shipment.RequestedShipment.Shipper.Contact.CompanyName = 'Sender Company Name'
shipment.RequestedShipment.Shipper.Contact.PhoneNumber = '0805522713'

# Shipper address.
shipment.RequestedShipment.Shipper.Address.StreetLines = ['Address Line 1']
shipment.RequestedShipment.Shipper.Address.City = 'Mumbai'
shipment.RequestedShipment.Shipper.Address.StateOrProvinceCode = 'MH'
shipment.RequestedShipment.Shipper.Address.PostalCode = '400076'
shipment.RequestedShipment.Shipper.Address.CountryCode = 'IN'
# shipment.RequestedShipment.Shipper.Address.Residential = True

# Recipient contact info.
shipment.RequestedShipment.Recipient.Contact.PersonName = 'Manoj Sharma'
shipment.RequestedShipment.Recipient.Contact.CompanyName = 'o i j y n n l v s f i k p r d u a q a z p s r j l v p l o f j m c r b k p a v y '
shipment.RequestedShipment.Recipient.Contact.PhoneNumber = '9012637906'

# Recipient address
shipment.RequestedShipment.Recipient.Address.StreetLines = ['o i j y n n l v s f i k p r d u a q a z p s r j l v p l o f j m c r b k p a v y ', 'Recipient Address Line 2']
shipment.RequestedShipment.Recipient.Address.City = 'Mumbai'
shipment.RequestedShipment.Recipient.Address.StateOrProvinceCode = 'MH'
shipment.RequestedShipment.Recipient.Address.PostalCode = '400093'
shipment.RequestedShipment.Recipient.Address.CountryCode = 'IN'
# This is needed to ensure an accurate rate quote with the response.
# shipment.RequestedShipment.Recipient.Address.Residential = True
shipment.RequestedShipment.EdtRequestType = None

shipment.RequestedShipment.ShippingChargesPayment.Payor.ResponsibleParty.AccountNumber = FEDEX_CONFIG_OBJ.account_number
# Who pays for the shipment?
# RECIPIENT, SENDER or THIRD_PARTY
# shipment.RequestedShipment.ShippingChargesPayment.PaymentType = 'SENDER'
# shipment.RequestedShipment.ShippingChargesPayment.Payor.ResponsibleParty.Address.CountryCode = 'US'


# shipment.RequestedShipment.SpecialServicesRequested = shipment.create_wsdl_object_of_type('PackageSpecialServicesRequested')
# shipment.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = 'COD'
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail = shipment.create_wsdl_object_of_type('CodDetail')
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount = shipment.create_wsdl_object_of_type('Money')
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount.Currency = 'INR'
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount.Amount = 100
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.CollectionType = 'CASH'
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress = shipment.create_wsdl_object_of_type('Party')
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact = shipment.create_wsdl_object_of_type('Contact')
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address = shipment.create_wsdl_object_of_type('Address')
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact.PersonName = 'Sumeet Wadhwa'
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact.CompanyName = 'Crazymind Technologies Pvt. Ltd.'
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact.PhoneNumber = '8879475752'
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.StreetLines = ['303, Building no 5, Lake Heights, Adi Shankaracharya marg', ', Rambaug, IIT-Mumbai, Powai']
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.City = 'Mumbai'
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.StateOrProvinceCode = 'MH'
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.PostalCode = '400076'
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.CountryCode = 'IN'
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.CountryName = 'INDIA'
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.RemitToName = 'Crazymind Technologies Pvt. Ltd.'
# shipment.RequestedShipment.SpecialServicesRequested.CodDetail.ReferenceIndicator = None

shipment.RequestedShipment.CustomsClearanceDetail.DutiesPayment.PaymentType = 'SENDER'
shipment.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.AccountNumber = FEDEX_CONFIG_OBJ.account_number
shipment.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.Contact = ''
shipment.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.Address.CountryCode = 'IN'
shipment.RequestedShipment.CustomsClearanceDetail.DocumentContent = 'NON_DOCUMENTS'
shipment.RequestedShipment.CustomsClearanceDetail.CustomsValue.Currency = 'INR'
shipment.RequestedShipment.CustomsClearanceDetail.CustomsValue.Amount = 400
shipment.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.Purpose = 'NOT_SOLD'
shipment.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.TaxesOrMiscellaneousChargeType = None
shipment.RequestedShipment.CustomsClearanceDetail.Commodities.NumberOfPieces = 1
shipment.RequestedShipment.CustomsClearanceDetail.Commodities.Description = 'Bedsheets'
shipment.RequestedShipment.CustomsClearanceDetail.Commodities.CountryOfManufacture = 'IN'
shipment.RequestedShipment.CustomsClearanceDetail.Commodities.Weight.Value = 1
shipment.RequestedShipment.CustomsClearanceDetail.Commodities.Weight.Units = "KG"
shipment.RequestedShipment.CustomsClearanceDetail.Commodities.Quantity = 1
shipment.RequestedShipment.CustomsClearanceDetail.Commodities.QuantityUnits = 'EA'
shipment.RequestedShipment.CustomsClearanceDetail.Commodities.UnitPrice.Currency = 'INR'
shipment.RequestedShipment.CustomsClearanceDetail.Commodities.UnitPrice.Amount = 100
shipment.RequestedShipment.CustomsClearanceDetail.Commodities.CustomsValue.Currency = 'INR'
shipment.RequestedShipment.CustomsClearanceDetail.Commodities.CustomsValue.Amount = 400
shipment.RequestedShipment.CustomsClearanceDetail.ExportDetail.B13AFilingOption = 'NOT_REQUIRED'
shipment.RequestedShipment.CustomsClearanceDetail.ClearanceBrokerage = None
shipment.RequestedShipment.CustomsClearanceDetail.FreightOnValue = None

# shipment.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = 'COD'


# Specifies the label type to be returned.
# LABEL_DATA_ONLY or COMMON2D
shipment.RequestedShipment.LabelSpecification.LabelFormatType = 'COMMON2D'

# Specifies which format the label file will be sent to you in.
# DPL, EPL2, PDF, PNG, ZPLII
shipment.RequestedShipment.LabelSpecification.ImageType = 'PDF'

# To use doctab stocks, you must change ImageType above to one of the
# label printer formats (ZPLII, EPL2, DPL).
# See documentation for paper types, there quite a few.
shipment.RequestedShipment.LabelSpecification.LabelStockType = 'PAPER_7X4.75'
shipment.RequestedShipment.LabelSpecification.LabelOrder = 'SHIPPING_LABEL_FIRST'

# This indicates if the top or bottom of the label comes out of the 
# printer first.
# BOTTOM_EDGE_OF_TEXT_FIRST or TOP_EDGE_OF_TEXT_FIRST
shipment.RequestedShipment.LabelSpecification.LabelPrintingOrientation = 'BOTTOM_EDGE_OF_TEXT_FIRST'

shipment.RequestedShipment.ShippingDocumentSpecification.ShippingDocumentTypes = 'COMMERCIAL_INVOICE'
shipment.RequestedShipment.ShippingDocumentSpecification.CommercialInvoiceDetail = shipment.create_wsdl_object_of_type('CommercialInvoiceDetail')
shipment.RequestedShipment.ShippingDocumentSpecification.CommercialInvoiceDetail.Format.ImageType = 'PDF'
shipment.RequestedShipment.ShippingDocumentSpecification.CommercialInvoiceDetail.Format.StockType = 'PAPER_LETTER'
# shipment.RequestedShipment.PackageCount = 1

package1_weight = shipment.create_wsdl_object_of_type('Weight')
# Weight, in pounds.
package1_weight.Value = 15
package1_weight.Units = "KG"

package1 = shipment.create_wsdl_object_of_type('RequestedPackageLineItem')
package1.SequenceNumber = 1
package1.PhysicalPackaging = None
package1.Weight = package1_weight
# Un-comment this to see the other variables you may set on a package.
#print package1

# This adds the RequestedPackageLineItem WSDL object to the shipment. It
# increments the package count and total weight of the shipment for you.
shipment.add_package(package1)

# If you'd like to see some documentation on the ship service WSDL, un-comment
# this line. (Spammy).
# print shipment.client

# Un-comment this to see your complete, ready-to-send request as it stands
# before it is actually sent. This is useful for seeing what values you can
# change.
# print shipment.RequestedShipment

# If you want to make sure that all of your entered details are valid, you
# can call this and parse it just like you would via send_request(). If
# shipment.response.HighestSeverity == "SUCCESS", your shipment is valid.
#shipment.send_validation_request()

# Fires off the request, sets the 'response' attribute on the object.
shipment.send_request()

# This will show the reply to your shipment being sent. You can access the
# attributes through the response attribute on the request object. This is
# good to un-comment to see the variables returned by the Fedex reply.
print shipment.response

# Here is the overall end result of the query.
print "HighestSeverity:", shipment.response.HighestSeverity
# Getting the tracking number from the new shipment.
print "Tracking #:", shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].TrackingIds[0].TrackingNumber
# Net shipping costs.
# print "Net Shipping Cost (US$):", shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].PackageRating.PackageRateDetails[0].NetCharge.Amount

# Get the label image in ASCII format from the reply. Note the list indices
# we're using. You'll need to adjust or iterate through these if your shipment
# has multiple packages.
ascii_label_data = COMMERCIAL_INVOICE = shipment.response.CompletedShipmentDetail.ShipmentDocuments[0].Parts[0].Image
# Convert the ASCII data to binary.
label_binary_data = binascii.a2b_base64(ascii_label_data)

"""
This is an example of how to dump a label to a PNG file.
"""
# This will be the file we write the label out to.
# pdf_file = ContentFile(ascii_label_data)
# print(pdf_file)
png_file = open('example_shipment_label.pdf', 'wb')
png_file.write(label_binary_data)
png_file.close()

"""
This is an example of how to print the label to a serial printer. This will not
work for all label printers, consult your printer's documentation for more
details on what formats it can accept.
"""
# Pipe the binary directly to the label printer. Works under Linux
# without requiring PySerial. This WILL NOT work on other platforms.
#label_printer = open("/dev/ttyS0", "w")
#label_printer.write(label_binary_data)
#label_printer.close()

"""
This is a potential cross-platform solution using pySerial. This has not been
tested in a long time and may or may not work. For Windows, Mac, and other
platforms, you may want to go this route.
"""
#import serial
#label_printer = serial.Serial(0)
#print "SELECTED SERIAL PORT: "+ label_printer.portstr
#label_printer.write(label_binary_data)
#label_printer.close()