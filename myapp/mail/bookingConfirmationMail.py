import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Set sender and receiver of the mail here
sender = "order@sendd.co"
receiver = "sargun@sendd.co"

# Authentication information for sending mail through third party SMTP server
SMTP_username = "kante@sendd.co"
SMTP_password = "cBFFa7xOxEe6b5RfJBTJig"

# Set values for contents of mail here
trackingID = "B134801Q28"
senderName = "Ankit Kante"
senderContact = "8588869761"
pickupAddress = "MDX 62,New Indira Nagar,Neemuch(M.P.)-458441"
pickupTime = "23-07-2015 10:30AM"
bookingTime = "21-07-2015 8:20PM"
recipientName = "Rohan Kumar"
recipientContact = "8588869512"
recipientAddress = "307,Powai Plaza,Mumbai(MH) - 400076"

# If no item name is available set it as ""
itemName = ""
if itemName!="":
	itemHTML = """<strong>Item: </strong>"""+itemName+"""<br />"""
else:
	itemHTML = ""

# If no image URL is available then set it as ""
itemImageURL = "https://d3k81ch9hvuctc.cloudfront.net/company/fG5Ccz/images/ebee834e-4bdc-4c76-ba33-a999a293fa2c.jpeg"
if itemImageURL != "":

	imageHTML =""" <td valign="top" class="kmTextContent" style='border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;color:#222;font-family:"Helvetica Neue", Arial;font-size:14px;line-height:130%;text-align:left;border-right:none;border-bottom:none;text-align:left;width:50%;border-top-style:none;padding-bottom:4px;padding-right:0px;padding-left:0px;padding-top:4px;border-top-color:#d9d9d9;border-top-width:1px;'>
<table align="left" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tr><td class="kmImageContent" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;padding:0;padding-top:0px;padding-bottom:0;padding-left:9px;padding-right:9px;">
<img align="left" alt="" class="kmImage" src="""+itemImageURL+""" width="264" style="border:0;height:auto;line-height:100%;outline:none;text-decoration:none;padding-bottom:0;display:inline;vertical-align:bottom;margin-right:0;max-width:2592px;" /></td></tr></table></td>""";	

else:
	imageHTML=""


# Set this for HTML mailing. Code sample taken from https://docs.python.org/2/library/email-examples.html
msg = MIMEMultipart('alternative')
msg['Subject'] = "Link"
msg['From'] = sender
msg['To'] = receiver

# If HTML is not loaded, this text will be shown
text = "Tracking ID: "+trackingID+"\n\nBooking Details:\nItem: "+itemName+"Name: "+senderName+"\nContact: "+senderContact+\
"\nPickup Address: "+pickupAddress+"\nPickup Time: "+pickupTime+"\nBooking Time: "+bookingTime+"\n\nRecipient Details:"+\
"\nName: "+recipientName+"\nContact: "+recipientContact+"\nAddress: "+recipientAddress

# Mail Body HTML
html = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title></title>

<style type="text/css">@media only screen and (max-width:480px){body,table,td,p,a,li,blockquote{-webkit-text-size-adjust:none !important}body{width:100% !important;min-width:100% !important}td[id=bodyCell]{padding:10px !important}table.kmMobileHide{display:none !important}table[class=kmTextContentContainer]{width:100% !important}table[class=kmBoxedTextContentContainer]{width:100% !important}td[class=kmImageContent]{padding-left:0 !important;padding-right:0 !important}img[class=kmImage]{width:100% !important}td.kmMobileStretch{padding-left:0 !important;padding-right:0 !important}table[class=kmSplitContentLeftContentContainer],table[class=kmSplitContentRightContentContainer],table[class=kmColumnContainer],td[class=kmVerticalButtonBarContentOuter] table[class=kmButtonBarContent],td[class=kmVerticalButtonCollectionContentOuter] table[class=kmButtonCollectionContent],table[class=kmVerticalButton],table[class=kmVerticalButtonContent]{width:100% !important}td[class=kmButtonCollectionInner]{padding-left:9px !important;padding-right:9px !important;padding-top:9px !important;padding-bottom:0 !important;background-color:transparent !important}td[class=kmVerticalButtonIconContent],td[class=kmVerticalButtonTextContent],td[class=kmVerticalButtonContentOuter]{padding-left:0 !important;padding-right:0 !important;padding-bottom:9px !important}table[class=kmSplitContentLeftContentContainer] td[class=kmTextContent],table[class=kmSplitContentRightContentContainer] td[class=kmTextContent],table[class=kmColumnContainer] td[class=kmTextContent],table[class=kmSplitContentLeftContentContainer] td[class=kmImageContent],table[class=kmSplitContentRightContentContainer] td[class=kmImageContent]{padding-top:9px !important}td[class="rowContainer kmFloatLeft"],td[class="rowContainer kmFloatLeft firstColumn"],td[class="rowContainer kmFloatLeft lastColumn"]{float:left;clear:both;width:100% !important}table[id=templateContainer],table[class=templateRow]{max-width:600px !important;width:100% !important}h1{font-size:40px !important;line-height:130% !important}h2{font-size:32px !important;line-height:130% !important}h3{font-size:24px !important;line-height:130% !important}h4{font-size:18px !important;line-height:130% !important}td[class=kmTextContent]{font-size:14px !important;line-height:130% !important}td[class=kmTextBlockInner] td[class=kmTextContent]{padding-right:18px !important;padding-left:18px !important}table[class="kmTableBlock kmTableMobile"] td[class=kmTableBlockInner]{padding-left:9px !important;padding-right:9px !important}table[class="kmTableBlock kmTableMobile"] td[class=kmTableBlockInner] [class=kmTextContent]{font-size:14px !important;line-height:130% !important;padding-left:4px !important;padding-right:4px !important}}</style>
</head>
<body style="margin:0;padding:0;background-color:#eee">
<center>
<table align="center" border="0" cellpadding="0" cellspacing="0" id="bodyTable" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;padding:0;background-color:#eee;height:100%;margin:0;width:100%">
<tbody>
<tr>
<td align="center" id="bodyCell" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;padding-top:50px;padding-left:20px;padding-bottom:20px;padding-right:20px;border-top:0;height:100%;margin:0;width:100%">
<table border="0" cellpadding="0" cellspacing="0" id="templateContainer" width="600" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;border:0 none #aaa;background-color:#fff;border-radius:0">
<tbody>
<tr>
<td id="templateContainerInner" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;padding:0">
<table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tr>
<td align="center" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<table border="0" cellpadding="0" cellspacing="0" class="templateRow" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody>
<tr>
<td class="rowContainer kmFloatLeft" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<table border="0" cellpadding="0" cellspacing="0" class="kmImageBlock" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody class="kmImageBlockOuter">
<tr>
<td class="kmImageBlockInner" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;padding:9px;" valign="top">
<table align="left" border="0" cellpadding="0" cellspacing="0" class="kmImageContentContainer" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody>
<tr>
<td class="kmImageContent" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;padding:0;padding-top:0px;padding-bottom:0;padding-left:9px;padding-right:9px;text-align: center;">
<img align="center" alt="" class="kmImage" src="https://d3k81ch9hvuctc.cloudfront.net/company/fG5Ccz/images/11a85d28-a32c-4ceb-a8fb-fcfde821b28b.png" width="211" style="border:0;height:auto;line-height:100%;outline:none;text-decoration:none;padding-bottom:0;display:inline;vertical-align:bottom;max-width:211px;" />
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
<tr>
<td align="center" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<table border="0" cellpadding="0" cellspacing="0" class="templateRow" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody>
<tr>
<td class="rowContainer kmFloatLeft" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<table border="0" cellpadding="0" cellspacing="0" class="kmTextBlock" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody class="kmTextBlockOuter">
<tr>
<td class="kmTextBlockInner" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;">
<table align="left" border="0" cellpadding="0" cellspacing="0" class="kmTextContentContainer" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody>
<tr>
<td class="kmTextContent" valign="top" style='border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;color:#222;font-family:"Helvetica Neue", Arial;font-size:14px;line-height:130%;text-align:left;padding-top:9px;padding-bottom:9px;padding-left:18px;padding-right:18px;'>
<p style="margin:0;padding-bottom:1em;text-align: center;"><span style="font-family:comic sans ms,cursive;"><strong><span style="font-size:20px;">Sit back and Relax !</span></strong></span></p>
<p style="margin:0;padding-bottom:1em;text-align: center;">You order has been confirmed.</p>
<p style="margin:0;padding-bottom:0;text-align: center;"><span style="font-family: arial, sans-serif; font-size: 12.8000001907349px; line-height: normal;">Our Pickup representative will contact you as per your scheduled pickup time.</span></p>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
<table border="0" cellpadding="0" cellspacing="0" class="kmTextBlock" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody class="kmTextBlockOuter">
<tr>
<td class="kmTextBlockInner" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;">
<table align="left" border="0" cellpadding="0" cellspacing="0" class="kmTextContentContainer" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody>
<tr>
<td class="kmTextContent" valign="top" style='border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;color:#222;font-family:"Helvetica Neue", Arial;font-size:14px;line-height:130%;text-align:left;padding-top:25px;padding-bottom:9px;padding-left:18px;padding-right:18px;'>
<span style="font-size:20px;"><strong>Tracking ID:</strong>"""+trackingID+"""</span>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
<table border="0" cellpadding="0" cellspacing="0" class="kmTableBlock kmTableMobile" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody class="kmTableBlockOuter">
<tr>
<td class="kmTableBlockInner" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;padding-top:9px;padding-bottom:9px;padding-left:18px;padding-right:18px;">
<table align="left" border="0" cellpadding="0" cellspacing="0" class="kmTable" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;">
<thead>
<tr>
<th valign="top" class="kmTextContent" style='color:#222;font-family:"Helvetica Neue", Arial;font-size:14px;line-height:130%;text-align:left;text-align:left;padding-top:4px;font-weight:bold;padding-right:0px;padding-left:0px;padding-bottom:4px;'>
</th>
<th valign="top" class="kmTextContent" style='color:#222;font-family:"Helvetica Neue", Arial;font-size:14px;line-height:130%;text-align:left;text-align:left;width:50%;padding-top:4px;font-weight:bold;padding-right:0px;padding-left:0px;padding-bottom:4px;'>
</th>
</tr>
</thead>
<tbody>
<tr class="kmTableRow">
<td valign="top" class="kmTextContent" style='border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;color:#222;font-family:"Helvetica Neue", Arial;font-size:14px;line-height:130%;text-align:left;border-bottom:none;text-align:left;;border-top-style:none;padding-bottom:4px;padding-right:0px;padding-left:0px;padding-top:4px;border-top-color:#d9d9d9;border-top-width:1px;'>
<h3 style='color:#222;display:block;font-family:"Helvetica Neue", Arial;font-size:24px;font-style:normal;font-weight:bold;line-height:110%;letter-spacing:normal;margin:0;margin-bottom:12px;text-align:left'><strong></strong>Booking Details:</h3>
<p style="margin:0;padding-bottom:0">"""+itemHTML+"""
<strong>Name:</strong> """+senderName+"""<br />
<strong>Contact:</strong> """+senderContact+"""<br />
<strong>Pickup&nbsp;Address:&nbsp;</strong>"""+pickupAddress+"""<br />
<strong>Pickup Time:&nbsp;</strong>"""+pickupTime+"""<br />
<strong>Booking Time: </strong>"""+bookingTime+"""</p>
</td>
"""+imageHTML+"""
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
<table border="0" cellpadding="0" cellspacing="0" class="kmTextBlock" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody class="kmTextBlockOuter">
<tr>
<td class="kmTextBlockInner" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;">
<table align="left" border="0" cellpadding="0" cellspacing="0" class="kmTextContentContainer" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody>
<tr>
<td class="kmTextContent" valign="top" style='border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;color:#222;font-family:"Helvetica Neue", Arial;font-size:14px;line-height:130%;text-align:left;padding-top:9px;padding-bottom:18px;padding-left:18px;padding-right:18px;'>
<h3 style='color:#222;display:block;font-family:"Helvetica Neue", Arial;font-size:24px;font-style:normal;font-weight:bold;line-height:110%;letter-spacing:normal;margin:0;margin-bottom:12px;text-align:left'>Recipient Details:</h3>
<p style="margin:0;padding-bottom:1em"><strong>Name:</strong> """+recipientName+"""<br />
<strong>Contact:&nbsp;</strong>"""+recipientContact+"""<br />
<strong>Address:&nbsp;</strong>"""+recipientAddress+"""</p>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
<table border="0" cellpadding="0" cellspacing="0" width="100%" class="kmButtonBlock" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody class="kmButtonBlockOuter">
<tr>
<td valign="top" align="center" class="kmButtonBlockInner" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;padding:9px 18px;">
<table border="0" cellpadding="0" cellspacing="0" width="" class="kmButtonContentContainer" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;border-top-left-radius:5px;border-top-right-radius:5px;border-bottom-right-radius:5px;border-bottom-left-radius:5px;background-color:#999;background-color:#337AB7;border-radius:5px;">
<tbody>
<tr>
<td align="center" valign="middle" class="kmButtonContent" style='border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;color:white;font-family:"Helvetica Neue", Arial;font-size:16px;padding:15px;padding-top:15px;padding-bottom:15px;padding-left:15px;padding-right:15px;color:#ffffff;font-weight:bold;font-size:16px;font-family:"Helvetica Neue", Arial;'>
<a class="kmButton" title="" href="http://sendd.co/track.html?trackingID="""+trackingID+"""" target="_self" style='word-wrap:break-word;font-weight:normal;letter-spacing:-0.5px;line-height:100%;text-align:center;text-decoration:underline;color:#15C;font-family:"Helvetica Neue", Arial;font-size:16px;text-decoration:initial;color:#ffffff;font-weight:bold;font-size:16px;font-family:"Helvetica Neue", Arial;padding-top:0;padding-bottom:0;'>Track Order</a>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
<table border="0" cellpadding="0" cellspacing="0" width="100%" class="kmDividerBlock" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody class="kmDividerBlockOuter">
<tr>
<td class="kmDividerBlockInner" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;padding-top:18px;padding-bottom:18px;padding-left:18px;padding-right:18px;">
<table class="kmDividerContent" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;border-top-width:1px;border-top-style:solid;border-top-color:#ccc;">
<tbody>
<tr><td style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0"><span></span></td></tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
<table border="0" cellpadding="0" cellspacing="0" class="kmButtonBarBlock" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody class="kmButtonBarOuter">
<tr>
<td class="kmButtonBarInner" align="center" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;padding-top:9px;padding-bottom:9px;padding-left:9px;padding-right:9px;">
<table border="0" cellpadding="0" cellspacing="0" class="kmButtonBarContentContainer" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody>
<tr>
<td align="center" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;padding-left:9px;padding-right:9px;">
<table border="0" cellpadding="0" cellspacing="0" class="kmButtonBarContent" style='border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;font-family:"Helvetica Neue", Arial'>
<tbody>
<tr>
<td align="center" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<table border="0" cellpadding="0" cellspacing="0" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody>
<tr>
<td valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<table align="left" border="0" cellpadding="0" cellspacing="0" class="" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody>
<tr>
<td align="center" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;padding-right:10px;">
<a href="https://www.facebook.com/app.sendd" target="_blank" style="word-wrap:break-word;color:#15C;font-weight:normal;text-decoration:underline"><img src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/default/facebook_48.png" alt="Button Text" class="kmButtonBlockIcon" width="48" style="border:0;height:auto;line-height:100%;outline:none;text-decoration:none;width:48px; max-width:48px; display:block;" /></a>
</td>
</tr>
</tbody>
</table>
<!--[if gte mso 6]></td><td align="left" valign="top"><![endif]-->
<table align="left" border="0" cellpadding="0" cellspacing="0" class="" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody>
<tr>
<td align="center" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;padding-right:10px;">
<a href="https://twitter.com/sendd_app" target="_blank" style="word-wrap:break-word;color:#15C;font-weight:normal;text-decoration:underline"><img src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/default/twitter_48.png" alt="Custom" class="kmButtonBlockIcon" width="48" style="border:0;height:auto;line-height:100%;outline:none;text-decoration:none;width:48px; max-width:48px; display:block;" /></a>
</td>
</tr>
</tbody>
</table>
<!--[if gte mso 6]></td><td align="left" valign="top"><![endif]-->
<table align="left" border="0" cellpadding="0" cellspacing="0" class="" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody>
<tr>
<td align="center" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;">
<a href="https://plus.google.com/u/0/108818261732926029035/posts" target="_blank" style="word-wrap:break-word;color:#15C;font-weight:normal;text-decoration:underline"><img src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/default/google_plus_48.png" alt="Custom" class="kmButtonBlockIcon" width="48" style="border:0;height:auto;line-height:100%;outline:none;text-decoration:none;width:48px; max-width:48px; display:block;" /></a>
</td>
</tr>
</tbody>
</table>
<!--[if gte mso 6]></td><td align="left" valign="top"><![endif]-->
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
<table border="0" cellpadding="0" cellspacing="0" class="kmTextBlock" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody class="kmTextBlockOuter">
<tr>
<td class="kmTextBlockInner" valign="top" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;">
<table align="left" border="0" cellpadding="0" cellspacing="0" class="kmTextContentContainer" width="100%" style="border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0">
<tbody>
<tr>
<td class="kmTextContent" valign="top" style='border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;color:#222;font-family:"Helvetica Neue", Arial;font-size:14px;line-height:130%;text-align:left;padding-top:9px;padding-bottom:18px;padding-right:18px;padding-left:18px;text-align:center;'>
            For any queries, call us at +91-<strong>808-002-8081</strong> or<br />
mail us at hello@sendd.co
          </td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</table>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</center>
</body>
</html>"""

# Attach HTML and plain text
part1 = MIMEText(text,'plain')
part2 = MIMEText(html,'html')
msg.attach(part1)
msg.attach(part2)

# Send mail
server = smtplib.SMTP("smtp.mandrillapp.com:587")
server.login(SMTP_username,SMTP_password)
server.sendmail(sender, receiver, msg.as_string())
server.quit()