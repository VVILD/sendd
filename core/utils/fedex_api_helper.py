import logging
import binascii
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


def create_shipment(sender, receiver, item, FEDEX_CONFIG_OBJ, service_type, sequence_no, package_count, master_tracking_no, reverse):
    shipment = FedexProcessShipmentRequest(FEDEX_CONFIG_OBJ)

    receiver_address = textwrap.wrap(text=str(receiver['address']), width=35)
    if len(receiver_address) > 3:
        raise ValidationError("Address Length > 130 chars")

    shipment.RequestedShipment.DropoffType = "REGULAR_PICKUP"
    shipment.RequestedShipment.ServiceType = str(service_type)
    shipment.RequestedShipment.PackagingType = 'YOUR_PACKAGING'

    if reverse is False:
        if sender['sender_details']['company_name'] is not None:
            # Shipper contact info.
            shipment.RequestedShipment.Shipper.Contact.PersonName = str(sender['sender_details']['company_name'])
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
            shipment.RequestedShipment.Shipper.Address.StateOrProvinceCode = "MH"
            shipment.RequestedShipment.Shipper.Address.PostalCode = "400093"

        shipment.RequestedShipment.Shipper.Address.CountryCode = "IN"

        # Recipient contact info.
        shipment.RequestedShipment.Recipient.Contact.PersonName = str(receiver['name'])

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

    else:
        shipment.RequestedShipment.Shipper.Contact.PersonName = str(sender['sender_details']['contact_person'])
        shipment.RequestedShipment.Shipper.Contact.CompanyName = str(sender['sender_details']['company_name'])
        shipment.RequestedShipment.Shipper.Contact.PhoneNumber = str(sender['sender_details']['phone_office'])
        sender_address = textwrap.wrap(text=str(sender['sender_details']['address']), width=35)
        if len(sender_address) > 3:
            raise ValidationError("Sender Address Length > 130 chars")
        if len(sender_address) > 1:
            shipment.RequestedShipment.Shipper.Address.StreetLines = [sender_address[1:]]
        else:
            shipment.RequestedShipment.Shipper.Address.StreetLines = [sender_address[0]]
        shipment.RequestedShipment.Shipper.Address.City = str(sender['sender_details']['city'])
        state_code = StateCodes.objects.get(country_code='IN', subdivision_name=str(sender['sender_details']['state']))
        shipment.RequestedShipment.Shipper.Address.StateOrProvinceCode = str(state_code.code).split('-')[1]
        shipment.RequestedShipment.Shipper.Address.PostalCode = str(sender['sender_details']['pincode'])
        shipment.RequestedShipment.Shipper.Address.CountryCode = "IN"

        if receiver['company'] is not None:
            # Shipper contact info.
            shipment.RequestedShipment.Recipient.Contact.PersonName = str(receiver['company'])
        else:
            # Shipper contact info.
            shipment.RequestedShipment.Recipient.Contact.PersonName = "Sendd"
        # if sender['company']:
        shipment.RequestedShipment.Recipient.Contact.CompanyName = "C/O: Sendd"
        shipment.RequestedShipment.Recipient.Contact.PhoneNumber = '8080028081'
        if receiver['warehouse'] is not None:
            # Shipper address.
            if receiver['warehouse']['address_line_2'] is not None:
                shipment.RequestedShipment.Recipient.Address.StreetLines = [str(receiver['warehouse']['address_line_1']),
                                                                          str(receiver['warehouse']['address_line_2'])]
            else:
                shipment.RequestedShipment.Recipient.Address.StreetLines = [str(receiver['warehouse']['address_line_1'])]
            shipment.RequestedShipment.Recipient.Address.City = str(receiver['warehouse']['city'])
            state_code = StateCodes.objects.get(country_code='IN', subdivision_name=str(receiver['warehouse']['state']))
            shipment.RequestedShipment.Recipient.Address.StateOrProvinceCode = str(state_code.code).split('-')[1]
            shipment.RequestedShipment.Recipient.Address.PostalCode = str(receiver['warehouse']['pincode'])
        else:
            # Shipper address.
            shipment.RequestedShipment.Recipient.Address.StreetLines = ["107 A-Wing Classique Center, Gundavali",
                                                                      "Andheri East, Mahakali Caves Road"]
            shipment.RequestedShipment.Recipient.Address.City = "Mumbai"
            shipment.RequestedShipment.Recipient.Address.StateOrProvinceCode = "MH"
            shipment.RequestedShipment.Recipient.Address.PostalCode = "400093"

        shipment.RequestedShipment.Recipient.Address.CountryCode = "IN"


    # This is needed to ensure an accurate rate quote with the response.
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
        shipment.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount.Amount = sum(i['price'] for i in item)
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
    if item[0]['is_doc']:
        shipment.RequestedShipment.CustomsClearanceDetail.DocumentContent = 'DOCUMENTS_ONLY'
    else:
        shipment.RequestedShipment.CustomsClearanceDetail.DocumentContent = 'NON_DOCUMENTS'
    shipment.RequestedShipment.CustomsClearanceDetail.CustomsValue.Currency = 'INR'
    shipment.RequestedShipment.CustomsClearanceDetail.CustomsValue.Amount = float(item[0]['price'])
    if sender['is_cod']:
        shipment.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.Purpose = 'SOLD'
    else:
        shipment.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.Purpose = 'NOT_SOLD'
    shipment.RequestedShipment.CustomsClearanceDetail.CommercialInvoice.TaxesOrMiscellaneousChargeType = None
    shipment.RequestedShipment.CustomsClearanceDetail.ExportDetail.B13AFilingOption = 'NOT_REQUIRED'
    shipment.RequestedShipment.CustomsClearanceDetail.ClearanceBrokerage = None
    shipment.RequestedShipment.CustomsClearanceDetail.FreightOnValue = None

    total_weight = 0.0
    for i in item:
        commodity = None
        commodity = shipment.create_wsdl_object_of_type('Commodity')
        commodity.Weight = shipment.create_wsdl_object_of_type('Weight')
        commodity.UnitPrice = shipment.create_wsdl_object_of_type('Money')
        commodity.CustomsValue = shipment.create_wsdl_object_of_type('Money')

        commodity.NumberOfPieces = 1
        commodity.CountryOfManufacture = 'IN'
        commodity.Weight.Units = 'KG'
        commodity.QuantityUnits = 'EA'
        commodity.UnitPrice.Currency = 'INR'
        commodity.CustomsValue.Currency = 'INR'
        commodity.Quantity = 1
        commodity.Description = str(i['name'])
        commodity.Weight.Value = float(i['weight'])
        commodity.UnitPrice.Amount = float(i['price'])
        commodity.CustomsValue.Amount = float(i['price'])
        shipment.RequestedShipment.CustomsClearanceDetail.Commodities.append(commodity)
        total_weight += float(i['weight'])

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

    if master_tracking_no is not None:
        shipment.RequestedShipment.MasterTrackingId = shipment.create_wsdl_object_of_type('TrackingId')
        shipment.RequestedShipment.MasterTrackingId.TrackingIdType = "FEDEX"
        shipment.RequestedShipment.MasterTrackingId.TrackingNumber = master_tracking_no
    else:
        shipment.RequestedShipment.PackageCount = package_count

    shipment.RequestedShipment.ShippingDocumentSpecification.ShippingDocumentTypes = 'COMMERCIAL_INVOICE'
    shipment.RequestedShipment.ShippingDocumentSpecification.CommercialInvoiceDetail = shipment.create_wsdl_object_of_type('CommercialInvoiceDetail')
    shipment.RequestedShipment.ShippingDocumentSpecification.CommercialInvoiceDetail.Format.ImageType = 'PDF'
    shipment.RequestedShipment.ShippingDocumentSpecification.CommercialInvoiceDetail.Format.StockType = 'PAPER_LETTER'

    package1_weight = shipment.create_wsdl_object_of_type('Weight')
    # Weight, in pounds.
    package1_weight.Value = float(item[0]['weight'])
    package1_weight.Units = "KG"

    package1 = shipment.create_wsdl_object_of_type('RequestedPackageLineItem')
    package1.SequenceNumber = sequence_no
    package1.PhysicalPackaging = None
    package1.CustomerReferences = shipment.create_wsdl_object_of_type('CustomerReference')
    package1.CustomerReferences.CustomerReferenceType = 'CUSTOMER_REFERENCE'
    package1.CustomerReferences.Value = 'Bill D/T - Sender'
    package1.Weight = package1_weight

    package1.GroupPackageCount = 1

    shipment.RequestedShipment.TotalWeight.Value = total_weight
    # Un-comment this to see the other variables you may set on a package.
    # print package1

    # This adds the RequestedPackageLineItem WSDL object to the shipment. It
    # increments the package count and total weight of the shipment for you.
    shipment.add_package(package1)

    shipment.send_request()


    if shipment.response.HighestSeverity == "ERROR":
        return {
            "status": shipment.response.HighestSeverity,
            "message": shipment.response.Notifications.Message
        }


    COD_RETURN_LABEL = None

    OUTBOUND_LABEL = shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].Label.Parts[0].Image
    COMMERCIAL_INVOICE = None
    shiping_cost = None
    if sequence_no == package_count:
        COMMERCIAL_INVOICE = shipment.response.CompletedShipmentDetail.ShipmentDocuments[0].Parts[0].Image
        shiping_cost = shipment.response.CompletedShipmentDetail.ShipmentRating.ShipmentRateDetails[0].TotalNetCharge.Amount

        if sender['is_cod']:
            COD_RETURN_LABEL = shipment.response.CompletedShipmentDetail.AssociatedShipments[0].Label.Parts[0].Image

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


def is_oda(sender, receiver, item, FEDEX_CONFIG_OBJ, service_type):

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
    rate_request.RequestedShipment.Shipper.Address.StateOrProvinceCode = "MH"
    rate_request.RequestedShipment.Shipper.Address.PostalCode = "400093"
    rate_request.RequestedShipment.Shipper.Address.CountryCode = "IN"

    # Recipient contact info.
    rate_request.RequestedShipment.Recipient.Contact.PersonName = str(receiver['name'])

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

    rate_request.send_request()

    # RateReplyDetails can contain rates for multiple ServiceTypes if ServiceType was set to None
    status = False
    for service in rate_request.response.RateReplyDetails:
        for detail in service.RatedShipmentDetails:
            for surcharge in detail.ShipmentRateDetail.Surcharges:
                if surcharge.SurchargeType == 'OUT_OF_DELIVERY_AREA':
                    status = True
    return status


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