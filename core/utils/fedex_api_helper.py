import logging
import binascii
# Use the fedex directory included in the downloaded package instead of
# any globally installed versions.
import os
import sys
from django.core.files.base import ContentFile
from core.models import StateCodes

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.fedex.config import FedexConfig
from core.fedex.services.ship_service import FedexProcessShipmentRequest

__author__ = 'vatsalshah'


class Fedex:
    # Change these values to match your testing account/meter number.
    FEDEX_CONFIG_OBJ = FedexConfig(key='Ha8gotyUoTHURYW6',
                                   password='ueU6dTNMxL0uPsJfxadWBhhjW',
                                   account_number='510087640',
                                   meter_number='118685245',
                                   use_test_server=False)
    # Set this to the INFO level to see the response from Fedex printed in stdout.
    logging.basicConfig(level=logging.INFO)

    def __init__(self):
        self.shipment = None

    def create_shipment(self, sender, receiver, item, dropoff_type='REGULAR_PICKUP', service_type='STANDARD_OVERNIGHT'):

        # This is the object that will be handling our tracking request.
        # We're using the FedexConfig object from example_config.py in this dir.
        shipment = FedexProcessShipmentRequest(self.FEDEX_CONFIG_OBJ)

        # This is very generalized, top-level information.
        # REGULAR_PICKUP, REQUEST_COURIER, DROP_BOX, BUSINESS_SERVICE_CENTER or STATION
        shipment.RequestedShipment.DropoffType = str(dropoff_type)

        # See page 355 in WS_ShipService.pdf for a full list. Here are the common ones:
        # STANDARD_OVERNIGHT, PRIORITY_OVERNIGHT, FEDEX_GROUND, FEDEX_EXPRESS_SAVER
        shipment.RequestedShipment.ServiceType = str(service_type)

        # What kind of package this will be shipped in.
        # FEDEX_BOX, FEDEX_PAK, FEDEX_TUBE, YOUR_PACKAGING
        shipment.RequestedShipment.PackagingType = 'YOUR_PACKAGING'

        # Shipper contact info.
        shipment.RequestedShipment.Shipper.Contact.PersonName = str(sender['name'])
        if sender['company']:
            shipment.RequestedShipment.Shipper.Contact.CompanyName = str(sender['company'])
        shipment.RequestedShipment.Shipper.Contact.PhoneNumber = str(sender['phone'])

        # Shipper address.
        shipment.RequestedShipment.Shipper.Address.StreetLines = [str(sender['address1']), str(sender['address2'])]
        shipment.RequestedShipment.Shipper.Address.City = str(sender['city'])
        state_code = StateCodes.objects.get(subdivision_name=str(sender['state']))
        shipment.RequestedShipment.Shipper.Address.StateOrProvinceCode = str(state_code.code).split('-')[1]
        shipment.RequestedShipment.Shipper.Address.PostalCode = str(sender['pincode'])
        shipment.RequestedShipment.Shipper.Address.CountryCode = str(sender['country_code'])
        # shipment.RequestedShipment.Shipper.Address.Residential = not sender['is_business']

        # Recipient contact info.
        shipment.RequestedShipment.Recipient.Contact.PersonName = str(receiver['name'])
        if receiver['company']:
            shipment.RequestedShipment.Recipient.Contact.CompanyName = str(receiver['company'])
        shipment.RequestedShipment.Recipient.Contact.PhoneNumber = str(receiver['phone'])

        # Recipient address
        shipment.RequestedShipment.Recipient.Address.StreetLines = [str(receiver['address1']), str(receiver['address2'])]
        shipment.RequestedShipment.Recipient.Address.City = str(receiver['city'])
        state_code = StateCodes.objects.get(subdivision_name=str(receiver['state']))
        shipment.RequestedShipment.Recipient.Address.StateOrProvinceCode = str(state_code.code).split('-')[1]
        shipment.RequestedShipment.Recipient.Address.PostalCode = str(receiver['pincode'])
        shipment.RequestedShipment.Recipient.Address.CountryCode = str(receiver['country_code'])
        # This is needed to ensure an accurate rate quote with the response.
        # shipment.RequestedShipment.Recipient.Address.Residential = not receiver['is_business']
        shipment.RequestedShipment.EdtRequestType = None

        shipment.RequestedShipment.ShippingChargesPayment.Payor.ResponsibleParty.AccountNumber = self.FEDEX_CONFIG_OBJ.account_number

        shipment.RequestedShipment.CustomsClearanceDetail.DutiesPayment.PaymentType = 'SENDER'
        shipment.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.AccountNumber = self.FEDEX_CONFIG_OBJ.account_number
        shipment.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.Contact = ''
        shipment.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.Address.CountryCode = 'IN'
        shipment.RequestedShipment.CustomsClearanceDetail.DocumentContent = 'NON_DOCUMENTS'
        shipment.RequestedShipment.CustomsClearanceDetail.CustomsValue.Currency = 'INR'
        shipment.RequestedShipment.CustomsClearanceDetail.CustomsValue.Amount = float(item['price'])
        shipment.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.Purpose = 'NOT_SOLD'
        shipment.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.TaxesOrMiscellaneousChargeType = None
        shipment.RequestedShipment.CustomsClearanceDetail.Commodities.NumberOfPieces = 1
        shipment.RequestedShipment.CustomsClearanceDetail.Commodities.Description = str(item['name'])
        shipment.RequestedShipment.CustomsClearanceDetail.Commodities.CountryOfManufacture = 'IN'
        shipment.RequestedShipment.CustomsClearanceDetail.Commodities.Weight.Value = float(item['weight'])
        shipment.RequestedShipment.CustomsClearanceDetail.Commodities.Weight.Units = "KG"
        shipment.RequestedShipment.CustomsClearanceDetail.Commodities.Quantity = 1
        shipment.RequestedShipment.CustomsClearanceDetail.Commodities.QuantityUnits = 'EA'
        shipment.RequestedShipment.CustomsClearanceDetail.Commodities.UnitPrice.Currency = 'INR'
        shipment.RequestedShipment.CustomsClearanceDetail.Commodities.UnitPrice.Amount = float(item['price'])
        shipment.RequestedShipment.CustomsClearanceDetail.Commodities.CustomsValue.Currency = 'INR'
        shipment.RequestedShipment.CustomsClearanceDetail.Commodities.CustomsValue.Amount = float(item['price'])
        shipment.RequestedShipment.CustomsClearanceDetail.ExportDetail.B13AFilingOption = 'NOT_REQUIRED'
        shipment.RequestedShipment.CustomsClearanceDetail.ClearanceBrokerage = None
        shipment.RequestedShipment.CustomsClearanceDetail.FreightOnValue = None


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
        shipment.RequestedShipment.LabelSpecification.LabelOrder = None

        # This indicates if the top or bottom of the label comes out of the
        # printer first.
        # BOTTOM_EDGE_OF_TEXT_FIRST or TOP_EDGE_OF_TEXT_FIRST
        shipment.RequestedShipment.LabelSpecification.LabelPrintingOrientation = 'BOTTOM_EDGE_OF_TEXT_FIRST'

        package1_weight = shipment.create_wsdl_object_of_type('Weight')
        # Weight, in pounds.
        package1_weight.Value = float(item['weight'])
        package1_weight.Units = "KG"

        package1 = shipment.create_wsdl_object_of_type('RequestedPackageLineItem')
        package1.SequenceNumber = 1
        package1.PhysicalPackaging = None
        package1.Weight = package1_weight
        # Un-comment this to see the other variables you may set on a package.
        # print package1

        # This adds the RequestedPackageLineItem WSDL object to the shipment. It
        # increments the package count and total weight of the shipment for you.
        shipment.add_package(package1)

        # Check if the shipment is valid
        # shipment.send_validation_request()
        # if shipment.response.HighestSeverity != "SUCCESS":
        #     return {
        #         "status" : shipment.response.HighestSeverity,
        #         "message": shipment.response.Notifications.Message
        #     }

        # Fires off the request, sets the 'response' attribute on the object.
        # print shipment.RequestedShipment
        # print shipment.client
        shipment.send_request()
        # print shipment.response
        if shipment.response.HighestSeverity == "ERROR":
            return {
                "status" : shipment.response.HighestSeverity,
                "message": shipment.response.Notifications.Message
            }
        # Get the label image in ASCII format from the reply. Note the list indices
        # we're using. You'll need to adjust or iterate through these if your shipment
        # has multiple packages.
        ascii_label_data = shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].Label.Parts[0].Image
        # Convert the ASCII data to binary.
        # label_binary_data = binascii.a2b_base64(ascii_label_data)

        return {
            "status": shipment.response.HighestSeverity,
            "tracking_number": shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].TrackingIds[
                0].TrackingNumber,
            "label": ascii_label_data
        }


    @staticmethod
    def get_service_type(selected_type, item_value, is_cod=False):
        if selected_type == 'P' and item_value < 5000 and not is_cod:
            return 'PRIORITY_OVERNIGHT'
        elif selected_type == 'P' and item_value > 5000 or is_cod:
            return 'STANDARD_OVERNIGHT'
        elif selected_type in ('B', 'N', 'S', 'E'):
            return 'FEDEX_EXPRESS_SAVER'
        return False