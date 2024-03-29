import logging
import binascii
# Use the fedex directory included in the downloaded package instead of
# any globally installed versions.
import os
import sys
import textwrap
from django.core.files.base import ContentFile
from core.fedex.services.rate_service import FedexRateServiceRequest
from core.models import StateCodes
from django.core.exceptions import ValidationError
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.fedex.config import FedexConfig
from core.fedex.services.ship_service import FedexProcessShipmentRequest

__author__ = 'vatsalshah'


class FedexLegacy:
    # Set this to the INFO level to see the response from Fedex printed in stdout.
    logging.basicConfig(level=logging.INFO)

    def __init__(self):
        self.shipment = None

    def create_shipment(self, sender, receiver, item, FEDEX_CONFIG_OBJ, service_type):

        # This is the object that will be handling our tracking request.
        # We're using the FedexConfig object from example_config.py in this dir.
        shipment = FedexProcessShipmentRequest(FEDEX_CONFIG_OBJ)

        receiver_address = textwrap.wrap(receiver['address'], 35)
        if len(receiver_address) > 3:
            raise ValidationError("Address Length > 130 chars")

        # This is very generalized, top-level information.
        # REGULAR_PICKUP, REQUEST_COURIER, DROP_BOX, BUSINESS_SERVICE_CENTER or STATION
        shipment.RequestedShipment.DropoffType = "REGULAR_PICKUP"

        # See page 355 in WS_ShipService.pdf for a full list. Here are the common ones:
        # STANDARD_OVERNIGHT, PRIORITY_OVERNIGHT, FEDEX_GROUND, FEDEX_EXPRESS_SAVER
        shipment.RequestedShipment.ServiceType = str(service_type)

        # What kind of package this will be shipped in.
        # FEDEX_BOX, FEDEX_PAK, FEDEX_TUBE, YOUR_PACKAGING
        shipment.RequestedShipment.PackagingType = 'YOUR_PACKAGING'

        if sender['sender_details']['business_name'] is not None:
            # Shipper contact info.
            shipment.RequestedShipment.Shipper.Contact.PersonName = str(sender['sender_details']['business_name'])
        else:
            # Shipper contact info.
            shipment.RequestedShipment.Shipper.Contact.PersonName = "Sendd"
        # if sender['company']:
        shipment.RequestedShipment.Shipper.Contact.CompanyName = "C/O: Sendd"
        shipment.RequestedShipment.Shipper.Contact.PhoneNumber = '8080028081'
        if sender['warehouse'] is not None:
            # Shipper address.
            if sender['warehouse']['address_line_2'] is not None:
                shipment.RequestedShipment.Shipper.Address.StreetLines = [str(sender['warehouse']['address_line_1']),
                                                                          str(sender['warehouse']['address_line_2'])]
            else:
                shipment.RequestedShipment.Shipper.Address.StreetLines = [str(sender['warehouse']['address_line_1'])]
            shipment.RequestedShipment.Shipper.Address.City = str(sender['warehouse']['city'])
            state_code = StateCodes.objects.get(country_code='IN', subdivision_name=str(sender['warehouse']['state']))
            shipment.RequestedShipment.Shipper.Address.StateOrProvinceCode = str(state_code.code).split('-')[1]
            shipment.RequestedShipment.Shipper.Address.PostalCode = str(sender['warehouse']['pincode'])
        else:
            # Shipper address.
            shipment.RequestedShipment.Shipper.Address.StreetLines = ["107 A-Wing Classique Center, Gundavali",
                                                                      "Andheri East, Mahakali Caves Road"]
            shipment.RequestedShipment.Shipper.Address.City = "Mumbai"
            # state_code = StateCodes.objects.get(subdivision_name=str(sender['state']))
            shipment.RequestedShipment.Shipper.Address.StateOrProvinceCode = "MH"
            shipment.RequestedShipment.Shipper.Address.PostalCode = "400093"

        shipment.RequestedShipment.Shipper.Address.CountryCode = "IN"
        # shipment.RequestedShipment.Shipper.Address.Residential = not sender['is_business']

        # Recipient contact info.
        shipment.RequestedShipment.Recipient.Contact.PersonName = str(receiver['name'])
        # if receiver['company']:
        #     shipment.RequestedShipment.Recipient.Contact.CompanyName = str(receiver['company'])
        if len(receiver_address) > 1:
            shipment.RequestedShipment.Recipient.Contact.CompanyName = str(receiver_address[0])
        shipment.RequestedShipment.Recipient.Contact.PhoneNumber = str(receiver['phone'])

        # Recipient address
        if len(receiver_address) > 1:
            shipment.RequestedShipment.Recipient.Address.StreetLines = [receiver_address[1:]]
        else:
            shipment.RequestedShipment.Recipient.Address.StreetLines = [receiver_address[0]]
        shipment.RequestedShipment.Recipient.Address.City = str(receiver['city'])
        state_code = StateCodes.objects.get(country_code='IN', subdivision_name=str(receiver['state']))
        shipment.RequestedShipment.Recipient.Address.StateOrProvinceCode = str(state_code.code).split('-')[1]
        shipment.RequestedShipment.Recipient.Address.PostalCode = str(receiver['pincode'])
        shipment.RequestedShipment.Recipient.Address.CountryCode = str(receiver['country_code'])
        # This is needed to ensure an accurate rate quote with the response.
        # shipment.RequestedShipment.Recipient.Address.Residential = not receiver['is_business']
        shipment.RequestedShipment.EdtRequestType = None

        shipment.RequestedShipment.ShippingChargesPayment.Payor.ResponsibleParty.AccountNumber = FEDEX_CONFIG_OBJ.account_number

        if sender['is_cod']:
            shipment.RequestedShipment.SpecialServicesRequested = shipment.create_wsdl_object_of_type(
                'PackageSpecialServicesRequested')
            shipment.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = 'COD'
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail = shipment.create_wsdl_object_of_type(
                'CodDetail')
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount = shipment.create_wsdl_object_of_type(
                'Money')
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount.Currency = 'INR'
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount.Amount = float(
                item['price'])
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.CollectionType = 'CASH'
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress = shipment.create_wsdl_object_of_type(
                'Party')
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact = shipment.create_wsdl_object_of_type(
                'Contact')
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address = shipment.create_wsdl_object_of_type(
                'Address')
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact.PersonName = 'Sumeet Wadhwa'
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact.CompanyName = 'Crazymind Technologies Pvt. Ltd.'
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact.PhoneNumber = '8879475752'
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.StreetLines = [
                '303, Building no 5, Lake Heights, Adi Shankaracharya marg', ', Rambaug, IIT-Mumbai, Powai']
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.City = 'Mumbai'
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.StateOrProvinceCode = 'MH'
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.PostalCode = '400076'
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.CountryCode = 'IN'
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.CountryName = 'INDIA'
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.RemitToName = 'Crazymind Technologies Pvt. Ltd.'
            shipment.RequestedShipment.SpecialServicesRequested.CodDetail.ReferenceIndicator = None

        shipment.RequestedShipment.CustomsClearanceDetail.DutiesPayment.PaymentType = 'SENDER'
        shipment.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.AccountNumber = FEDEX_CONFIG_OBJ.account_number
        shipment.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.Contact = ''
        shipment.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.Address.CountryCode = 'IN'
        shipment.RequestedShipment.CustomsClearanceDetail.DocumentContent = 'NON_DOCUMENTS'
        shipment.RequestedShipment.CustomsClearanceDetail.CustomsValue.Currency = 'INR'
        shipment.RequestedShipment.CustomsClearanceDetail.CustomsValue.Amount = float(item['price'])
        if sender['is_cod']:
            shipment.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.Purpose = 'SOLD'
        else:
            shipment.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.Purpose = 'NOT_SOLD'
        shipment.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.TaxesOrMiscellaneousChargeType = None

        shipment.RequestedShipment.CustomsClearanceDetail.Commodities = shipment.create_wsdl_object_of_type('Commodity')
        shipment.RequestedShipment.CustomsClearanceDetail.Commodities.Weight = shipment.create_wsdl_object_of_type('Weight')
        shipment.RequestedShipment.CustomsClearanceDetail.Commodities.UnitPrice = shipment.create_wsdl_object_of_type('Money')
        shipment.RequestedShipment.CustomsClearanceDetail.Commodities.CustomsValue = shipment.create_wsdl_object_of_type('Money')

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

        shipment.RequestedShipment.PackageCount = 1
        # Specifies the label type to be returned.
        # LABEL_DATA_ONLY or COMMON2D
        shipment.RequestedShipment.LabelSpecification.LabelFormatType = 'COMMON2D'

        # Specifies which format the label file will be sent to you in.
        # DPL, EPL2, PDF, PNG, ZPLII
        shipment.RequestedShipment.LabelSpecification.ImageType = 'PDF'

        # To use doctab stocks, you must change ImageType above to one of the
        # label printer formats (ZPLII, EPL2, DPL).
        # See documentation for paper types, there quite a few.
        shipment.RequestedShipment.LabelSpecification.LabelStockType = 'PAPER_8.5X11_TOP_HALF_LABEL'
        shipment.RequestedShipment.LabelSpecification.LabelOrder = None

        # This indicates if the top or bottom of the label comes out of the
        # printer first.
        # BOTTOM_EDGE_OF_TEXT_FIRST or TOP_EDGE_OF_TEXT_FIRST
        shipment.RequestedShipment.LabelSpecification.LabelPrintingOrientation = 'TOP_EDGE_OF_TEXT_FIRST'

        shipment.RequestedShipment.ShippingDocumentSpecification.ShippingDocumentTypes = 'COMMERCIAL_INVOICE'
        shipment.RequestedShipment.ShippingDocumentSpecification.CommercialInvoiceDetail = shipment.create_wsdl_object_of_type('CommercialInvoiceDetail')
        shipment.RequestedShipment.ShippingDocumentSpecification.CommercialInvoiceDetail.Format.ImageType = 'PDF'
        shipment.RequestedShipment.ShippingDocumentSpecification.CommercialInvoiceDetail.Format.StockType = 'PAPER_LETTER'

        package1_weight = shipment.create_wsdl_object_of_type('Weight')
        # Weight, in pounds.
        package1_weight.Value = float(item['weight'])
        package1_weight.Units = "KG"

        package1 = shipment.create_wsdl_object_of_type('RequestedPackageLineItem')
        package1.SequenceNumber = 1
        package1.PhysicalPackaging = None
        package1.CustomerReferences = shipment.create_wsdl_object_of_type('CustomerReference')
        package1.CustomerReferences.CustomerReferenceType = 'CUSTOMER_REFERENCE'
        package1.CustomerReferences.Value = 'Bill D/T - Sender'
        package1.Weight = package1_weight

        shipment.RequestedShipment.TotalWeight.Value = float(item['weight'])
        # Un-comment this to see the other variables you may set on a package.
        # print package1

        # This adds the RequestedPackageLineItem WSDL object to the shipment. It
        # increments the package count and total weight of the shipment for you.
        shipment.add_package(package1)

        # Check if the shipment is valid
        # shipment.send_validation_request()
        # if shipment.response.HighestSeverity != "SUCCESS":
        # return {
        # "status" : shipment.response.HighestSeverity,
        # "message": shipment.response.Notifications.Message
        #     }

        # Fires off the request, sets the 'response' attribute on the object.
        # print shipment.RequestedShipment
        # print shipment.client
        shipment.send_request()
        # print shipment.response
        # print shipment.client.last_sent()

        if shipment.response.HighestSeverity == "ERROR":
            return {
                "status": shipment.response.HighestSeverity,
                "message": shipment.response.Notifications.Message
            }
        # Get the label image in ASCII format from the reply. Note the list indices
        # we're using. You'll need to adjust or iterate through these if your shipment
        # has multiple packages.
        # ascii_label_data = shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].Label.Parts[0].Image
        # Convert the ASCII data to binary.
        # label_binary_data = binascii.a2b_base64(ascii_label_data)
        if sender['is_cod']:
            COD_RETURN_LABEL = shipment.response.CompletedShipmentDetail.AssociatedShipments[0].Label.Parts[0].Image
        else:
            COD_RETURN_LABEL = None
        OUTBOUND_LABEL = shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].Label.Parts[0].Image
        COMMERCIAL_INVOICE = shipment.response.CompletedShipmentDetail.ShipmentDocuments[0].Parts[0].Image
        shiping_cost = None
        if shipment.response.HighestSeverity == "SUCCESS":
            shiping_cost = shipment.response.CompletedShipmentDetail.ShipmentRating.ShipmentRateDetails[0].TotalNetCharge.Amount

        return {
            "status": shipment.response.HighestSeverity,
            "tracking_number": shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].TrackingIds[
                0].TrackingNumber,
            "OUTBOUND_LABEL": OUTBOUND_LABEL,
            "COD_RETURN_LABEL": COD_RETURN_LABEL,
            "COMMERCIAL_INVOICE": COMMERCIAL_INVOICE,
            "service_type": service_type,
            "account": FEDEX_CONFIG_OBJ.account_number,
            "shipping_cost": shiping_cost
        }
    
    def is_oda(self, sender, receiver, item, FEDEX_CONFIG_OBJ, service_type):

        # This is the object that will be handling our tracking request.
        # We're using the FedexConfig object from example_config.py in this dir.
        rate_request = FedexRateServiceRequest(FEDEX_CONFIG_OBJ)


        receiver_address = textwrap.wrap(receiver['address'], 35)
        if len(receiver_address) > 3:
            raise ValidationError("Address Length > 130 chars")


        # This is very generalized, top-level information.
        # REGULAR_PICKUP, REQUEST_COURIER, DROP_BOX, BUSINESS_SERVICE_CENTER or STATION
        rate_request.RequestedShipment.DropoffType = "REGULAR_PICKUP"

        # See page 355 in WS_ShipService.pdf for a full list. Here are the common ones:
        # STANDARD_OVERNIGHT, PRIORITY_OVERNIGHT, FEDEX_GROUND, FEDEX_EXPRESS_SAVER
        rate_request.RequestedShipment.ServiceType = str(service_type)

        # What kind of package this will be shipped in.
        # FEDEX_BOX, FEDEX_PAK, FEDEX_TUBE, YOUR_PACKAGING
        rate_request.RequestedShipment.PackagingType = 'YOUR_PACKAGING'

        # Shipper contact info.
        rate_request.RequestedShipment.Shipper.Contact.PersonName = "Sendd"
        # if sender['company']:
        rate_request.RequestedShipment.Shipper.Contact.CompanyName = "Sendd"
        rate_request.RequestedShipment.Shipper.Contact.PhoneNumber = '8080028081'

        # Shipper address.
        rate_request.RequestedShipment.Shipper.Address.StreetLines = ["107 A-Wing Classique Center, Gundavali",
                                                                  "Andheri East, Mahakali Caves Road"]
        rate_request.RequestedShipment.Shipper.Address.City = "Mumbai"
        # state_code = StateCodes.objects.get(subdivision_name=str(sender['state']))
        rate_request.RequestedShipment.Shipper.Address.StateOrProvinceCode = "MH"
        rate_request.RequestedShipment.Shipper.Address.PostalCode = "400093"
        rate_request.RequestedShipment.Shipper.Address.CountryCode = "IN"
        # rate_request.RequestedShipment.Shipper.Address.Residential = not sender['is_business']

        # Recipient contact info.
        rate_request.RequestedShipment.Recipient.Contact.PersonName = str(receiver['name'])
        # if receiver['company']:
        #     rate_request.RequestedShipment.Recipient.Contact.CompanyName = str(receiver['company'])
        if len(receiver_address) > 1:
            rate_request.RequestedShipment.Recipient.Contact.CompanyName = str(receiver_address[0])
        rate_request.RequestedShipment.Recipient.Contact.PhoneNumber = str(receiver['phone'])

        # Recipient address
        if len(receiver_address) > 1:
            rate_request.RequestedShipment.Recipient.Address.StreetLines = [receiver_address[1:]]
        else:
            rate_request.RequestedShipment.Recipient.Address.StreetLines = [receiver_address[0]]
        rate_request.RequestedShipment.Recipient.Address.City = str(receiver['city'])
        state_code = StateCodes.objects.get(country_code='IN', subdivision_name=str(receiver['state']))
        rate_request.RequestedShipment.Recipient.Address.StateOrProvinceCode = str(state_code.code).split('-')[1]
        rate_request.RequestedShipment.Recipient.Address.PostalCode = str(receiver['pincode'])
        rate_request.RequestedShipment.Recipient.Address.CountryCode = str(receiver['country_code'])
        # This is needed to ensure an accurate rate quote with the response.
        # rate_request.RequestedShipment.Recipient.Address.Residential = not receiver['is_business']
        rate_request.RequestedShipment.EdtRequestType = None

        rate_request.RequestedShipment.ShippingChargesPayment.Payor.ResponsibleParty.AccountNumber = FEDEX_CONFIG_OBJ.account_number

        if sender['is_cod']:
            rate_request.RequestedShipment.SpecialServicesRequested = rate_request.create_wsdl_object_of_type(
                'PackageSpecialServicesRequested')
            rate_request.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = 'COD'
            rate_request.RequestedShipment.SpecialServicesRequested.CodDetail = rate_request.create_wsdl_object_of_type(
                'CodDetail')
            rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount = rate_request.create_wsdl_object_of_type(
                'Money')
            rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount.Currency = 'INR'
            rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount.Amount = float(
                item['price'])
            rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CollectionType = 'CASH'
            rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress = rate_request.create_wsdl_object_of_type(
                'Party')
            rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact = rate_request.create_wsdl_object_of_type(
                'Contact')
            rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address = rate_request.create_wsdl_object_of_type(
                'Address')
            rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact.PersonName = 'Sumeet Wadhwa'
            rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact.CompanyName = 'Crazymind Technologies Pvt. Ltd.'
            rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Contact.PhoneNumber = '8879475752'
            rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.FinancialInstitutionContactAndAddress.Address.StreetLines = [
                '303, Building no 5, Lake Heights, Adi Shankaracharya marg', ', Rambaug, IIT-Mumbai, Powai']
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
        rate_request.RequestedShipment.CustomsClearanceDetail.CustomsValue.Amount = float(item['price'])
        if sender['is_cod']:
            rate_request.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.Purpose = 'SOLD'
        else:
            rate_request.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.Purpose = 'NOT_SOLD'
        rate_request.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.TaxesOrMiscellaneousChargeType = None
        rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.NumberOfPieces = 1
        rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.Description = str(item['name'])
        rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.CountryOfManufacture = 'IN'
        rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.Weight.Value = float(item['weight'])
        rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.Weight.Units = "KG"
        rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.Quantity = 1
        rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.QuantityUnits = 'EA'
        rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.UnitPrice.Currency = 'INR'
        rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.UnitPrice.Amount = float(item['price'])
        rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.CustomsValue.Currency = 'INR'
        rate_request.RequestedShipment.CustomsClearanceDetail.Commodities.CustomsValue.Amount = float(item['price'])
        rate_request.RequestedShipment.CustomsClearanceDetail.ExportDetail.B13AFilingOption = 'NOT_REQUIRED'
        rate_request.RequestedShipment.CustomsClearanceDetail.ClearanceBrokerage = None
        rate_request.RequestedShipment.CustomsClearanceDetail.FreightOnValue = None


        # Specifies the label type to be returned.
        # LABEL_DATA_ONLY or COMMON2D
        # rate_request.RequestedShipment.LabelSpecification.LabelFormatType = 'COMMON2D'
        #
        # # Specifies which format the label file will be sent to you in.
        # # DPL, EPL2, PDF, PNG, ZPLII
        # rate_request.RequestedShipment.LabelSpecification.ImageType = 'PDF'
        #
        # # To use doctab stocks, you must change ImageType above to one of the
        # # label printer formats (ZPLII, EPL2, DPL).
        # # See documentation for paper types, there quite a few.
        # rate_request.RequestedShipment.LabelSpecification.LabelStockType = 'PAPER_8.5X11_TOP_HALF_LABEL'
        # rate_request.RequestedShipment.LabelSpecification.LabelOrder = None
        #
        # # This indicates if the top or bottom of the label comes out of the
        # # printer first.
        # # BOTTOM_EDGE_OF_TEXT_FIRST or TOP_EDGE_OF_TEXT_FIRST
        # rate_request.RequestedShipment.LabelSpecification.LabelPrintingOrientation = 'TOP_EDGE_OF_TEXT_FIRST'

        package1_weight = rate_request.create_wsdl_object_of_type('Weight')
        # Weight, in pounds.
        package1_weight.Value = float(item['weight'])
        package1_weight.Units = "KG"

        package1 = rate_request.create_wsdl_object_of_type('RequestedPackageLineItem')
        package1.SequenceNumber = 1
        package1.PhysicalPackaging = None
        package1.CustomerReferences = rate_request.create_wsdl_object_of_type('CustomerReference')
        package1.CustomerReferences.CustomerReferenceType = 'CUSTOMER_REFERENCE'
        package1.CustomerReferences.Value = 'Bill D/T - Sender'
        package1.Weight = package1_weight
        # Un-comment this to see the other variables you may set on a package.
        # print package1
        package1.GroupPackageCount = 1
        # This adds the RequestedPackageLineItem WSDL object to the rate_request. It
        # increments the package count and total weight of the rate_request for you.
        rate_request.add_package(package1)

        # Check if the rate_request is valid
        # rate_request.send_validation_request()
        # if rate_request.response.HighestSeverity != "SUCCESS":
        # return {
        # "status" : rate_request.response.HighestSeverity,
        # "message": rate_request.response.Notifications.Message
        #     }

        # Fires off the request, sets the 'response' attribute on the object.
        # print rate_request.RequestedShipment
        # print rate_request.client
        rate_request.send_request()
        # print rate_request.response
        # print rate_request.client.last_sent()

        # RateReplyDetails can contain rates for multiple ServiceTypes if ServiceType was set to None
        status = False
        for service in rate_request.response.RateReplyDetails:
            for detail in service.RatedShipmentDetails:
                for surcharge in detail.ShipmentRateDetail.Surcharges:
                    if surcharge.SurchargeType == 'OUT_OF_DELIVERY_AREA':
                        status = True
        return status

    @staticmethod
    def get_service_type(selected_type, item_value, item_weight, receiver_city, is_cod=False):
        FEDEX_CONFIG_INTRA_MUMBAI = FedexConfig(key='FRmcajHEPfMUjNmC',
                                            password='fY5ZwylNGYFXAgNoChYYYSojG',
                                            account_number='678650382',
                                            meter_number='108284351',
                                            use_test_server=False)
        FEDEX_CONFIG_INDIA = FedexConfig(key='jFdC6SAqFS9vz7gY',
                                         password='6bxCaeVdszjUo2iHw5R3tbrBu',
                                         account_number='677853204',
                                         meter_number='108284345',
                                         use_test_server=False)
        # FEDEX_CONFIG_TEST = FedexConfig(key='Ha8gotyUoTHURYW6',
        #                                 password='ueU6dTNMxL0uPsJfxadWBhhjW',
        #                                 account_number='510087640',
        #                                 meter_number='118685245',
        #                                 use_test_server=False)
        if str(receiver_city).lower() == 'mumbai':
            if item_weight <= 0.5 and not is_cod and item_value <= 5000:
                return 'PRIORITY_OVERNIGHT', FEDEX_CONFIG_INTRA_MUMBAI
            elif item_weight <= 0.5 and (is_cod or item_value > 5000):
                return 'STANDARD_OVERNIGHT', FEDEX_CONFIG_INDIA
            elif item_weight <= 1.0 and not is_cod and item_value <= 5000:
                return 'PRIORITY_OVERNIGHT', FEDEX_CONFIG_INTRA_MUMBAI
            elif item_weight <= 1.0 and (is_cod or item_value > 5000):
                return 'STANDARD_OVERNIGHT', FEDEX_CONFIG_INTRA_MUMBAI
            elif item_weight <= 3.0:
                return 'FEDEX_EXPRESS_SAVER', FEDEX_CONFIG_INDIA
            else:
                return 'FEDEX_EXPRESS_SAVER', FEDEX_CONFIG_INTRA_MUMBAI
        elif selected_type in ('P', 'S', 'N'):
            if is_cod or item_value > 5000 or item_weight > 31:
                return 'STANDARD_OVERNIGHT', FEDEX_CONFIG_INDIA
            else:
                return 'PRIORITY_OVERNIGHT', FEDEX_CONFIG_INDIA
        else:
            if item_weight <= 3.0:
                return 'FEDEX_EXPRESS_SAVER', FEDEX_CONFIG_INDIA
            else:
                return 'FEDEX_EXPRESS_SAVER', FEDEX_CONFIG_INTRA_MUMBAI