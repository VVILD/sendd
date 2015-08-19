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
    FEDEX_CONFIG_TEST = FedexConfig(key='Ha8gotyUoTHURYW6',
                                    password='ueU6dTNMxL0uPsJfxadWBhhjW',
                                    account_number='510087640',
                                    meter_number='118685245',
                                    use_test_server=False)
    # Set this to the INFO level to see the response from Fedex printed in stdout.
    logging.basicConfig(level=logging.INFO)

    def __init__(self):
        self.shipment = None

    def create_shipment(self, sender, receiver, item, dropoff_type='REGULAR_PICKUP', service_type='STANDARD_OVERNIGHT'):
        if str(receiver['city']).lower() == 'mumbai':
            FEDEX_CONFIG_OBJ = self.FEDEX_CONFIG_INTRA_MUMBAI
        else:
            FEDEX_CONFIG_OBJ = self.FEDEX_CONFIG_INDIA
        # This is the object that will be handling our tracking request.
        # We're using the FedexConfig object from example_config.py in this dir.
        shipment = FedexProcessShipmentRequest(FEDEX_CONFIG_OBJ)

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
        shipment.RequestedShipment.Shipper.Contact.PersonName = "Sendd"
        # if sender['company']:
        shipment.RequestedShipment.Shipper.Contact.CompanyName = "Sendd"
        shipment.RequestedShipment.Shipper.Contact.PhoneNumber = '8080028081'

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
        if receiver['company']:
            shipment.RequestedShipment.Recipient.Contact.CompanyName = str(receiver['company'])
        shipment.RequestedShipment.Recipient.Contact.PhoneNumber = str(receiver['phone'])

        # Recipient address
        shipment.RequestedShipment.Recipient.Address.StreetLines = [str(receiver['address1']),
                                                                    str(receiver['address2'])]
        shipment.RequestedShipment.Recipient.Address.City = str(receiver['city'])
        state_code = StateCodes.objects.get(subdivision_name=str(receiver['state']))
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
        shipment.RequestedShipment.LabelSpecification.LabelStockType = 'PAPER_8.5X11_TOP_HALF_LABEL'
        shipment.RequestedShipment.LabelSpecification.LabelOrder = None

        # This indicates if the top or bottom of the label comes out of the
        # printer first.
        # BOTTOM_EDGE_OF_TEXT_FIRST or TOP_EDGE_OF_TEXT_FIRST
        shipment.RequestedShipment.LabelSpecification.LabelPrintingOrientation = 'TOP_EDGE_OF_TEXT_FIRST'

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
            OUTBOUND_LABEL = shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].Label.Parts[0].Image
        else:
            OUTBOUND_LABEL = shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].Label.Parts[0].Image
            COD_RETURN_LABEL = None
        shiping_cost = None
        if shipment.response.HighestSeverity == "SUCCESS":
            shiping_cost = shipment.response.CompletedShipmentDetail.ShipmentRating.ShipmentRateDetails[0].TotalNetCharge.Amount

        return {
            "status": shipment.response.HighestSeverity,
            "tracking_number": shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].TrackingIds[
                0].TrackingNumber,
            "OUTBOUND_LABEL": OUTBOUND_LABEL,
            "COD_RETURN_LABEL": COD_RETURN_LABEL,
            "service_type": service_type,
            "account": FEDEX_CONFIG_OBJ.account_number,
            "shipping_cost": shiping_cost
        }


    @staticmethod
    def get_service_type(selected_type, item_value, is_cod=False):
        if selected_type in ('P', 'S', 'N') and item_value < 5000 and not is_cod:
            return 'PRIORITY_OVERNIGHT'
        elif selected_type in ('P', 'S', 'N') and item_value > 5000 or is_cod:
            return 'STANDARD_OVERNIGHT'
        elif selected_type in ('B', 'E'):
            return 'FEDEX_EXPRESS_SAVER'
        return False