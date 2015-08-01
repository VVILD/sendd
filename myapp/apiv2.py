from tastypie.resources import ModelResource
from django.conf.urls import url
from myapp.models import *
from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.serializers import Serializer
from random import randint
import random
import urllib2,urllib
import hashlib, random
import os
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.authentication import ApiKeyAuthentication
import math
import string
from django.core.mail import send_mail
from push_notifications.models import APNSDevice, GCMDevice
from tastypie.resources import Resource

from django.http.response import HttpResponse
from tastypie import http
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import csrf_exempt
from tastypie.resources import Resource, ModelResource
import logging


import redis

config = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
}

r = redis.StrictRedis(**config)


cities={"Satara": "Maharashtra", "Krishnapur": "West Bengal", "Saundatti": "Karnataka", "Arakkonam": "Tamil Nadu", "Sultanpur%20Sadar": "Bihar", "Cherthala": "Kerala", "Nissing": "Haryana", "Karur": "Tamil Nadu", "Muthukur": "Andhra Pradesh", "Madurantakam": "Tamil Nadu", "Nabagram": "West Bengal", "Vemulawada": "Telangana", "Modinagar": "Uttar Pradesh", "Chengalpattu": "Tamil Nadu", "Savanur": "Karnataka", "Sindgi": "Karnataka", "Biswan": "Uttar Pradesh", "Cumbum": "Tamil Nadu", "Katrenikona": "Andhra Pradesh", "Thoothukkudi": "Tamil Nadu", "Kolkata%20East": "West Bengal", "Tirupathur": "Tamil Nadu", "Uran": "Maharashtra", "Virajpet": "Karnataka", "Phagwara": "Punjab", "Bharuch": "Gujarat", "Rishieksh": "Uttarakhand", "Chataparru": "Andhra Pradesh", "Vedaraniam": "Tamil Nadu", "Katwa": "West Bengal", "Vishnupur": "Bihar", "Joginder%20Nagar": "Himachal Pradesh", "Sitalkuchi": "West Bengal", "Gurap": "West Bengal", "Tiruturaipundi": "Tamil Nadu", "Sarenga": "West Bengal", "Santuri": "West Bengal", "Tirupattur": "Tamil Nadu", "Deoband": "Uttar Pradesh", "Raghunathapali": "Telangana", "Jind": "Haryana", "Kanke": "Jharkhand", "Pithoragarh": "Uttarakhand", "Reddigudem": "Andhra Pradesh", "Bangalore%20North": "Karnataka", "Sujangarh": "Rajasthan", "Shahpur": "Karnataka", "Niphad": "Maharashtra", "Una%28t%29": "Himachal Pradesh", "Manantahvady": "Kerala", "Gangtok": "Sikkim", "Allapur%20%2A%2A": "Uttar Pradesh", "Qusba%20Kotla": "Himachal Pradesh", "Phagwara%20Ho": "Punjab", "Palampur": "Himachal Pradesh", "Wyra": "Telangana", "Anekal": "Karnataka", "Sedam": "Karnataka", "Tamkuhi": "Bihar", "Narayankhed": "Telangana", "Raghuathpur": "West Bengal", "Palladam": "Tamil Nadu", "Padra": "Gujarat", "Amalapuram": "Andhra Pradesh", "Raghogarh": "Madhya Pradesh", "Trichur": "Kerala", "Anand%20Nagar": "Uttar Pradesh", "Siliguri": "West Bengal", "Shamli": "Uttar Pradesh", "Pandharpur": "Maharashtra", "Udayarpalayam": "Tamil Nadu", "Kadipiur": "Uttar Pradesh", "Haidergarh": "Uttar Pradesh", "Tiruvarur": "Tamil Nadu", "Lalgopalganj": "Uttar Pradesh", "Gingee": "Tamil Nadu", "Pedana": "Andhra Pradesh", "K%20%20Mahankal": "Himachal Pradesh", "Thirumangalam": "Tamil Nadu", "Arki": "Himachal Pradesh", "Ropar": "Punjab", "Karunagappaly": "Kerala", "Jayamkondcholapuram": "Tamil Nadu", "Ambala": "Haryana", "Kanchipuram": "Tamil Nadu", "Bareilly": "Uttar Pradesh", "Itahar": "West Bengal", "Siruguppa": "Karnataka", "Khamanon": "Punjab", "Irinjalakuda": "Kerala", "Kothavalasa": "Andhra Pradesh", "Howrah": "West Bengal", "Rivaikuntam": "Tamil Nadu", "Allahabad": "Uttar Pradesh", "Harodi": "Karnataka", "Sundarnagar%28t%29": "Himachal Pradesh", "Mormugao": "Goa", "Jogindernagar": "Himachal Pradesh", "Tirur": "Kerala", "Nadia%20North": "West Bengal", "Jaipur%20Moffusil": "Rajasthan", "Shimla%20Urban%28t%29": "Himachal Pradesh", "Ludhiana%20East": "Punjab", "Kudal": "Maharashtra", "Adoor": "Kerala", "Kaliyaganj": "West Bengal", "Srikalahasti": "Andhra Pradesh", "Shahpur%28t%29": "Karnataka", "Goutam%20Budd%20Nagar": "Uttar Pradesh", "Purwa": "Uttar Pradesh", "Dhaniakhali": "West Bengal", "Dehradun": "Uttarakhand", "Bayenda": "West Bengal", "Dalhousie%28t%29": "Himachal Pradesh", "Pehowa": "Haryana", "Eluru": "Andhra Pradesh", "Mandar": "Jharkhand", "Gollaprolu": "Andhra Pradesh", "Dhule": "Maharashtra", "Udaipur": "Rajasthan", "Dinhata": "West Bengal", "Vythiri": "Kerala", "Rajsamand": "Rajasthan", "Malegaon": "Maharashtra", "Gandevi": "Gujarat", "Mirzapur": "Uttar Pradesh", "Nampally": "Telangana", "Poonamallee": "Tamil Nadu", "Faridabad": "Haryana", "Nasik": "Maharashtra", "Palwal": "Haryana", "Karahal": "Madhya Pradesh", "Kamthi": "Maharashtra", "Salcette": "Goa", "Arkalgud": "Karnataka", "Kolllam": "Kerala", "Cuttack%20Sadar": "Odisha", "Baijnath": "Himachal Pradesh", "Nilambur": "Kerala", "Alangulam": "Tamil Nadu", "Bhallai": "Chhattisgarh", "Perintalmanna": "Kerala", "Veeraghattam": "Andhra Pradesh", "Salur": "Andhra Pradesh", "Panchuria": "Odisha", "Iluppur": "Tamil Nadu", "Raigarh": "Chhattisgarh", "Anandpur%20Sahib": "Punjab", "Dwarahat": "Uttarakhand", "Salcete": "Goa", "Dhalbhum": "Jharkhand", "Durg": "Chhattisgarh", "Beleghata": "West Bengal", "Tohana": "Haryana", "Lepakshi": "Andhra Pradesh", "Virudhachalam": "Tamil Nadu", "Mahasi": "Uttar Pradesh", "Sonepat": "Haryana", "Nandakumar": "West Bengal", "Kovvur": "Andhra Pradesh", "Kumarsain": "Himachal Pradesh", "Ramdurg": "Karnataka", "Kanth": "Uttar Pradesh", "Moga": "Punjab", "Hatkanagale": "Maharashtra", "Hilli": "West Bengal", "Angua": "West Bengal", "Perundurai": "Tamil Nadu", "Gudivada": "Andhra Pradesh", "Chatrapur": "Odisha", "Gushkara": "West Bengal", "Allagadda": "Andhra Pradesh", "Vikas%20Nagar": "Uttar Pradesh", "Barnala": "Punjab", "Holagarh": "Uttar Pradesh", "Rahata": "Maharashtra", "Haliyal": "Karnataka", "Malsras": "Tamil Nadu", "Banda": "Uttar Pradesh", "Jaspur": "Uttarakhand", "Tirukkoyilur": "Tamil Nadu", "Mirik": "West Bengal", "Tp%20Gudur": "Andhra Pradesh", "Habra%20-%20Ii": "West Bengal", "Vellore": "Tamil Nadu", "Kottarakkara": "Kerala", "Mannargudi": "Tamil Nadu", "K%20Kota": "Rajasthan", "Madanapalle": "Andhra Pradesh", "Kattummannarkoil": "Tamil Nadu", "Sangaum": "Telangana", "Kishangarh": "Rajasthan", "Sakaldiha": "Uttar Pradesh", "Khatima": "Uttarakhand", "Huzur": "Madhya Pradesh", "Mulug": "Telangana", "Chikhli": "Maharashtra", "Milak": "Uttar Pradesh", "Hata": "Uttar Pradesh", "Paravur": "Kerala", "Bhongaon": "Uttar Pradesh", "Tiruppathur": "Tamil Nadu", "Rawan": "Chhattisgarh", "Fatehpur%28t%29": "Uttar Pradesh", "Penukonda": "Andhra Pradesh", "Dungarpur": "Rajasthan", "Sahaswan": "Uttar Pradesh", "Nadiad": "Gujarat", "Mariahu": "Uttar Pradesh", "Kadma": "Jharkhand", "Razole": "Andhra Pradesh", "Bangarpet": "Maharashtra", "Karnal": "Haryana", "Lakshadweep": "Lakshadweep", "Dadri": "Uttar Pradesh", "Gondal": "Gujarat", "Jalor": "Rajasthan", "Budhan%20Pur": "Uttar Pradesh", "Uttar-tajpur": "West Bengal", "Chail": "Himachal Pradesh", "Kairana": "Uttar Pradesh", "Tiruppattur": "Tamil Nadu", "Khagual": "Bihar", "Chhatna": "West Bengal", "Chas": "Jharkhand", "Chikodi": "Karnataka", "Nashik": "Maharashtra", "Koilkuntla": "Andhra Pradesh", "Periyakulam": "Tamil Nadu", "Memari": "West Bengal", "D%20B%20Nagar": "Rajasthan", "Chirgaon": "Uttar Pradesh", "Chennur": "Telangana", "Jandiala%20Guru": "Punjab", "Erandol": "Maharashtra", "Roha": "Maharashtra", "Boath": "Telangana", "Mohammadabad%20Yusufpur": "Uttar Pradesh", "Barabani": "West Bengal", "Kadampukur": "West Bengal", "Ranchi": "Jharkhand", "Jundla": "Haryana", "Sivakasi": "Tamil Nadu", "Thiruvalla": "Kerala", "Joypur": "Rajasthan", "Jubbal": "Himachal Pradesh", "Gangapur": "Rajasthan", "Safidon": "Haryana", "Baridih%20Colony": "Bihar", "Udupi": "Karnataka", "Maunath%20Bhanjan": "Uttar Pradesh", "Honavar": "Karnataka", "Vadipatti": "Tamil Nadu", "Changanacherry": "Kerala", "Balotra": "Rajasthan", "Umrer": "Maharashtra", "S%20Qudeem": "Punjab", "Thiruvallur": "Tamil Nadu", "Sardhana": "Uttar Pradesh", "Onda": "West Bengal", "Aruppukkottai": "Tamil Nadu", "Mawana": "Uttar Pradesh", "Mau%20Aima": "Uttar Pradesh", "Hooghly%20South": "West Bengal", "Sonbhadra": "Uttar Pradesh", "Sirhind": "Punjab", "Kotabommali%20Mandal": "Andhra Pradesh", "Warangal": "Telangana", "Dighari": "Madhya Pradesh", "Maval": "Rajasthan", "Robertsganj": "Uttar Pradesh", "Bangarapet": "Karnataka", "Thiruvaiyaru": "Tamil Nadu", "Jewar": "Uttar Pradesh", "Sawaimadhopur": "Rajasthan", "Nawanshahr": "Punjab", "Kariapatti": "Tamil Nadu", "Sanguem": "Goa", "Makkuva": "Andhra Pradesh", "Phalodi": "Rajasthan", "Baishnabnagar": "West Bengal", "Kushtagi": "Karnataka", "Jaitu": "Punjab", "Biramitrapur": "Odisha", "Desuri": "Rajasthan", "Porbandar": "Gujarat", "Puinan": "West Bengal", "Navsari": "Gujarat", "Arsha": "West Bengal", "Kalikiri": "Andhra Pradesh", "Thalapilly": "Kerala", "Azamgarh": "Uttar Pradesh", "Narwana": "Haryana", "Aruppukottai": "Tamil Nadu", "Chhpyana": "Uttar Pradesh", "Parbatsar": "Rajasthan", "Moradabad": "Uttar Pradesh", "Shrirampur": "Maharashtra", "Kunnathur": "Tamil Nadu", "Tirumalagiri": "Telangana", "Namchi": "Sikkim", "Ghumarwin": "Himachal Pradesh", "Saidapet": "Tamil Nadu", "Madurai%20South": "Tamil Nadu", "Chincholi": "Karnataka", "Gudalur": "Tamil Nadu", "Raurkela%20%28m%29": "Odisha", "Basti%20Sadar": "Chhattisgarh", "Kadipur": "Uttar Pradesh", "Maicha": "Uttarakhand", "Bharatpur": "Rajasthan", "Ghazipur": "Uttar Pradesh", "Addatigala": "Andhra Pradesh", "Latur": "Maharashtra", "Samalkota": "Andhra Pradesh", "Kirtinagar": "Uttarakhand", "Hoshiar%20%20Pur": "Punjab", "Batrara": "Himachal Pradesh", "Yadgir": "Karnataka", "Naggar": "Himachal Pradesh", "Chakeri": "Uttar Pradesh", "Anni": "Himachal Pradesh", "Haldibari": "West Bengal", "Ponnur": "Andhra Pradesh", "Rangpo": "Sikkim", "Koraon%20%2A%2A": "Uttar Pradesh", "Chengam": "Tamil Nadu", "Karimpur%20Ii": "West Bengal", "Ajodhyapur": "Rajasthan", "Daspur": "West Bengal", "Tiruvananamalai": "Tamil Nadu", "Kurseong": "West Bengal", "Ghatiya": "Madhya Pradesh", "Kumta": "Karnataka", "Needamangalam": "Tamil Nadu", "Devakottai": "Tamil Nadu", "Koduru": "Andhra Pradesh", "Kamareddy": "Telangana", "Aravakurichi": "Tamil Nadu", "Siddapur": "Karnataka", "Mahisadal": "West Bengal", "Vinjamoor": "Andhra Pradesh", "Idappadi": "Tamil Nadu", "Berhampur": "Odisha", "Charminar": "Telangana", "Suti%20-%20I": "West Bengal", "Panskura%20Ii": "West Bengal", "Anwarganj": "Uttar Pradesh", "Kasaragod": "Kerala", "Chhata": "Uttar Pradesh", "South%20Presidency": "Tamil Nadu", "Surat%20City": "Gujarat", "Khopoli": "Maharashtra", "Ketugram%20-%20I": "West Bengal", "Belthra%20Road": "Uttar Pradesh", "Pendurthi": "Andhra Pradesh", "Mannarkad": "Kerala", "Ulundurpettai": "Tamil Nadu", "Hamirpur%28t%29": "Himachal Pradesh", "Pudukkottai--": "Tamil Nadu", "Girwa": "Madhya Pradesh", "Narsapur": "Andhra Pradesh", "Kichha": "Uttarakhand", "Jamjodhpur": "Gujarat", "Pen": "Maharashtra", "Kakadeo": "Uttar Pradesh", "Raikot": "Punjab", "Sirohi": "Rajasthan", "Sarsawa": "Uttar Pradesh", "Kaligiri": "Andhra Pradesh", "Manihara": "Uttar Pradesh", "Chamoli": "Uttarakhand", "Manachanalloor": "Tamil Nadu", "Beawar": "Rajasthan", "Gurgaon": "Haryana", "Purulia": "West Bengal", "Bharatpur%20-%20Ii": "Odisha", "Palakkad": "Kerala", "Chauri%20Chaura": "Uttar Pradesh", "Goutam%20%20Budd%20%20Nagar": "Uttar Pradesh", "Hatkanangle": "Maharashtra", "Islampur": "West Bengal", "Faizabad": "Uttar Pradesh", "Dewas": "Madhya Pradesh", "Vijai%20Nagar": "Uttar Pradesh", "Sankrail": "West Bengal", "Preet%20Nagar": "Punjab", "Banga": "Punjab", "Ram%20Sanehi%20Ghat": "Uttar Pradesh", "Jhunjhunun": "Rajasthan", "Idukki": "Kerala", "Visakhapatnam%20%28urban%29": "Andhra Pradesh", "Ananthagiri": "Andhra Pradesh", "Umargam": "Gujarat", "Pharenda": "Uttar Pradesh", "Khed%20%28rtg%29": "Maharashtra", "Menhdawal": "Uttar Pradesh", "Barara": "Haryana", "Deoria": "Uttar Pradesh", "Manamadurai": "Tamil Nadu", "Mulshi": "Maharashtra", "Hanumangrh": "Rajasthan", "Tirupati%20%28urban%29": "Maharashtra", "Saidpur": "Uttar Pradesh", "Biakner": "Rajasthan", "Mohammedabad": "Uttar Pradesh", "Jammikunta": "Telangana", "Budaun": "Uttar Pradesh", "Vadodara": "Gujarat", "Chennai%20City%20North": "Tamil Nadu", "Deodurga": "Karnataka", "Gorubathan": "West Bengal", "Raibag": "Karnataka", "Dubda": "West Bengal", "Bhater": "Himachal Pradesh", "Repalle": "Andhra Pradesh", "Krishnaganj": "West Bengal", "Pursurah": "West Bengal", "Karandighi": "West Bengal", "Englishbazar": "West Bengal", "Bagdah": "West Bengal", "Srivilliputtur": "Tamil Nadu", "Nihri%28s%20T%29": "Himachal Pradesh", "Sitarganj": "Uttarakhand", "Sidhauli": "Uttar Pradesh", "Sinnar": "Maharashtra", "Phuool%20Pur": "Uttar Pradesh", "Bhusawal": "Maharashtra", "Calicut": "Kerala", "Sakaldhia": "Uttar Pradesh", "Palayamkottai": "Tamil Nadu", "Kotkhai": "Himachal Pradesh", "Dasuya": "Punjab", "Nandigram-ii": "West Bengal", "Ramanagaram": "Karnataka", "Ranaghat%20-%20Ii": "West Bengal", "Anaparthy": "Andhra Pradesh", "Penumantra%20%28mdl%29": "Andhra Pradesh", "Wankaner": "Gujarat", "Ashoknagar": "Madhya Pradesh", "Sardarshahar": "Rajasthan", "Bali%20Chowki%28s%20T%29": "Himachal Pradesh", "Challapalli": "Andhra Pradesh", "Bassi%20Pathana": "Punjab", "Bhanderhati": "West Bengal", "Sriganganagar": "Rajasthan", "Bidar": "Karnataka", "Chanchal": "West Bengal", "Ponani": "Kerala", "Laksar": "Uttarakhand", "Gauriganj": "Uttar Pradesh", "Mainpuri": "Uttar Pradesh", "Chinglepet": "Tamil Nadu", "Burdwan%20-%20Ii": "West Bengal", "Cherthla": "Kerala", "Tiruturipundi": "Tamil Nadu", "Maharajganj": "Uttar Pradesh", "Dera%20Gopipur%28t%29": "Himachal Pradesh", "Nichlaul": "Uttar Pradesh", "Tenali": "Andhra Pradesh", "Igatpuri": "Maharashtra", "Halol": "Gujarat", "Khanakul-2b": "West Bengal", "Bilaspur": "Chhattisgarh", "Rasra": "Uttar Pradesh", "Kanksa": "West Bengal", "Amaravati": "Andhra Pradesh", "Somwarpet": "Karnataka", "Rishikesh": "Uttarakhand", "Ottapalam": "Kerala", "Bhulath": "West Bengal", "B%20Bagewadi": "Karnataka", "Sikandarour": "Uttar Pradesh", "S%20R%20Nagar": "Telangana", "Trimbakeshwar": "Maharashtra", "Ambajipeta": "Andhra Pradesh", "Fatehgarh%20Sahib": "Punjab", "Gangavathi": "Karnataka", "Tulsipur": "Uttar Pradesh", "Mysore": "Karnataka", "Thane": "Maharashtra", "Guoour": "Goa", "Krishnagiri": "Tamil Nadu", "Khajani": "Uttar Pradesh", "Alapur": "Uttar Pradesh", "Alatur": "Kerala", "Chitvel": "Andhra Pradesh", "Miryalguda": "Telangana", "Yeleswaram": "Andhra Pradesh", "Avadaiyarkoil": "Tamil Nadu", "Champawat": "Uttarakhand", "Jalalpore": "Gujarat", "Bhgaon": "Maharashtra", "Vaimpalle": "Andhra Pradesh", "Dehra%20Gopipur": "Himachal Pradesh", "Namkum": "Jharkhand", "Kaviti%20Mandal": "Andhra Pradesh", "Karthikappally": "Kerala", "Sojat": "Rajasthan", "Rohru": "Himachal Pradesh", "Nandigram": "West Bengal", "Jalesar": "Uttar Pradesh", "Narasaraopet": "Andhra Pradesh", "Chintamani": "Karnataka", "Ambalapuzh%20A": "Kerala", "Singtam": "Sikkim", "New%20Delhi": "Delhi", "Ravangla": "Sikkim", "Suratgarh": "Rajasthan", "Mudhol": "Karnataka", "Memari%20-%20Ii": "West Bengal", "Nalagarh": "Himachal Pradesh", "Walajapet": "Tamil Nadu", "Delhi%20East": "Delhi", "Bdh": "Gujarat", "Chakrata": "Uttarakhand", "Kannauj": "Uttar Pradesh", "Pakala": "Andhra Pradesh", "Nihal%20Singhwala": "Punjab", "Thalisain": "Uttarakhand", "Len": "Nagaland", "Saroornagar": "Telangana", "Air%20Force": "Rajasthan", "Suar": "Uttar Pradesh", "Nagina": "Uttar Pradesh", "Gajja": "Rajasthan", "Kota": "Rajasthan", "Hunsabad": "Telangana", "Ganti": "Rajasthan", "Bhatpara": "West Bengal", "Pernem": "Goa", "Kalghatgi": "Karnataka", "Colonelganj": "Uttar Pradesh", "Jodhpur": "Rajasthan", "Nilokheri": "Haryana", "Melli": "Sikkim", "Idar": "Gujarat", "Mudhole": "Maharashtra", "Mavli": "Rajasthan", "Arambag": "West Bengal", "Bhuranj": "Himachal Pradesh", "Dahisar%20West": "Maharashtra", "Illuppur": "Tamil Nadu", "Sivigiri": "Tamil Nadu", "Bulandshahr": "Uttar Pradesh", "Trichy": "Tamil Nadu", "Mavelikkara": "Kerala", "Palamaner": "Andhra Pradesh", "Krishnanagar-i": "West Bengal", "Mahabaleshwar": "Maharashtra", "Valparai": "Tamil Nadu", "Mudigubba": "Andhra Pradesh", "Palayankottai": "Tamil Nadu", "Kirishnarayapuram": "Tamil Nadu", "Amethi": "Uttar Pradesh", "Bhairampur": "West Bengal", "Kapkote": "Uttarakhand", "Tiswadi": "Goa", "Changanassery": "Kerala", "Purulia%20-%20I": "West Bengal", "Paithan": "Maharashtra", "Lahaul": "Himachal Pradesh", "Tuni": "Andhra Pradesh", "Verka": "Punjab", "Morang%28t%29": "Jharkhand", "Harraiya": "Uttar Pradesh", "Gangolihat": "Uttarakhand", "Chaubepur": "Uttar Pradesh", "Hardoi": "Uttar Pradesh", "Sadulpur": "Rajasthan", "Sagari": "Bihar", "Ratua": "West Bengal", "Devarapalli%20Mandalam": "Andhra Pradesh", "Metpalli": "Telangana", "Lansdowne": "Uttarakhand", "Sikandrabad": "Uttar Pradesh", "Cheyyur": "Tamil Nadu", "Pelling": "Sikkim", "Bithara%20Road": "Uttar Pradesh", "Veppanthattai": "Tamil Nadu", "Pandabeswar": "West Bengal", "Basavana%20Bagevadi": "Karnataka", "Srirangam": "Tamil Nadu", "Nakur": "Uttar Pradesh", "Meerpur": "Uttar Pradesh", "Kollam": "Kerala", "Ramachandrapuram": "Andhra Pradesh", "Muddanur": "Andhra Pradesh", "Walva": "Maharashtra", "Sakchi": "Jharkhand", "Barabari%20South": "West Bengal", "Raipur": "Chhattisgarh", "Sanganer": "Rajasthan", "Bantval": "Karnataka", "Ambasamudram": "Tamil Nadu", "Bangalore%20South": "Karnataka", "Bhopal": "Madhya Pradesh", "Tiruannamalai": "Tamil Nadu", "Taranagar": "Rajasthan", "Guntur": "Andhra Pradesh", "Tadepalligudem": "Andhra Pradesh", "Wanaparthy": "Telangana", "Ambegaon": "Maharashtra", "Chandrakona-ii": "West Bengal", "Cuddalore": "Tamil Nadu", "Shenkottai": "Tamil Nadu", "Behat": "Uttar Pradesh", "Kalna": "West Bengal", "Rhenock": "Sikkim", "Tufanganj%20-%20Ii": "West Bengal", "Salon": "Uttar Pradesh", "Neyyattinkara": "Kerala", "Srivilliputhur": "Tamil Nadu", "Thirumalairayan%20Pattinam%20Commune%20Panchayat": "Puducherry", "Hyderabad%20City": "Telangana", "Jamshedpur": "Jharkhand", "Tarabganij": "Uttar Pradesh", "Saravakota%20Mandal": "Andhra Pradesh", "Aligarh": "Uttar Pradesh", "Khinwsar": "Rajasthan", "Baghapurana": "Punjab", "Lakhimpur": "Uttar Pradesh", "Kalakada": "Andhra Pradesh", "Pachor": "Madhya Pradesh", "Limkheda": "Gujarat", "Banjar%28t%29": "Himachal Pradesh", "Dholpur": "Rajasthan", "Pallipattu": "Tamil Nadu", "Jalalpur": "Uttar Pradesh", "Meerut": "Uttar Pradesh", "Kasauli": "Himachal Pradesh", "Rourkela": "Odisha", "Ghatal": "West Bengal", "Shahabad": "Uttar Pradesh", "Bhanupali": "Punjab", "Sanmeshwar": "Maharashtra", "Dhamtari": "Chhattisgarh", "Pedagantyada": "Andhra Pradesh", "Amravati": "Maharashtra", "Tallada": "Telangana", "Begunia": "Odisha", "Ahmedabad": "Gujarat", "Ganapavaram%20Mandalam": "Andhra Pradesh", "Kaladhungi": "Uttarakhand", "Chiral": "Kerala", "Thalasery": "Kerala", "Hosdurg": "Kerala", "Jawahar%20Nagar": "Telangana", "Golmuri": "Jharkhand", "Nilakkottai": "Tamil Nadu", "Andipatti": "Tamil Nadu", "Madanmohanpur": "Jharkhand", "Thane%20Central": "Maharashtra", "Banaganapalle": "Andhra Pradesh", "Itachuna": "West Bengal", "Achampet": "Andhra Pradesh", "Peddapappur": "Andhra Pradesh", "Sivagiri": "Tamil Nadu", "Kurnool": "Andhra Pradesh", "Hungund": "Karnataka", "Khargram": "West Bengal", "Nawabganj": "Uttar Pradesh", "Raichur": "Karnataka", "Pamidi": "Andhra Pradesh", "Mejhia": "Jharkhand", "Palam%20Road": "Odisha", "K%20R%20Pete": "Maharashtra", "Banaganapalli": "Andhra Pradesh", "Madha": "Maharashtra", "Koradacherry": "Tamil Nadu", "Kundgol": "Karnataka", "Ladwa": "Haryana", "Manaparai": "Tamil Nadu", "Kadi": "Gujarat", "Kangeyam": "Tamil Nadu", "Charkhi%20Dadri": "Haryana", "Rajam%20Mandal": "Andhra Pradesh", "Karapa": "Andhra Pradesh", "Supa": "Maharashtra", "Thiruthuraipoondi": "Tamil Nadu", "Kenda": "West Bengal", "Mehnagar%20%2A%2A": "Uttar Pradesh", "Dharmajigudem": "Andhra Pradesh", "Gorakhpur": "Uttar Pradesh", "Dhanghata": "Uttar Pradesh", "Shikarpur": "Uttar Pradesh", "Wada": "Maharashtra", "Anand": "Gujarat", "Meerganj": "Uttar Pradesh", "Bokaro": "Jharkhand", "Atrampur": "Uttar Pradesh", "Malad%20West": "Maharashtra", "Nuzvid": "Andhra Pradesh", "Karunagappally": "Kerala", "Amloh%20%28p%29": "Punjab", "Spiti": "Himachal Pradesh", "Mukundapuram": "Kerala", "Eojnagar": "West Bengal", "Gangajalghati": "West Bengal", "Jangipara": "West Bengal", "Jhawa": "West Bengal", "Anara": "Gujarat", "Quepem": "Goa", "Kotagiri": "Tamil Nadu", "Abohar": "Punjab", "Dawarahat": "Uttarakhand", "Asifabad": "Telangana", "Pokhari": "Maharashtra", "Bandel": "West Bengal", "Rupnagar": "Punjab", "Karveer": "Maharashtra", "Velgode": "Andhra Pradesh", "Utnoor": "Telangana", "Palacode": "Tamil Nadu", "Paramathi%20Velur": "Tamil Nadu", "Jhalawar": "Rajasthan", "Indi": "Karnataka", "Mangalore": "Karnataka", "Bapatla": "Andhra Pradesh", "Etawah": "Uttar Pradesh", "Bhiwani": "Haryana", "Kulithalai": "Tamil Nadu", "Burkot": "Uttarakhand", "Rasulabad": "Uttar Pradesh", "Devikulam": "Kerala", "Mehre": "Himachal Pradesh", "Homnabad": "Karnataka", "Krishnangar%20Ii": "West Bengal", "Thandrampattu": "Tamil Nadu", "Burdwan": "West Bengal", "Amaravathi": "Andhra Pradesh", "Kothakota": "Andhra Pradesh", "Mypadu": "Andhra Pradesh", "Alwar": "Rajasthan", "S%20A%20S%20Nagar%20%28mohali%29": "Punjab", "Salempur": "Uttar Pradesh", "Vayalpad": "Andhra Pradesh", "Baran": "Rajasthan", "Neemuch": "Madhya Pradesh", "South%20Delhi": "Delhi", "Chittorgarh": "Rajasthan", "Kottayam": "Kerala", "Moyna": "Rajasthan", "Gharsana": "Rajasthan", "Eranad": "Kerala", "Kothagudem": "Telangana", "Tirukuvalai": "Tamil Nadu", "Amdanga": "West Bengal", "Valsad": "Gujarat", "Barshi": "Maharashtra", "Yercaud": "Tamil Nadu", "Badalapur": "Maharashtra", "Daman": "Daman and Diu", "Anklav": "Gujarat", "Rajarhat": "West Bengal", "Ludhiana%20City": "Punjab", "Jhalda": "West Bengal", "Velhe": "Maharashtra", "Rohtak": "Haryana", "Sankarankovil": "Tamil Nadu", "Baroh": "Himachal Pradesh", "Raghunathpur": "West Bengal", "Muzaffarnagar": "Uttar Pradesh", "Pedakakani": "Andhra Pradesh", "Barabazar": "West Bengal", "Hooghly%20North": "West Bengal", "Bhagta%20Bhai": "Punjab", "Noida": "Uttar Pradesh", "Siddipet": "Telangana", "Delhi": "Delhi", "Hayathnagar": "Telangana", "Bapulapadu": "Andhra Pradesh", "Sangamner": "Maharashtra", "Malihabad": "Uttar Pradesh", "Arantangi": "Tamil Nadu", "Giddalur": "Andhra Pradesh", "Khambhalia": "Gujarat", "Nawanshahar": "Punjab", "Ahmednagar": "Maharashtra", "Nanded": "Maharashtra", "Kalpa%28t%29": "Himachal Pradesh", "Zaheerabad": "Telangana", "Dharchula": "Uttarakhand", "Kalol": "Gujarat", "Meliaputti%20Mandal": "Andhra Pradesh", "Piduguralla": "Andhra Pradesh", "Hiramandalam%20Mandal": "Andhra Pradesh", "Pakyong": "Sikkim", "Kaliachak": "West Bengal", "Agastheeswaram": "Tamil Nadu", "Atmakur": "Andhra Pradesh", "Phaltan": "Maharashtra", "Kishan%20Garh": "Rajasthan", "Chikmagalur": "Karnataka", "Sangareddy": "Telangana", "D%20Hirehal": "Andhra Pradesh", "Chanditala%20-%20Ii": "West Bengal", "Alangiri": "Tamil Nadu", "Dudhi": "Uttar Pradesh", "Baruipur": "West Bengal", "Ani%28s%20T%29": "Chhattisgarh", "Mekliganj": "West Bengal", "Malshiras": "Maharashtra", "Kanchrapara": "West Bengal", "G%20Ghati": "Rajasthan", "Bisra": "Odisha", "Byadgi": "Karnataka", "Lucknow": "Uttar Pradesh", "Dhuri": "Punjab", "Sambhal": "Uttar Pradesh", "Kulittalai": "Tamil Nadu", "Egmore%20Nungambakkam": "Tamil Nadu", "Jalandhar%20-ii": "Punjab", "Parkal": "Telangana", "Bangalore%20East": "Karnataka", "Tambaram": "Tamil Nadu", "Budge%20Budge%20-%20I": "West Bengal", "Mancherial": "Telangana", "Barjora": "West Bengal", "Hingna": "Maharashtra", "Mansa": "Punjab", "Gudiyatham": "Tamil Nadu", "Kashipur": "Uttarakhand", "Ferozpur": "Punjab", "Venkatachalam": "Andhra Pradesh", "Serampore": "West Bengal", "Ludhiana%20%28west%29": "Punjab", "Alipurduar%20-%20I": "West Bengal", "Thottiam": "Tamil Nadu", "Ottapidaram": "Tamil Nadu", "Erode": "Tamil Nadu", "Devgadh%20Baria": "Gujarat", "Balurghat": "West Bengal", "Jalalabad": "Punjab", "Valapady": "Tamil Nadu", "Mirzapur%20Sadar": "Uttar Pradesh", "Bundi": "Rajasthan", "Chittur": "Kerala", "Tiruchendur": "Tamil Nadu", "Neravy%20Commune%20Panchayat": "Puducherry", "Loha": "Maharashtra", "Siraul%20Gauspur": "Uttar Pradesh", "Burdwan%20-%20I": "West Bengal", "Gadarpur": "Uttarakhand", "Amreli": "Gujarat", "Rbl": "Uttar Pradesh", "Ramangara": "Karnataka", "Gurazalla": "Andhra Pradesh", "Lal%20Ganj": "Uttar Pradesh", "Chitapur": "Karnataka", "Kandivali%20West": "Maharashtra", "Thasra": "Gujarat", "Jalandhar-ii": "Punjab", "Singur": "West Bengal", "Yavatmal": "Maharashtra", "Dharamkot": "Punjab", "Hoskote": "Karnataka", "Bti": "Madhya Pradesh", "Bikapur": "Uttar Pradesh", "Manuguru": "Telangana", "Jaipur": "Rajasthan", "Denkanikottai": "Tamil Nadu", "Kolar": "Karnataka", "Khagda": "West Bengal", "Ankola": "Karnataka", "Bathalapalle": "Andhra Pradesh", "Behta%20Gambhirpur": "Uttar Pradesh", "Ambalapuzha": "Kerala", "Phulpur": "Uttar Pradesh", "Sholinganallur": "Tamil Nadu", "Sreebhumi": "West Bengal", "Pathardi": "Maharashtra", "Jaswant%20Nagar": "Rajasthan", "Peerumade": "Kerala", "Udagamandalam": "Tamil Nadu", "Himayathnagar": "Telangana", "Salboni": "West Bengal", "Karsog": "Himachal Pradesh", "Rae%20Bareli": "Uttar Pradesh", "Nadendla": "Andhra Pradesh", "Dada%20Nagar": "Uttar Pradesh", "Gulbarga": "Karnataka", "Kerakat": "Uttar Pradesh", "Chandanagar": "Telangana", "Faridpur": "Uttar Pradesh", "Bhokar": "Maharashtra", "Sirkali": "Tamil Nadu", "Murshidabad%20Jiaganj": "West Bengal", "Garhbeta-i": "West Bengal", "Bilthara%20Road": "Uttar Pradesh", "Pattukkottai": "Tamil Nadu", "Mabarakpur": "Uttar Pradesh", "Huvinahadagali": "Karnataka", "Behrampore": "West Bengal", "Chamba": "Himachal Pradesh", "Manapparai": "Tamil Nadu", "Barra": "Jharkhand", "Chilakaluripet": "Andhra Pradesh", "Kadiri": "Andhra Pradesh", "Industrial%20Estate": "Punjab", "Krishnagar%20-%20Ii": "Andhra Pradesh", "Phul": "Punjab", "Shadnagar": "Telangana", "Tarikere": "Karnataka", "Devanahalli": "Karnataka", "Patancheru": "Telangana", "Solan": "Himachal Pradesh", "Adilabad": "Telangana", "Hisar": "Haryana", "Jajmau": "Uttar Pradesh", "Bhucho": "Punjab", "Pune": "Maharashtra", "Labpur": "West Bengal", "Kanniyakumari": "Tamil Nadu", "Peapally": "Arizona", "Dahanu": "Maharashtra", "Pallipat": "Tamil Nadu", "Uttiramerur": "Tamil Nadu", "Tirurangadi": "Kerala", "Jagatpur": "Odisha", "Rampachodavaram": "Andhra Pradesh", "Koni": "Rajasthan", "Konaraopet": "Telangana", "Nagari": "Andhra Pradesh", "Falakata": "West Bengal", "Dhar%20Kalan": "Punjab", "Tehatta": "West Bengal", "Diamond%20Harbour%20-%20I": "West Bengal", "Sulthanbathery": "Kerala", "Narkeldanga": "West Bengal", "Sangrur": "Punjab", "Bavla": "Gujarat", "Rajapur": "Maharashtra", "Udumalaipettai": "Tamil Nadu", "Nigdhu": "Haryana", "Denkanikotta": "Tamil Nadu", "Hindaun": "Rajasthan", "Koyilandi": "Kerala", "Agasteeswaram": "Tamil Nadu", "Sirathu": "Uttar Pradesh", "Bangalore": "Karnataka", "Sahid%20Matangini": "West Bengal", "Amtalia": "West Bengal", "Poo%28t%29": "Andhra Pradesh", "Budan%20Pur": "Uttar Pradesh", "Nihal%20Singh%20Wala": "Punjab", "Bhiwandi": "Maharashtra", "Amraudha": "Uttar Pradesh", "Hanamkonda%20Mandal": "Andhra Pradesh", "Campeirganj": "Uttar Pradesh", "Aundipatti": "Tamil Nadu", "Jawali": "Himachal Pradesh", "Salooni": "Himachal Pradesh", "Sampgaon": "Karnataka", "Sandila": "Uttar Pradesh", "Golconda": "Telangana", "Tirunelveli": "Tamil Nadu", "Kang": "Punjab", "Mohammadabad%20Gohana": "Uttar Pradesh", "Jhansi": "Uttar Pradesh", "Dhaulana": "Uttar Pradesh", "Sattenapalle": "Andhra Pradesh", "Raghunathganj%20-%20Ii": "Madhya Pradesh", "Varanasi": "Uttar Pradesh", "Hasanparthy": "Telangana", "Badlapur": "Maharashtra", "Shillai": "Himachal Pradesh", "Mahmudabad": "Uttar Pradesh", "Lathikata": "Odisha", "Arni": "Tamil Nadu", "Kushmandi": "West Bengal", "Goregaon%20East": "Maharashtra", "Sindhanur": "Karnataka", "Jawad": "Madhya Pradesh", "Talwandi%20Sabo": "Punjab", "Marwar%20Jn": "Rajasthan", "Rajganj": "Jharkhand", "Ballichak": "West Bengal", "Haldia%20Patna": "West Bengal", "Baghthala": "Haryana", "Raebarely": "Uttar Pradesh", "Garur": "Uttarakhand", "Tarabganj": "Uttar Pradesh", "Sawantwadi": "Maharashtra", "Sandur": "Karnataka", "Suryapet": "Telangana", "Raebareli": "Uttar Pradesh", "Railway%20Road": "Uttar Pradesh", "Amritsar-%20Ii": "Punjab", "Sangaria": "Rajasthan", "Hapur": "Uttar Pradesh", "Chamba%28t%29": "Himachal Pradesh", "Sangat": "Punjab", "Ghaziabad": "Uttar Pradesh", "Fazilka": "Punjab", "Mananthavady": "Kerala", "Sangam": "Telangana", "Jakholi": "Uttarakhand", "Dhamdha": "Chhattisgarh", "Adur": "Kerala", "Shahbad": "Haryana", "Shimoga": "Karnataka", "Munsiari": "Uttarakhand", "Milkipur": "Uttar Pradesh", "Kilvelur": "Tamil Nadu", "Thovala": "Kerala", "Namkhana": "West Bengal", "Ponnani": "Kerala", "Vijayawada%20%28urban%29": "Andhra Pradesh", "Daskroi": "Gujarat", "Ambalappuzha": "Kerala", "Jagraon": "Punjab", "Ashok%20Nagar": "Tamil Nadu", "Kunigal": "Karnataka", "Midnapore": "West Bengal", "Malout": "Punjab", "Okhimath": "Uttarakhand", "Ramtek": "Maharashtra", "Dharapuram": "Tamil Nadu", "Tirutani": "Tamil Nadu", "Sadabad": "Uttar Pradesh", "Alangudi": "Tamil Nadu", "Baldwara%28s%20T%29": "Himachal Pradesh", "Banshihari": "West Bengal", "Tirumangalam": "Tamil Nadu", "Kaikalur": "Andhra Pradesh", "Karad": "Maharashtra", "Kotla": "Punjab", "Bhilwara": "Rajasthan", "Nagpur": "Maharashtra", "Palanpur": "Gujarat", "Balconagar": "Chhattisgarh", "Mana%20Camp": "Chhattisgarh", "Burwan": "West Bengal", "Vikasnagar%20%2A%2A": "Uttarakhand", "Paramathivelur": "Tamil Nadu", "Mandapeta": "Andhra Pradesh", "Khedbrahma": "Gujarat", "Sirauli%20Gauspur": "Uttar Pradesh", "Saoner": "Maharashtra", "Jalna": "Maharashtra", "Dhumakot": "Uttarakhand", "Hirbandh": "West Bengal", "Kesrisinghpur": "Rajasthan", "Purbasthali%20-%20Ii": "West Bengal", "Bhatar": "West Bengal", "Krithivennu": "Andhra Pradesh", "Gummidipundi": "Tamil Nadu", "Rabale": "Maharashtra", "Puttaparthi": "Andhra Pradesh", "Gudur": "Andhra Pradesh", "Rawatpur%20Gaon": "Uttar Pradesh", "Kakinada%20%28urban%29": "Andhra Pradesh", "Kaithal": "Haryana", "Dhoomakot": "Uttarakhand", "Nagaur": "Rajasthan", "Chandrapur": "Maharashtra", "Trivandrum": "Kerala", "Nohar": "Rajasthan", "Kodaikanal": "Tamil Nadu", "Bellary": "Karnataka", "Mant": "Uttar Pradesh", "Thottiyam": "Tamil Nadu", "Uppal": "Telangana", "Tiruklalikundram": "Tamil Nadu", "Calcutta%20South": "West Bengal", "Secunderabad": "Telangana", "Hoshiarpur": "Punjab", "Athani": "Karnataka", "Rudhauli": "Uttar Pradesh", "Baraut": "Uttar Pradesh", "Nautanawa": "Uttar Pradesh", "Koratla": "Telangana", "Nizamabad": "Telangana", "Belthangady": "Karnataka", "Degana": "Rajasthan", "Anoop%20Shahr": "Uttar Pradesh", "Rajpura": "Punjab", "Aswaraopet": "Telangana", "Gudiyattam": "Tamil Nadu", "Mundra": "Gujarat", "Tizara": "Rajasthan", "Viramgam": "Gujarat", "Kolkata": "West Bengal", "Bommanahal": "Andhra Pradesh", "Ranagaht-ii": "West Bengal", "Coimbatore": "Tamil Nadu", "Meenachil": "Kerala", "Arakonam": "Tamil Nadu", "Zamania": "Uttar Pradesh", "Hasanpur": "Uttar Pradesh", "Sumerpur": "Rajasthan", "Peddapalle": "Telangana", "Kamudi": "Tamil Nadu", "Joida": "Karnataka", "Ilayangudi": "Tamil Nadu", "Puraula": "West Bengal", "Peddapalli": "Telangana", "Anakapalle": "Andhra Pradesh", "Thakurdwara": "Uttar Pradesh", "Tanakpur": "Uttarakhand", "Bhadrawati": "Karnataka", "Nadaun": "Himachal Pradesh", "Tapan": "Rajasthan", "Canacona": "Goa", "Hyderabad": "Telangana", "Dhanbad": "Jharkhand", "Raninagar%20-%20I": "West Bengal", "Khanakul-i": "West Bengal", "Hanumangarh": "Rajasthan", "Allapur": "Uttar Pradesh", "Haider%20Garh": "Uttar Pradesh", "Tibbi": "Rajasthan", "Khalapur": "Maharashtra", "Shilai": "Himachal Pradesh", "Ratlam": "Madhya Pradesh", "Thiruvidaimarudur": "Tamil Nadu", "Firozabad": "Uttar Pradesh", "Atur": "Tamil Nadu", "Gmc": "Telangana", "Chamiari": "Punjab", "Bazpur": "Uttarakhand", "Baragudha": "Odisha", "Bishnupur": "Manipur", "Jaleswar": "Odisha", "Bhimavaram": "Andhra Pradesh", "Gunnaur": "Uttar Pradesh", "Cooch%20Behar%20-%20I": "West Bengal", "Karchhana": "Uttar Pradesh", "Haroli": "Himachal Pradesh", "Quilandy": "Kerala", "Sagar": "Madhya Pradesh", "Armapur": "Uttar Pradesh", "Sarkaghat": "Himachal Pradesh", "M%20Bad": "Uttar Pradesh", "Akola": "Maharashtra", "Nandyal": "Andhra Pradesh", "Anjar": "Gujarat", "Hanskhlai": "West Bengal", "Tanda": "Uttar Pradesh", "Budge%20Budge": "West Bengal", "Bansdih": "Uttar Pradesh", "Bhaini%20Bagha": "Punjab", "Spiti%20%20%20%20%20%20%20%28t%29": "Himachal Pradesh", "Sikandra": "Uttar Pradesh", "Pulivendla": "Andhra Pradesh", "Khanpur": "Rajasthan", "Nayagram": "West Bengal", "Tana%20Gazi": "Rajasthan", "Meja": "Uttar Pradesh", "Koregaon": "Maharashtra", "Karaikudi": "Tamil Nadu", "Dinhata%20-%20I": "West Bengal", "Pithapuram": "Andhra Pradesh", "Ballia": "Uttar Pradesh", "Nidamangalam": "Tamil Nadu", "Kapurthala": "Punjab", "Sakhinetipalli%20Mandal": "Andhra Pradesh", "Taliaparamba": "Kerala", "Kamuthi": "Tamil Nadu", "Jangareddigudem": "Andhra Pradesh", "Thuraiyur": "Tamil Nadu", "Saltklake": "Andhra Pradesh", "Kaliacahak": "West Bengal", "Sojitra": "Gujarat", "Etmadpur": "Uttar Pradesh", "Narendranagar": "Uttarakhand", "Ranaghat%20-%20I": "West Bengal", "Dalmau": "Uttar Pradesh", "Proddatur": "Andhra Pradesh", "Shahjahanpur": "Uttar Pradesh", "Malerkotla": "Punjab", "Sanand": "Gujarat", "Dalkhola": "West Bengal", "Tirumayam": "Tamil Nadu", "Bhalki": "Karnataka", "Chodavaram": "Andhra Pradesh", "Rudraprayg": "Uttarakhand", "Khundian": "Himachal Pradesh", "Bawani%20Khera": "Haryana", "Palia": "Uttar Pradesh", "Singhbhum": "Jharkhand", "Tarn-taran": "Punjab", "Padampur": "Rajasthan", "Phillaur": "Punjab", "Nabha": "Punjab", "Pochampalli": "Tamil Nadu", "Deobhog": "Chhattisgarh", "Baikara": "West Bengal", "Disa": "Gujarat", "Sihunta": "Himachal Pradesh", "Sachin": "Gujarat", "Pappireddipatti": "Tamil Nadu", "Rajgarah": "Madhya Pradesh", "Dlf%20Ph-iii": "Haryana", "Patna%20Sadar": "Bihar", "Chirala": "Andhra Pradesh", "Perinthalmanna": "Kerala", "Slooni": "Haryana", "Dhandhuka": "Gujarat", "Panthalur": "Kerala", "Saidabad": "Uttar Pradesh", "Rajavommangi": "Andhra Pradesh", "Bicholim": "Goa", "Nawacity": "Rajasthan", "Solapur%20North": "Maharashtra", "Vadgam": "Gujarat", "T%20Narasipura": "Karnataka", "Palakonda": "Andhra Pradesh", "Kanpur%20%20Dehat": "Uttar Pradesh", "Amritsar%20-i": "Punjab", "Nagrakata": "West Bengal", "Bhatkal": "Karnataka", "Jhanduta%28t%29": "Himachal Pradesh", "Machhlishahr": "Uttar Pradesh", "Bamangola": "West Bengal", "Gayzing": "Sikkim", "Dascroi": "Gujarat", "Mishrikh": "Uttar Pradesh", "Kanandala%20Bawada": "Maharashtra", "Domariaganj": "Uttar Pradesh", "Manbazar": "West Bengal", "Mandi%28t%29": "Himachal Pradesh", "Bandlaguda": "Telangana", "Ulundurpet": "Tamil Nadu", "Nirmal": "Telangana", "Kullu%28t%29": "Himachal Pradesh", "Tiruchirapalli": "Tamil Nadu", "Tuticorin": "Tamil Nadu", "Vijayawada%20%28rural%29": "Andhra Pradesh", "Kalyandurg": "Andhra Pradesh", "Madakasira": "Andhra Pradesh", "Lalgudi": "Tamil Nadu", "Sidhpur": "Gujarat", "Mohadi": "Maharashtra", "Kadiyam": "Andhra Pradesh", "Perambur%20Purasawalkam": "Tamil Nadu", "Dehgam": "Gujarat", "Bathinda": "Punjab", "Salt": "Uttar Pradesh", "Hamirpur": "Himachal Pradesh", "Tiruchirappalli": "Tamil Nadu", "Kasaria": "West Bengal", "Mumbai%20%20East": "Maharashtra", "Rangli": "West Bengal", "Jamkhandi": "Karnataka", "Ranikhet": "Uttarakhand", "Jagatdal": "West Bengal", "Chungthang": "Sikkim", "Tuini": "Uttarakhand", "Mathur": "Uttar Pradesh", "Jaisinghpur": "Himachal Pradesh", "Pune%20Moffusil": "Maharashtra", "Powayan": "Uttar Pradesh", "Amritsar": "Punjab", "Bisalpur": "Uttar Pradesh", "Bijhari": "Himachal Pradesh", "Nanjangud": "Karnataka", "Mannarkkad": "Kerala", "Ausgram%20-%20I": "West Bengal", "Swarupnagar": "West Bengal", "Peravurni": "Tamil Nadu", "Kalanwali": "Haryana", "Batala": "Punjab", "Aland": "Karnataka", "Jiwati": "Maharashtra", "Ankleshwar": "Gujarat", "Nahan": "Himachal Pradesh", "Jamkhed": "Maharashtra", "Unjha": "Gujarat", "Lalpur": "Jharkhand", "Patti": "Punjab", "Akberpur": "Uttar Pradesh", "Prathipadu": "Andhra Pradesh", "Chennai": "Tamil Nadu", "Sader": "Madhya Pradesh", "Tirukalilkundram": "Tamil Nadu", "Uluberia%20-%20I": "West Bengal", "Phool%20Pur": "Uttar Pradesh", "Ramkanali": "West Bengal", "Una": "Himachal Pradesh", "Gondia": "Maharashtra", "Dharaupram": "Tamil Nadu", "Tharangambadi": "Tamil Nadu", "Sawayajpur": "Uttar Pradesh", "Sarkaghat%28t%29": "Himachal Pradesh", "Omalur": "Tamil Nadu", "Uthukkottai": "Tamil Nadu", "Gubbi": "Karnataka", "Raghunathpur%20-%20Ii": "West Bengal", "Farrukhabad": "Uttar Pradesh", "Nowda%20%28murshidabad%29": "West Bengal", "Mauda": "Maharashtra", "Hanamkonda": "Telangana", "Karanprayag": "Uttarakhand", "Uttukottai": "Tamil Nadu", "Tiruvallur": "Tamil Nadu", "Sathy": "Tamil Nadu", "Ferozepur": "Punjab", "Savli": "Gujarat", "Raina%20-%20Ii": "West Bengal", "Namakkal": "Tamil Nadu", "Kandivali%20East": "Maharashtra", "Haveli": "Gujarat", "Sahjanwa": "Uttar Pradesh", "Sankari": "Tamil Nadu", "Paramakudi": "Tamil Nadu", "Chittoor": "Andhra Pradesh", "Bankura": "West Bengal", "Yelburga": "Karnataka", "Chhindwara": "Madhya Pradesh", "Mahesana": "Gujarat", "Kanjirappally": "Kerala", "Rajendra%20Nagar": "Bihar", "Kozhikode": "Kerala", "Jhunjhunu": "Rajasthan", "Bhinga": "Uttar Pradesh", "Barsar%28t%29": "Himachal Pradesh", "Sikandar%20Pur": "Bihar", "Tamkuhi%20Raj": "Bihar", "Purandar": "Maharashtra", "Sannad": "Gujarat", "Kunjpura": "Haryana", "Rudauli": "Uttar Pradesh", "Valva": "Gujarat", "Bhanvad": "Gujarat", "Bhimadole": "Andhra Pradesh", "Gooty": "Andhra Pradesh", "Gangoh": "Uttar Pradesh", "Thunag": "Himachal Pradesh", "Basti": "Uttar Pradesh", "Chorayasi": "Gujarat", "Virudhunagar": "Tamil Nadu", "Sathupalli": "Telangana", "Sirpur%20%28t%29": "Maharashtra", "Phansidewa": "Rajshahi Division", "S%20Mydukur": "Andhra Pradesh", "Sullia": "Karnataka", "Laxmipul": "Tripura", "Gurdaspur": "Punjab", "North%2024%20Parganas": "West Bengal", "Dhrol": "Gujarat", "Pune%20City": "Maharashtra", "Sangrah": "Himachal Pradesh", "Phulwari": "Bihar", "Tiruttani": "Tamil Nadu", "Gonda": "Uttar Pradesh", "Nagapattinam": "Tamil Nadu", "Bholath": "Punjab", "Tirupanandal": "Tamil Nadu", "Vansda": "Gujarat", "Machhali%20Shahar": "Uttar Pradesh", "Darjeeling%20Pulbazar": "West Bengal", "Palghar": "Maharashtra", "Karvir": "Maharashtra", "Ludhiana%20%28east%29": "Punjab", "Tondiarpet%20Fort%20St%20George": "Tamil Nadu", "Narsinghpur": "Madhya Pradesh", "Mandvi": "Gujarat", "Vedasandur": "Tamil Nadu", "Alibag": "Maharashtra", "Jharobari%20Block": "Assam", "Hoshangabad": "Madhya Pradesh", "Dhaurahara": "Uttar Pradesh", "Bagh%20Mehtab": "Uttar Pradesh", "Poanta%20Sahib": "Himachal Pradesh", "Panhala": "Maharashtra", "G%20B%20Nagar": "Rajasthan", "Shillong": "Meghalaya", "Gharunda": "Haryana", "Gangavati": "Karnataka", "Zira": "Punjab", "Ramnagar": "Uttarakhand", "Argora": "Jharkhand", "Gyanpur": "Uttar Pradesh", "Survepalli": "Andhra Pradesh", "Bhagha%20Purana": "Punjab", "Tiruvannamalai": "Tamil Nadu", "Mathurapur%20-%20Ii": "Bihar", "Jhandutta": "Himachal Pradesh", "Peraiyur": "Tamil Nadu", "Bhamora": "Uttar Pradesh", "Dera%20Baba%20Nanak": "Punjab", "Ganga%20Ganj": "Uttar Pradesh", "Gajol": "West Bengal", "Karimnagar": "Telangana", "Chandannagar": "West Bengal", "Sangarh": "Himachal Pradesh", "Bngarpet": "Andhra Pradesh", "Pilibanga": "Rajasthan", "Taudhakpur": "Uttar Pradesh", "Didihat": "Uttarakhand", "Papanasam": "Tamil Nadu", "Patrasayer": "West Bengal", "Rangli%20Rangliot": "West Bengal", "Ghat": "Uttar Pradesh", "Suni": "Himachal Pradesh", "Jansath": "Uttar Pradesh", "Dokra": "Jharkhand", "Ranipool": "Sikkim", "Dataganj": "Uttar Pradesh", "Kagal": "Maharashtra", "Mohammdi": "Uttar Pradesh", "Phaphamau": "Uttar Pradesh", "Sriperumbudur": "Tamil Nadu", "Kotdwara": "Uttarakhand", "Udumbanchola": "Kerala", "Debra": "West Bengal", "Jakhnidhar": "Uttarakhand", "Rura": "Uttar Pradesh", "Kamalapuram": "Andhra Pradesh", "Baroh%28t%29": "Himachal Pradesh", "Sonamukhi": "West Bengal", "Coonoor": "Tamil Nadu", "Panskura": "West Bengal", "Chorasi": "Odisha", "Bagalkot": "Karnataka", "Attur": "Tamil Nadu", "Ujjain": "Madhya Pradesh", "Akbarur": "Uttar Pradesh", "Tiloi": "Uttar Pradesh", "Chandpur": "Uttar Pradesh", "Rayachoti": "Andhra Pradesh", "Panruti": "Tamil Nadu", "Banjar": "Himachal Pradesh", "Rajendranagar": "Bihar", "Nakhatrana": "Gujarat", "Faridkot": "Punjab", "Samrala": "Punjab", "Ranebennur": "Karnataka", "Mathabhanga%20-%20Ii": "West Bengal", "Aonla": "Uttar Pradesh", "Someshwar": "Karnataka", "Tangarapali": "Odisha", "Shahapur": "Maharashtra", "Vikasnagar": "Uttarakhand", "Kuttalam": "Tamil Nadu", "Venkatagiri": "Andhra Pradesh", "Vaghoida": "Gujarat", "Tanuku": "Andhra Pradesh", "Indri": "Haryana", "Jainti": "Uttarakhand", "Haridwar": "Uttarakhand", "Rampur%28t%29": "Uttar Pradesh", "Panvel": "Maharashtra", "Tehri": "Uttarakhand", "Asansol": "West Bengal", "Gangarampur": "West Bengal", "Giddarbaha": "Punjab", "Narsipatnam": "Andhra Pradesh", "Akbarpur": "Uttar Pradesh", "Mayiladuthurai": "Tamil Nadu", "Haldia%20Municipality": "West Bengal", "Ghatkesar": "Telangana", "Salanpur": "West Bengal", "Karkala": "Karnataka", "Basirhat%20-%20I": "West Bengal", "Narendernagar": "Uttarakhand", "Lingaraj": "Odisha", "Aurangabad": "Maharashtra", "Assandh": "Haryana", "Nainital": "Uttarakhand", "Sadar%20Mau": "Uttar Pradesh", "Machilipatnam": "Andhra Pradesh", "Dehra": "Rajasthan", "Jhinjhak": "Uttar Pradesh", "Nurpur%28t%29": "Himachal Pradesh", "Udhagamandalam": "Tamil Nadu", "Bhadravati": "Karnataka", "Ambala%20City": "Haryana", "Surajgarh": "Rajasthan", "Kothkhai": "Himachal Pradesh", "Ambajogai": "Maharashtra", "Kopergaon": "Maharashtra", "Ranni": "Kerala", "Qutubullapur": "Telangana", "Hubli": "Karnataka", "Shahganj": "Uttar Pradesh", "Kalka": "Haryana", "Kundah": "Tamil Nadu", "Kunnathunadu": "Kerala", "Bhadrachalam": "Telangana", "Yamuna%20Nagar": "Haryana", "Ranny": "Kerala", "Tadoor": "Telangana", "Kasia": "Uttar Pradesh", "Ambad": "Maharashtra", "Old%20Malda": "West Bengal", "Murshidabad": "West Bengal", "Khairatabad": "Telangana", "Tumsar": "Maharashtra", "Mumbai": "Maharashtra", "Ranibundh": "West Bengal", "Khanakul%202b": "West Bengal", "Betul": "Madhya Pradesh", "Wardha": "Maharashtra", "Campierganj": "Uttar Pradesh", "Oddanchatram": "Tamil Nadu", "New%20Town": "West Bengal", "Bardez": "Goa", "Rohini": "Delhi", "Sompeta%20Mandal": "Andhra Pradesh", "Rajampet": "Andhra Pradesh", "Lal%20Bangla": "Uttar Pradesh", "Narendra%20Nagar": "Uttarakhand", "Mahabubabad": "Telangana", "Hissar": "Haryana", "Bhubaneswar": "Odisha", "Karaikal": "Puducherry", "Cononel%20Ganj": "Uttar Pradesh", "Aswapuram": "Telangana", "Armoor": "Telangana", "Chandausi": "Uttar Pradesh", "Kankurgachi": "West Bengal", "Huzurnagar": "Telangana", "Amroha": "Uttar Pradesh", "Pandalur": "Kerala", "Kanekal": "Andhra Pradesh", "Basgaon": "Uttar Pradesh", "Parasgad": "Karnataka", "Santipur": "West Bengal", "Udamalpet": "Tamil Nadu", "Chapatala": "West Bengal", "Rasipuram": "Tamil Nadu", "Mukerian": "Punjab", "Pedapudi": "Andhra Pradesh", "Rampur%20Bushahr": "Himachal Pradesh", "Aurad%28b%29": "Karnataka", "Nandod": "Rajasthan", "Shaikpet": "Telangana", "Mangrol": "Gujarat", "Nalgonda": "Telangana", "Koraon": "Uttar Pradesh", "Banglore": "Karnataka", "Sandhol%28s%20T%29": "Himachal Pradesh", "Pandua": "West Bengal", "Malvan": "Maharashtra", "Rania": "Uttar Pradesh", "Kandaghat": "Himachal Pradesh", "Kasauli%28t%29": "Himachal Pradesh", "Jagtial": "Telangana", "Pooh": "Himachal Pradesh", "Bankura%20-%20I": "West Bengal", "Bhatapara": "Chhattisgarh", "Dohad": "Gujarat", "Kharagpur": "West Bengal", "Madurai": "Tamil Nadu", "Kakinada": "Andhra Pradesh", "Naxalbari": "West Bengal", "Miraj": "Maharashtra", "Hodal": "Haryana", "Tadipatri": "Andhra Pradesh", "Jhagadia": "Gujarat", "Goghat-ii": "West Bengal", "Hagaribommanahalli": "Karnataka", "Indapur": "Maharashtra", "Guntakal": "Andhra Pradesh", "Gokavaram": "Andhra Pradesh", "Rajgamar": "Chhattisgarh", "Tiruppattur%20-singsmpunariblock": "Tamil Nadu", "Karhal": "Uttar Pradesh", "Delhi%20North": "Delhi", "Radhanagari": "Maharashtra", "Kharagpur-i": "West Bengal", "Visnagar": "Gujarat", "Rawatbhata": "Rajasthan", "Saltlake": "Rajasthan", "Talakondapally": "Telangana", "Asansol%20Mc": "West Bengal", "Barmer": "Rajasthan", "Amberpet": "Telangana", "Indpur": "West Bengal", "Dachepalle": "Andhra Pradesh", "Rajnandgaon": "Chhattisgarh", "Mandi%20Dabwali": "Haryana", "Sujanpur": "Punjab", "Serilingampally": "Telangana", "Ludhiana": "Punjab", "Ariyalur": "Tamil Nadu", "Para": "Haryana", "Mentada": "Andhra Pradesh", "Khammam%20%28urban%29": "Telangana", "Nambal": "Telangana", "Satankulam": "Tamil Nadu", "Indus": "West Bengal", "Sector%20-45": "Chandigarh", "Tehatta%20I": "West Bengal", "Anklesvar": "Gujarat", "Viluppuram": "Tamil Nadu", "Mettur": "Tamil Nadu", "Palus": "Maharashtra", "Fatehabad": "Haryana", "Uttangarai": "Tamil Nadu", "Deoprayag": "Uttarakhand", "Hospet%20Ho": "Karnataka", "Alathur": "Kerala", "Madhira": "Telangana", "Mustabad": "Telangana", "Bisauli": "Uttar Pradesh", "Medikonduru": "Andhra Pradesh", "Khatra": "West Bengal", "Thanjavur": "Tamil Nadu", "Pune%20City%20East": "Maharashtra", "North%20Solapur": "Maharashtra", "Kodur": "Kerala", "Basavakalyan": "Karnataka", "Wai": "Maharashtra", "Ernakulam": "Kerala", "Dhanolti": "Uttarakhand", "Manikchak": "West Bengal", "Kunda": "Uttar Pradesh", "Khachraud": "Madhya Pradesh", "Nilakottai": "Tamil Nadu", "New%20Mumbai": "Maharashtra", "Mandirbazar": "Uttar Pradesh", "Gandhidham": "Gujarat", "Utraula": "Uttar Pradesh", "Madhugiri": "Karnataka", "Unchahar%20%2A%2A": "Uttar Pradesh", "Patan-veraval": "Gujarat", "Khalra": "Punjab", "Aurad%20%28b%29": "Karnataka", "Harishchandrapur": "West Bengal", "Kusmunda": "Chhattisgarh", "Kapadwanj": "Gujarat", "Ottappalam": "Kerala", "Jammalamdugu": "Andhra Pradesh", "Sunam": "Punjab", "Patiali": "Punjab", "Hassan": "Karnataka", "Chengannur": "Kerala", "Kalavad": "Gujarat", "Patiala": "Punjab", "Osmanabad": "Maharashtra", "Sitai": "West Bengal", "Salem": "Tamil Nadu", "Madhuban": "Uttar Pradesh", "Charla": "Rajasthan", "Mahrajganj": "Uttar Pradesh", "Nagayalanka": "Andhra Pradesh", "City": "State", "Balanagar": "Telangana", "Uthiramerur": "Tamil Nadu", "Chejerla": "Andhra Pradesh", "Dhari": "Gujarat", "Chakarnagar%20%2A%2A": "Uttar Pradesh", "Blaspur": "Chhattisgarh", "Jhalda%20-%20Ii": "West Bengal", "Kodair": "Telangana", "Chachyot%28t%29": "Himachal Pradesh", "Tenkasi": "Tamil Nadu", "Nanguneri": "Tamil Nadu", "Jalgaon": "Maharashtra", "Koria": "Uttar Pradesh", "Huzurabad": "Telangana", "Ballarpur": "Maharashtra", "Kherwara": "Rajasthan", "Chola%20Sahib": "Punjab", "Bagda": "West Bengal", "Pardi": "Gujarat", "Palani": "Tamil Nadu", "Krishnagar%20-%20I": "West Bengal", "Murwara": "Madhya Pradesh", "Vagra": "Gujarat", "Kangra%28t%29": "Himachal Pradesh", "Andal": "West Bengal", "Gird": "Madhya Pradesh", "Ponda": "Goa", "Kaprada": "Gujarat", "Amb%28t%29": "Himachal Pradesh", "Anikola": "West Bengal", "Roorkee": "Uttarakhand", "Fatehpur%20Roshnai": "Uttar Pradesh", "Kovilpatti": "Tamil Nadu", "Bhavani": "Tamil Nadu", "Chaukhutia": "Uttarakhand", "Kunnam": "Kerala", "Tiruppur": "Tamil Nadu", "Talappilly": "Kerala", "Dharsiwa": "Chhattisgarh", "Pundri": "Haryana", "Tarbganj": "Uttar Pradesh", "Pathankot": "Punjab", "Banswara": "Rajasthan", "Porumamilla": "Andhra Pradesh", "Budhana": "Uttar Pradesh", "Merta": "Rajasthan", "Kozhencherri": "Kerala", "Kharar": "Punjab", "Chitradurga": "Karnataka", "Rampur": "Uttar Pradesh", "Gobichettipalayam": "Tamil Nadu", "Kozhencherry": "Kerala", "Musheerabad": "Telangana", "Bhorang": "Jharkhand", "Manachanallur": "Tamil Nadu", "Bhoranj": "Himachal Pradesh", "Katpadi": "Tamil Nadu", "Mahuva": "Gujarat", "Surat": "Gujarat", "Dadra%20%26%20Nagar%20Haveli": "Dadra and Nagar Haveli", "Narasannapeta%20Mandal": "Andhra Pradesh", "Barasat%20-%20Ii": "West Bengal", "Musafirkhana": "Uttar Pradesh", "Baghpat": "Uttar Pradesh", "Bidhuna": "Uttar Pradesh", "Jodiya": "Gujarat", "Jamuria": "West Bengal", "Nistoli": "Uttar Pradesh", "Vilathikulam": "Tamil Nadu", "Tiruvanathapuram": "Kerala", "Melur": "Tamil Nadu", "Choryasi": "Gujarat", "Borsad": "Gujarat", "Baramati": "Maharashtra", "Sengottai": "Tamil Nadu", "Ikauna": "Uttar Pradesh", "Ravulapalem": "Andhra Pradesh", "Morbi": "Gujarat", "Bilgram": "Uttar Pradesh", "Bodinayakanur": "Tamil Nadu", "Naijibabad": "Uttar Pradesh", "Unnao": "Uttar Pradesh", "Chakia": "Bihar", "Raiganj": "West Bengal", "Markapur": "Andhra Pradesh", "Raina%20-%20I": "West Bengal", "Nedumangad": "Kerala", "Madurai%20North": "Tamil Nadu", "Koyyalagudem": "Andhra Pradesh", "Indira%20Nagar": "Karnataka", "Uluberia%20-%20Ii": "West Bengal", "Bagmundi": "West Bengal", "Palam%20Vihar": "Haryana", "Nannilam": "Tamil Nadu", "Baraboni": "Uttar Pradesh", "Matigara": "West Bengal", "Bara": "Uttar Pradesh", "Borjora": "West Bengal", "Gadag": "Karnataka", "Agra": "Uttar Pradesh", "Kallakurichi": "Tamil Nadu", "Bharmour": "Himachal Pradesh", "Tiruvanamalai": "Tamil Nadu", "Tadikonda": "Andhra Pradesh", "Alipurduar": "West Bengal", "Thanesar": "Haryana", "Juhi": "Madhya Pradesh", "Bakshi%20Ka%20Talab": "Uttar Pradesh", "Bansi": "Uttar Pradesh", "Tiruchuli": "Tamil Nadu", "Yellapur": "Karnataka", "Afjalpur": "Karnataka", "Dhupguri": "West Bengal", "Raghurajnagar": "Madhya Pradesh", "Maharajang": "Tamil Nadu", "Rakkar": "Himachal Pradesh", "Sunder%20Nagar": "Jharkhand", "Bairia": "Jharkhand", "Turaiyur": "Tamil Nadu", "Belgaum": "Karnataka", "Kallur": "Telangana", "Nanpara": "Uttar Pradesh", "Dapoli": "Maharashtra", "Mallappally": "Kerala", "Phoolpur": "Uttar Pradesh", "Vlr": "Telangana", "Kumharsain%28t%29": "Himachal Pradesh", "Bahadurgarh": "Haryana", "Fateh%20Pur": "Uttar Pradesh", "Hospet": "Karnataka", "Qasba%20Kotla": "Himachal Pradesh", "Musiri": "Tamil Nadu", "Nimbahera": "Rajasthan", "Pandaveshwar": "West Bengal", "Karwar": "Karnataka", "Ponneri": "Tamil Nadu", "Guptipara": "West Bengal", "Lalganj": "Uttar Pradesh", "Jawali%28t%29": "Himachal Pradesh", "Pamarru": "Andhra Pradesh", "Nawalgarh": "Rajasthan", "Gobindpur": "Jharkhand", "Dlf%20Ph-ii": "Haryana", "Dhar": "Madhya Pradesh", "Bangana": "Himachal Pradesh", "Asifnagar": "Telangana", "Yellandu": "Telangana", "Brahmadevam": "Andhra Pradesh", "Puncha": "West Bengal", "Bobbili": "Andhra Pradesh", "Chandigarh": "Chandigarh", "Mau": "Uttar Pradesh", "Tittagudi": "Tamil Nadu", "Sikar": "Rajasthan", "Domjur": "West Bengal", "Dharwad": "Karnataka", "Jangaon": "Telangana", "Edappadi": "Tamil Nadu", "Bhalei": "Uttar Pradesh", "Almora": "Uttarakhand", "Medak": "Telangana", "Mal": "West Bengal", "Man": "Maharashtra", "Chittapur": "Karnataka", "Chandrapur%20Ho": "Tripura", "Sigadam": "Andhra Pradesh", "Kamudhi": "Tamil Nadu", "Parur": "Kerala", "New%20Delhi%20West": "Delhi", "Kothamangalam": "Kerala", "Balarampur": "West Bengal", "Turrrur": "Tamil Nadu", "Mangan": "Sikkim", "Mummidivaram": "Andhra Pradesh", "Ramshahar": "Himachal Pradesh", "Tiruvalla": "Kerala", "Luxettipet": "Telangana", "Sathyamangalam": "Tamil Nadu", "Bhamini": "Andhra Pradesh", "Ranibandh": "West Bengal", "Tiptur": "Karnataka", "Konarpur": "West Bengal", "Tirthahalli": "Karnataka", "Valangaman": "Tamil Nadu", "Bilsi": "Uttar Pradesh", "Venkatapuram": "Andhra Pradesh", "Thirunallar%20Commune%20Panchayat": "Puducherry", "Siyana": "Uttar Pradesh", "Uttarkashi": "Uttarakhand", "Dikchu": "Sikkim", "Narsampet": "Telangana", "Ranaghat-ii": "West Bengal", "Mathura": "Uttar Pradesh", "Saltora": "West Bengal", "Kochi": "Kerala", "Khandwa": "Madhya Pradesh", "Muktsar": "Punjab", "Siwani": "Haryana", "Panchkula": "Haryana", "Kanchili%20Mandal": "Andhra Pradesh", "Tirukkuvalai": "Tamil Nadu", "Tiruchengodu": "Tamil Nadu", "Abi%20Karlpora": "Jammu and Kashmir", "Vedaranyam": "Tamil Nadu", "Chavakkad": "Kerala", "Hangrang": "Himachal Pradesh", "Firozepur": "Punjab", "Tiruchengode": "Tamil Nadu", "Cooch%20Behar": "West Bengal", "Anupshahr": "Uttar Pradesh", "Kaliganj": "West Bengal", "Barrackpur%20-%20Ii": "West Bengal", "Santrampur": "Gujarat", "Mundgod": "Karnataka", "Unchahar": "Uttar Pradesh", "Sangla%28t%29": "Himachal Pradesh", "Lohaghat": "Uttarakhand", "Madarihat": "West Bengal", "Sonipat": "Haryana", "Shyam%20Nagar": "West Bengal", "Sitapur": "Uttar Pradesh", "Aranangi": "Tamil Nadu", "Karjat": "Maharashtra", "Jamnagar": "Gujarat", "Devprayag": "Uttarakhand", "Hardwar": "Uttarakhand", "Bahraich": "Uttar Pradesh", "Kandukur": "Telangana", "T%20Sabo": "Madhya Pradesh", "Rajapalayam": "Tamil Nadu", "Mahabubnagar": "Telangana", "Tirumayaam": "Tamil Nadu", "Junnar": "Maharashtra", "Becharaji": "Gujarat", "Nurpur": "Himachal Pradesh", "Ramsanehighat": "Uttar Pradesh", "Pennagaram": "Tamil Nadu", "Baba%20Bakala": "Punjab", "Kharba": "West Bengal", "Mohammadabad": "Uttar Pradesh", "Tiruvadanai": "Tamil Nadu", "Bairampur": "Uttar Pradesh", "Najibabad": "Uttar Pradesh", "Thovalai": "Tamil Nadu", "Perambalur": "Tamil Nadu", "Solapur%20South": "Maharashtra", "Khandar": "Rajasthan", "Ratangarh": "Rajasthan", "Badvel": "Andhra Pradesh", "Edlapadu": "Andhra Pradesh", "Ghatampur": "Uttar Pradesh", "Srikakulam": "Andhra Pradesh", "Raninagar%20-%20Ii": "West Bengal", "Gokak": "Karnataka", "Pooranpur": "Uttar Pradesh", "Chennai%20City%20Corporation": "Tamil Nadu", "Neemrana": "Rajasthan", "Pali": "Rajasthan", "Nankhari": "Himachal Pradesh", "Amgaon": "Maharashtra", "Malikipuram": "Andhra Pradesh", "Bhatpar%20Rani": "Uttar Pradesh", "Kozhenchery": "Kerala", "Chogawan": "Haryana", "Peddapuram": "Andhra Pradesh", "Junagadh": "Gujarat", "Shivpuri": "Madhya Pradesh", "Bharthana": "Uttar Pradesh", "Sattari": "Goa", "Bardoli": "Gujarat", "Misrikh": "Uttar Pradesh", "Bangana%28t%29": "Himachal Pradesh", "Pukhrayan": "Uttar Pradesh", "Lambhua": "Uttar Pradesh", "Rameswaram": "Tamil Nadu", "Mahemdavad": "Gujarat", "Mhow": "Madhya Pradesh", "Nakodar": "Punjab", "Pangi": "Himachal Pradesh", "Arani": "Tamil Nadu", "Radhapuram": "Tamil Nadu", "Sultanpur%20Lodhi": "Punjab", "Chhatargarh": "Uttar Pradesh", "Naugarh": "Uttar Pradesh", "Pauri": "Uttarakhand", "Chopra": "Madhya Pradesh", "Sahajalalpur": "Bihar", "Durgapur%20Mc": "Delhi", "Kullu": "Himachal Pradesh", "Nellore": "Andhra Pradesh", "Aranthangi": "Tamil Nadu", "Goalpukher": "West Bengal", "Machhali%20Shshar": "Uttar Pradesh", "Rampurhat%20-%20I": "West Bengal", "Tamluk": "West Bengal", "Usilampatti": "Tamil Nadu", "Sattur": "Tamil Nadu", "Thalassery": "Kerala", "Jhajjar": "Haryana", "Kurupam": "Andhra Pradesh", "Garhbeta": "West Bengal", "Hukeri": "Karnataka", "Korba": "Chhattisgarh", "Yerraguntla": "Andhra Pradesh", "Peermade": "Kerala", "Cheyyar": "Tamil Nadu", "Nelamangala": "Karnataka", "Nabadwip": "West Bengal", "Vangoor": "Telangana", "Guskara": "West Bengal", "Agrico": "Jharkhand", "Vasai": "Maharashtra", "Athni": "Karnataka", "Barsar": "Himachal Pradesh", "Palsanda": "West Bengal", "Sahauran": "Punjab", "Sadar": "Maharashtra", "Mrg": "Kerala", "Cuddapah": "Andhra Pradesh", "Ghosi": "Uttar Pradesh", "Indora": "Madhya Pradesh", "Villupuram": "Tamil Nadu", "Kalkulam": "Tamil Nadu", "Chhatri": "Rajasthan", "Chennai%20City%20South": "Tamil Nadu", "Moonak": "Punjab", "Jalandhar%20-%20I": "Punjab", "Ballabgarh": "Haryana", "Sirsi": "Karnataka", "Matteli": "Kerala", "Mangalagiri": "Andhra Pradesh", "Sirsa": "Haryana", "Haripal": "West Bengal", "Odhan": "Haryana", "Palitana": "Gujarat", "Sampatchak": "Bihar", "Taliparamba": "Kerala", "Harur": "Tamil Nadu", "Chakar%20Nagar": "Uttar Pradesh", "Vadali": "Andhra Pradesh", "Jogeshwari%20West": "Maharashtra", "Chunar": "Uttar Pradesh", "Gorakhpur%20Sadar": "Madhya Pradesh", "Sikanderpur": "Uttar Pradesh", "Ausgram%20-%20Ii": "West Bengal", "Rangareddy": "Telangana", "Samana": "Punjab", "Khanna": "Punjab", "Gandarvakottai": "Tamil Nadu", "Stn%20%20Jadcherla": "Telangana", "Avanigadda": "Andhra Pradesh", "Govind%20Nagar": "Uttar Pradesh", "Ajnala": "Punjab", "Borivali%20East": "Maharashtra", "Khajni": "Uttar Pradesh", "Saharanpur": "Uttar Pradesh", "Sagri": "Madhya Pradesh", "Vaniyambadi": "Tamil Nadu", "Kajlagarh": "West Bengal", "Chapra": "Bihar", "Mullanpur": "Punjab", "Saifai": "Uttar Pradesh", "Naina%20Devi": "Himachal Pradesh", "Kalyan": "Maharashtra", "Jetpur": "Gujarat", "Sheoli": "Uttar Pradesh", "Ramagundam": "Telangana", "Digha": "West Bengal", "Gandhinagar": "Gujarat", "Binpur-i": "West Bengal", "Kasarawad": "Madhya Pradesh", "Sambhl": "Uttar Pradesh", "Goghat-i": "West Bengal", "Kaiserganj": "Rajasthan", "Shivrajpur": "Uttar Pradesh", "Pilibhit": "Uttar Pradesh", "Humnabad": "Karnataka", "Pilibangan": "Rajasthan", "Natham": "Tamil Nadu", "Bhanoli": "Uttarakhand", "Palasbari%20Circle": "Assam", "Galsi%20-%20I": "West Bengal", "New%20Delhi%20South%20West": "Delhi", "Dod%20Ballapur": "Karnataka", "Khurja": "Uttar Pradesh", "Pratapnagar": "Rajasthan", "Murbad": "Maharashtra", "Sainj%28s%20T%29": "Himachal Pradesh", "Sathankulam": "Tamil Nadu", "Tasgaon": "Maharashtra", "Dindori": "Madhya Pradesh", "Nighasan": "Uttar Pradesh", "Dhapa": "West Bengal", "Sikandarpur": "Uttar Pradesh", "Tada": "Andhra Pradesh", "Petlad": "Gujarat", "Chanditala%20-%20I": "West Bengal", "East%20Singhbhum": "Jharkhand", "Shirol": "Maharashtra", "Visakhapatnam%20%28rural%29": "Andhra Pradesh", "Arcot": "Tamil Nadu", "Guna": "Madhya Pradesh", "Kancheepuram": "Tamil Nadu", "Srikaranpur": "Rajasthan", "Amadalavalasa": "Andhra Pradesh", "Berhampore": "West Bengal", "Indore": "Madhya Pradesh", "Tijara": "Rajasthan", "Lalat": "West Bengal", "Pratapgarh": "Rajasthan", "Mudukulathur": "\u0ba4\u0bae\u0bbf\u0bb4\u0bcd\u0ba8\u0bbe\u0b9f\u0bc1", "Ambattur": "Tamil Nadu", "Indas": "West Bengal", "Rudaui": "Uttar Pradesh", "Koppal": "Karnataka", "Khatav": "Maharashtra", "Shimla%20R": "Himachal Pradesh", "Tirupur": "Tamil Nadu", "Jalesher": "Uttar Pradesh", "Kadaladi": "Tamil Nadu", "Haldwani": "Uttarakhand", "Khanapur": "Karnataka", "Churu": "Rajasthan", "Yadgiri": "Karnataka", "Nankhari%28s%20T%29": "Himachal Pradesh", "Pudukkottai": "Tamil Nadu", "Habibpur": "Bihar", "North%2024%20Paraganas": "West Bengal", "Vizianagaram": "Andhra Pradesh", "Jayamkondacholapuram": "Tamil Nadu", "Kheda": "Gujarat", "Mohanlalganj": "Uttar Pradesh", "Chopal": "Himachal Pradesh", "Chirayinkeezhu": "Kerala", "Manali%28t%29": "Himachal Pradesh", "Theog": "Himachal Pradesh", "Panskura-ii": "West Bengal", "Harihar": "Karnataka", "Nawda": "Bihar", "Pathapatnam": "Andhra Pradesh", "Ernad": "Kerala", "Virakerlamapudur": "Tamil Nadu", "Kangayam": "Tamil Nadu", "Seri%20Lingampally": "Telangana", "Anapur": "Uttar Pradesh", "Mekhliganj": "West Bengal", "Borivali%20West": "Maharashtra", "Kuttanadu": "Kerala", "Mandangad": "Maharashtra", "Srirangapatna": "Karnataka", "Barrackpore": "West Bengal", "Piler": "Mizoram", "Kunnathunad": "Kerala", "Tamluk-i": "West Bengal", "Sulthan%20Batheri": "Kerala", "G%20T%20Road": "Uttar Pradesh", "Mehnagar": "Uttar Pradesh", "Ratua-ii": "West Bengal", "Hoshiar%20Pur": "Punjab", "Lingasugur": "Karnataka", "Gosaba": "West Bengal", "Baund": "Haryana", "Udayagiri": "Andhra Pradesh", "Muvattupuzha": "Kerala", "Patan": "Gujarat", "Gairsain": "Uttarakhand", "Gondiya": "Maharashtra", "Chharrah": "West Bengal", "Bhatwari": "Uttarakhand", "North%20Presidency": "Tamil Nadu", "Chandangar": "Telangana", "Hosur": "Tamil Nadu", "Jalandhar": "Punjab", "Kalmeshwar": "Maharashtra", "Rahargora": "Jharkhand", "Handia": "Uttar Pradesh", "Garividi": "Andhra Pradesh", "Sanat%20Nagar": "Telangana", "Karunagapally": "Kerala", "Alamuru": "Andhra Pradesh", "Walaja": "Tamil Nadu", "Auraiya": "Uttar Pradesh", "Ajmer": "Rajasthan", "Pollachi": "Tamil Nadu", "Jorethang": "Sikkim", "Gwalior": "Madhya Pradesh", "Aurad": "Karnataka", "Gola": "Uttar Pradesh", "Nadia%20South": "West Bengal", "Bikaner": "Rajasthan", "Dera%20Bassi": "Punjab", "Jhanduta": "Himachal Pradesh", "Vip%20Nagar": "West Bengal", "Kodavalur": "Andhra Pradesh", "Molakalmuru": "Karnataka", "Loharu": "Haryana", "Thiruvarur": "Tamil Nadu", "Davanagere": "Karnataka", "Sohawal": "Madhya Pradesh", "Gohad": "Madhya Pradesh", "Sankarapuram": "Tamil Nadu", "Ongole": "Andhra Pradesh", "Hariharpara": "West Bengal", "Srirampur": "West Bengal", "Battala": "Punjab", "Tiruvidaimarudur": "Tamil Nadu", "Dhampur": "Uttar Pradesh", "Ramanathapuram": "Tamil Nadu", "Yadamarri": "Andhra Pradesh", "Kudligi": "Karnataka", "Bhor": "Maharashtra", "Jalpaiguri": "West Bengal", "Panskura-i": "West Bengal", "North%2024%20Pgs": "West Bengal", "Shorapur": "Karnataka", "Burhanpur": "Madhya Pradesh", "Nakashipara": "West Bengal", "Srivaikuntam": "Tamil Nadu", "Chiplun": "Maharashtra", "Virakeralampudur": "Tamil Nadu", "Polur": "Tamil Nadu", "Dharmapuri": "Tamil Nadu", "Champahati": "West Bengal", "Kalimpong": "West Bengal", "Naraingarh": "Haryana", "Bodhan": "Telangana", "Kalimpong%20-i": "West Bengal", "Yellpur": "Karnataka", "Godhra": "Gujarat", "Hansi": "Haryana", "Soraon": "Uttar Pradesh", "Bahadurpura": "Telangana", "Pachhad": "Maharashtra", "Darjeeling": "West Bengal", "Jogeshwari%20East": "Maharashtra", "Tekkali": "Andhra Pradesh", "Barhaj": "Uttar Pradesh", "Kutki": "Maharashtra", "Kangra": "Himachal Pradesh", "Kotalpur": "West Bengal", "Kavali": "Andhra Pradesh", "Balagarh": "West Bengal", "Nagpur%20%28urban%29": "Maharashtra", "Pattukottai": "Tamil Nadu", "Khem%20Karan": "Punjab", "Kasganj": "Uttar Pradesh", "Etah": "Uttar Pradesh", "Mandsaur": "Madhya Pradesh", "Bilgi": "Karnataka", "Dunda": "Punjab", "Krishnarayapuram": "Tamil Nadu", "Arambagh": "West Bengal", "Annavasal": "Tamil Nadu", "Tallapudi%20Mandalam": "Andhra Pradesh", "Tumkur": "Karnataka", "Farenda": "Uttar Pradesh", "Nautanwa": "Uttar Pradesh", "Baheri": "Uttar Pradesh", "Chintalapudi": "Andhra Pradesh", "Parsibagan": "West Bengal", "Fatehpur": "Uttar Pradesh", "Salcate": "Goa", "Birbhum": "West Bengal", "Parvathipuram": "Andhra Pradesh", "Chidambaram": "Tamil Nadu", "Bhandara": "Maharashtra", "Kanjirapally": "Kerala", "D%20Tirumala": "Andhra Pradesh", "Mumbai%20%20North%20East": "Maharashtra", "Manjhanpur": "Uttar Pradesh", "Serampur%20Uttarpara": "West Bengal", "Paloncha": "Telangana", "Badami": "Karnataka", "Simlapal": "West Bengal", "Goregaon%20West": "Maharashtra", "Valangaiman": "Tamil Nadu", "Thirukkuvalai": "Tamil Nadu", "Kodavasal": "Tamil Nadu", "Nichar%28t%29": "Himachal Pradesh", "Sangmeshwar": "Maharashtra", "Bhatinda": "Punjab", "Udhna": "Gujarat", "Ettayapuram": "Tamil Nadu", "Beas": "Punjab", "Buchireddypalem": "Andhra Pradesh", "Barasat%20-%20I": "West Bengal", "Kulathur": "Tamil Nadu", "Kumbakonam": "Tamil Nadu", "Londa": "Karnataka", "Gangavalli": "Tamil Nadu", "Tilhar": "Uttar Pradesh", "Coimbatore%20South": "Tamil Nadu", "Deshbandhunagar": "West Bengal", "Rudraprayag": "Uttarakhand", "Bijapur": "Karnataka", "Raikal": "Telangana", "Malad%20East": "Maharashtra", "Khundian%28t%29": "Himachal Pradesh", "Parseoni": "Maharashtra", "Jugsalai": "Jharkhand", "Kalchini": "West Bengal", "Jorebunglow%20Sukiapokhri": "West Bengal", "Mangolkote": "West Bengal", "Jaggampeta": "Andhra Pradesh", "Murardih": "Bihar", "Morar": "Himachal Pradesh", "Hatkanangale": "Maharashtra", "Raniganj": "West Bengal", "Tiruvidamarudur": "Tamil Nadu", "Thiruvananthapuram": "Kerala", "Lunawada": "Gujarat", "Kottarakara": "Kerala", "Laudoha": "West Bengal", "Uttaripura": "Uttar Pradesh", "Sithanagaram": "Andhra Pradesh", "Bairi%20Gaon": "Uttarakhand", "Pondicherry": "Puducherry", "Mawal": "Rajasthan", "Bkh": "Maharashtra", "Kanayannur": "Kerala", "Itwa": "Uttar Pradesh", "Chinsurah%20-%20Magra": "West Bengal", "Mankapur": "Uttar Pradesh", "Balachaur": "Punjab", "Bageshwar": "Uttarakhand", "Bhogaon": "Maharashtra", "Kandi": "West Bengal", "Paramathi-velur": "Tamil Nadu", "Bilhaur": "Uttar Pradesh", "Chandanpur": "Odisha", "Kanda": "Haryana", "Jakhnidharr": "Uttarakhand", "Derabassi": "Punjab", "Jakhania": "Gujarat", "Aluva": "Kerala", "Sultanpur": "Uttar Pradesh", "Dhanaura": "Uttar Pradesh", "Ghansali": "Uttarakhand", "Theni": "Tamil Nadu", "Hyd": "Telangana", "Gundluper": "Karnataka", "Umbergaon": "Gujarat", "Kumarganj": "West Bengal", "Kumargram": "West Bengal", "Bishnupur%20-%20I": "Manipur", "Darbhanga": "Bihar", "Kodungallur": "Kerala", "Kavathe%20Mahankal": "Maharashtra", "Jewargi": "Karnataka", "Katni": "Madhya Pradesh", "Bundwan": "West Bengal", "Dindigul": "Tamil Nadu", "Wadhwancity": "Maharashtra", "Hanskhali": "West Bengal", "Sullurpeta": "Andhra Pradesh", "Mandya": "Karnataka", "Mathabhanga": "West Bengal", "Maynaguri": "West Bengal", "Mettupalayam": "Tamil Nadu", "Nagal": "Punjab", "Visakhapatnam": "Andhra Pradesh", "Guhla": "Haryana", "Rajahmundry%20%28urban%29": "Andhra Pradesh", "Vriddhachalam": "Tamil Nadu", "Muddebihal": "Karnataka", "Uthamapalayam": "Tamil Nadu", "Adoni": "Andhra Pradesh", "Joshimath": "Uttarakhand", "Chandauli": "Uttar Pradesh", "Khed": "Maharashtra", "Gara": "Andhra Pradesh", "Pathanapuram": "Kerala", "Vilavancode": "Tamil Nadu", "Vaikom": "Kerala", "Rajkot": "Gujarat", "Renigunta": "Andhra Pradesh", "Bailhongal": "Karnataka", "Nirmand": "Himachal Pradesh", "Sausar": "Madhya Pradesh", "Khakurda": "West Bengal", "Nidhlaul": "Uttar Pradesh", "Anantapur": "Andhra Pradesh", "Maur": "Punjab", "Kadambagachi": "West Bengal", "Daund": "Maharashtra", "Kanpur%20Dehat": "Uttar Pradesh", "Jewer": "Haryana", "Rajgarhi": "Uttarakhand", "Puttur": "Karnataka", "Kotda%20Sanghani": "Gujarat", "Dharamsala": "Himachal Pradesh", "Aliganj": "Uttar Pradesh", "Thirumayam": "Tamil Nadu", "Habra%20-%20I": "West Bengal", "Avanashi": "Tamil Nadu", "Mariahun": "Uttar Pradesh", "Chakdah": "West Bengal", "Macherla": "Andhra Pradesh", "Tharali": "Uttarakhand", "Rajaund": "Haryana", "Tufanganj": "West Bengal", "Haveri": "Karnataka", "Baneswarpur": "West Bengal", "Sadasivpet": "Telangana", "Koratagere": "Karnataka", "Sankhavaram": "Andhra Pradesh", "Abu%20Road": "Rajasthan", "Dubrajpur": "West Bengal", "Malsiras": "Maharashtra", "Rajahmundry%20Rural": "Andhra Pradesh", "Taldangra": "West Bengal", "Shimla": "Himachal Pradesh", "Manvi": "Karnataka", "Amb": "Himachal Pradesh", "Kulpi": "West Bengal", "Vandavasi": "Tamil Nadu", "Tiljala": "West Bengal", "Ulhasnagar": "Maharashtra", "Devgad": "Maharashtra", "Harike": "Punjab", "Maduravoyal": "Tamil Nadu", "Laharpur": "Uttar Pradesh", "Panipat": "Haryana", "Kanigiri": "Andhra Pradesh", "Berinag": "Uttarakhand", "Buchireddypalem%20Mandalam": "Andhra Pradesh", "Ichchapuram%20Mandal": "Andhra Pradesh", "Haringhata": "West Bengal", "Hb%20Halli": "Karnataka", "Sivaganga": "Tamil Nadu", "Thali%20Sain": "Uttarakhand", "Chirawa": "Rajasthan", "Bilari": "Uttar Pradesh", "Kattumannarkoil": "Tamil Nadu", "Tiruvuru": "Andhra Pradesh", "Umreth": "Gujarat", "Yellareddy": "Telangana", "Kalyanpur": "Uttar Pradesh", "Bhai%20Rupa": "Punjab", "Bhavnagar": "Gujarat", "Sehore": "Madhya Pradesh", "Chhachhrauli": "Haryana", "Galleria%20Dlf-iv": "Haryana", "Thrissur": "Kerala", "Karimpur%20I": "West Bengal", "Gorantla": "Andhra Pradesh", "Magra": "Bihar", "Padrauna": "Uttar Pradesh", "Tindivanam": "Tamil Nadu", "Naidupeta": "Andhra Pradesh", "Ramchandrapur%20Khaspur": "West Bengal", "Jabalpur": "Madhya Pradesh", "Raisinghnagar": "Rajasthan", "Bhanpur": "Uttar Pradesh", "Jhargram": "West Bengal", "Shirur": "Maharashtra", "Kannur": "Kerala", "Basti%20East": "Uttar Pradesh", "Jaynagar%20-%20I": "Bihar", "Otapidaram": "Tamil Nadu", "Shahkot": "Punjab", "Khalilabad": "Uttar Pradesh", "Ranaghat-i": "West Bengal", "Balrampur": "Uttar Pradesh", "Cheyur": "Tamil Nadu", "Kalayat": "Haryana", "Ambarnath": "Maharashtra", "Manamelkudi": "Tamil Nadu", "Jhandutha": "Himachal Pradesh", "Munshipurwa": "Uttar Pradesh", "Vadakara": "Kerala", "Mandore": "Rajasthan", "Shohratgarh": "Uttar Pradesh", "Coimbatore%20North": "Tamil Nadu", "Thodupuzha": "Kerala", "Tirukalikundram": "Tamil Nadu", "Jaunpur": "Uttar Pradesh","Laundi": "Madhya Pradesh", "Daudnagar": "Bihar", "Kachugaon": "Assam", "Kondapalli": "Andhra Pradesh", "Dharmabad": "Maharashtra", "Prakasam": "Andhra Pradesh", "Pakhanjore": "Chhattisgarh", "Ranavav": "Gujarat", "Narla": "Chhattisgarh", "Mylavaram": "Andhra Pradesh", "Rupsi": "Rajasthan", "Baloda": "Chhattisgarh", "Nathnager": "Bihar", "Talala": "Gujarat", "Bhind": "Madhya Pradesh", "Dongargaon": "Chhattisgarh", "Pullampeta": "Andhra Pradesh", "Jamankira": "Odisha", "Barodia%20Kumaria": "Rajasthan", "Agali": "Andhra Pradesh", "Newasa": "Maharashtra", "Chewara": "Bihar", "Raipura": "Chhattisgarh", "Chittamur": "Tamil Nadu", "Gopadbanas": "Madhya Pradesh", "Boitamari": "Assam", "Sarangpur": "Gujarat", "Mokokchung": "Nagaland", "Rlegaon": "Andhra Pradesh", "Ipuru": "Andhra Pradesh", "Motipur": "Bihar", "Kotananduru": "Andhra Pradesh", "Smit": "Meghalaya", "Bilkhawthlir": "Mizoram", "Vellaturu": "Andhra Pradesh", "Ampati": "Meghalaya", "Muzaffarpur": "Bihar", "Rajura": "Maharashtra", "Ellanthkunta": "Telangana", "Mehkar": "Maharashtra", "Pandarak": "Bihar", "Mohla": "Chhattisgarh", "Barkatha": "Jharkhand", "Nagshankar": "Assam", "Kiraoli": "Uttar Pradesh", "Marwan": "Bihar", "Vunguturu": "Andhra Pradesh", "Maihar": "Madhya Pradesh", "Lalitpur": "Uttar Pradesh", "Rajupalem": "Andhra Pradesh", "Chhuikhadan": "Chhattisgarh", "Mohol": "Maharashtra", "Padru": "Rajasthan", "Naigaon": "Maharashtra", "Khijersarai": "Bihar", "Dhariawad": "Rajasthan", "Barwani": "Madhya Pradesh", "Poraiyahat": "Jharkhand", "Bodh%20Gaya": "Bihar", "Baikunthapur": "West Bengal", "Bhinmal": "Rajasthan", "Maripeda": "Telangana", "Peint": "Maharashtra", "Kondapuram": "Andhra Pradesh", "Darak": "Punjab", "Fatwah": "Bihar", "Abhanpur": "Chhattisgarh", "Chatrai": "Andhra Pradesh", "Tena": "Uttar Pradesh", "Simri%20Bakhtiarpur": "Bihar", "Nandura": "Maharashtra", "Lakhisarai": "Bihar", "Osian": "Rajasthan", "Basia": "Jharkhand", "Fulbari": "West Bengal", "Ralegaon": "Maharashtra", "Niwas": "Madhya Pradesh", "Tadvai": "Telangana", "Chandur%20Railway": "Maharashtra", "Angrail": "West Bengal", "Karanjia": "Odisha", "Rajgangpur": "Odisha", "Allur": "Andhra Pradesh", "Kodala": "Odisha", "Sadak%20Arjuni": "Maharashtra", "Bhuabichhiya": "Rajasthan", "Colgong": "Bihar", "Tajpur": "Bihar", "Umsning": "Meghalaya", "Lahladpur": "Bihar", "Sukantanagar": "West Bengal", "Sadulshahar": "Rajasthan", "Bermo": "Jharkhand", "Sutrapada": "Gujarat", "Asika": "Odisha", "Meghraj": "Gujarat", "Panchmile": "Assam", "Gambhiraopet": "Telangana", "Paroo": "Bihar", "Amarwara": "Madhya Pradesh", "Nimapara": "Odisha", "Seorinarayan": "Chhattisgarh", "Kesaria": "Bihar", "Farakka": "West Bengal", "Bedeti": "Assam", "Luni": "Rajasthan", "Khilchipur": "Madhya Pradesh", "Dighwara": "Bihar", "Kodakandal": "Tamil Nadu", "Hirmi": "Chhattisgarh", "Mankachar": "Assam", "Chhura": "Chhattisgarh", "Dhula": "Assam", "Chakai%20So": "Bihar", "Koira": "Odisha", "Bhasma": "Odisha", "Mandal": "Gujarat", "Palam": "Maharashtra", "Vaibhavwadi": "Maharashtra", "H%20Kharagpur": "West Bengal", "Marowa": "Assam", "Parlakhemundi": "Odisha", "Janjgir": "Chhattisgarh", "Khuldabad": "Maharashtra", "Kamlang%20Nagar": "Delhi", "Stuvartpuram": "Andhra Pradesh", "Tondur": "Andhra Pradesh", "Danta": "Gujarat", "Ranapur": "Madhya Pradesh", "Jhabua": "Madhya Pradesh", "Dhaka": "Bihar", "Dikom": "Assam", "Chumukedima": "Nagaland", "Umari": "Maharashtra", "Shrigonda": "Maharashtra", "Anantavaram": "Andhra Pradesh", "Mungeli": "Chhattisgarh", "Muktainagar": "Maharashtra", "Sribijeynagar": "Rajasthan", "Tirumalgiri": "Telangana", "Manubolu": "Andhra Pradesh", "Badnawar": "Madhya Pradesh", "Begamganj": "Madhya Pradesh", "Atlur": "Andhra Pradesh", "Singheshwar": "Bihar", "Banpur": "West Bengal", "Nandapur": "Odisha", "Umsaw": "Meghalaya", "Todabhim": "Rajasthan", "Kuderu": "Karnataka", "Biharsharif": "Bihar", "Karakat": "Bihar", "Kanti": "Bihar", "Churachandpur": "Manipur", "Koida": "Uttar Pradesh", "Raghunathganj%20-%20Ii": "Madhya Pradesh", "Sitamau": "Madhya Pradesh", "Kurtha": "Bihar", "Tanakallu": "Andhra Pradesh", "Patoda": "Maharashtra", "Chuchuyimlang": "Nagaland", "Tadimarri": "Andhra Pradesh", "Yawal": "Maharashtra", "Narkher": "Maharashtra", "Haspura": "Bihar", "Bettiah": "Bihar", "Barakhama": "Odisha", "Anandabazar": "Assam", "Mahulpalli": "Odisha", "Mahagama": "Jharkhand", "Barhiya": "Bihar", "Roing": "Arunachal Pradesh", "Jhanjharpur": "Bihar", "Dariapur": "Gujarat", "Jamui": "Bihar", "Srisailam": "Andhra Pradesh", "Jamua": "Jharkhand", "Gangrar": "Rajasthan", "Malhargarh": "Madhya Pradesh", "Durgapur": "West Bengal", "Simulia": "Odisha", "Muhuripur": "Tripura", "Bestawaripeta": "Andhra Pradesh", "Balijana": "Assam", "Chamorshi": "Maharashtra", "Kirnapur": "Madhya Pradesh", "Umarpada": "Gujarat", "Tamnar": "Chhattisgarh", "Umiam": "Meghalaya", "Kirmira": "Odisha", "Hindupur": "Andhra Pradesh", "Ormanjhi": "Jharkhand", "Ranka%20Raj": "Maharashtra", "Akoda": "Madhya Pradesh", "South%20Solapur": "Maharashtra", "Harnaut": "Bihar", "Gokinepalli": "Telangana", "Bairgania": "Bihar", "Indukurpeta": "Andhra Pradesh", "Meharma": "Jharkhand", "Kothaguda": "Telangana", "Bramhapuri": "Maharashtra", "Karra": "Jharkhand", "Galiveedu": "Andhra Pradesh", "Marhaura": "Bihar", "Man%20%28dahiwadi%29": "Maharashtra", "Bikramganj": "Bihar", "Sidhout": "Andhra Pradesh", "Masaurhi": "Bihar", "Kalamnuri": "Maharashtra", "Dhorimana": "Rajasthan", "Japla": "Jharkhand", "Uludanga": "West Bengal", "Rajnagar": "Tripura", "Chamaria": "Haryana", "Sapotara": "Rajasthan", "Vemula": "Andhra Pradesh", "Guduru": "Andhra Pradesh", "Revelganj": "Bihar", "Paradip": "Odisha", "Lanja": "Maharashtra", "Pakur": "Jharkhand", "Rasmi": "Rajasthan", "Modasa": "Gujarat", "Mamidikuduru": "Andhra Pradesh", "Yeola": "Maharashtra", "Bijnapally": "Telangana", "Berla": "Chhattisgarh", "Longding": "Arunachal Pradesh", "Kandhar": "Maharashtra", "Hansot": "Gujarat", "Malahara": "Uttar Pradesh", "Sironcha": "Maharashtra", "Jetaran": "Rajasthan", "Chandaka": "Odisha", "Borigumma": "Odisha", "Gandepalli": "Andhra Pradesh", "Tangi%20Choudwar": "Odisha", "Manavadar": "Gujarat", "Barbigha": "Bihar", "Kankinara": "West Bengal", "Thungathurthy": "Telangana", "Sipajhar": "Assam", "Thungathurthi": "Telangana", "Katoria": "Bihar", "Gilund": "Rajasthan", "Ariyari": "Uttar Pradesh", "Barda": "Gujarat", "Sayra": "Rajasthan", "Takhatpur": "Chhattisgarh", "Sursand": "Bihar", "Buhana": "Rajasthan", "Kharod": "Chhattisgarh", "Shella": "Gujarat", "Satbarwa": "Jharkhand", "Bant": "Odisha", "Warisaliganj": "Bihar", "Enkoor": "Telangana", "Manendragarh": "Chhattisgarh", "Dangarmakha": "Assam", "Jamtara": "Jharkhand", "Bano": "Jharkhand", "Rajaun": "Bihar", "Kamrej": "Gujarat", "Jadcherla": "Telangana", "Prithvipur": "Uttarakhand", "Sitamarhi": "Bihar", "Basna": "Chhattisgarh", "Bayyaram": "Telangana", "Susner": "Madhya Pradesh", "Ganki": "Tripura", "Nuagaon": "Odisha", "Barsahi": "Maharashtra", "Areraj": "Bihar", "Kishannagar": "Telangana", "Sankarakhole": "Odisha", "Puthalpattu": "Andhra Pradesh", "Majalgaon": "Maharashtra", "Wani": "Maharashtra", "Shikohabad": "Uttar Pradesh", "Akuluto": "Nagaland", "Vengurla": "Maharashtra", "Hariharganj": "Jharkhand", "Chakradharpur": "Jharkhand", "Devendra%20Nagar": "Madhya Pradesh", "R%20%20Saidpur": "Uttar Pradesh", "Rahuri": "Maharashtra", "Iswarigacha": "West Bengal", "Tamar": "Jharkhand", "Maksudangarh": "Madhya Pradesh", "Moubhandar": "Jharkhand", "Rajgarh": "Madhya Pradesh", "Nallikaddur": "Telangana", "Hardibazar": "Chhattisgarh", "Palera": "Madhya Pradesh", "Bid": "Maharashtra", "Hatidhura": "\u0985\u09b8\u09ae", "Samdari": "Rajasthan", "Nekarikallu": "Andhra Pradesh", "Nardiganj": "Bihar", "Palojori": "Jharkhand", "Aau": "Rajasthan", "Nanpur": "Bihar", "Mohanpur": "Uttar Pradesh", "Nalkheda": "Madhya Pradesh", "Mahishi": "Bihar", "Goalpara": "Assam", "Dhamanagar": "Odisha", "Peren": "Nagaland", "Kolibira": "Odisha", "Rentachintala": "Andhra Pradesh", "Kasrawad": "Madhya Pradesh", "Nagda": "Madhya Pradesh", "Nagaon": "Assam", "Vikramgad": "Maharashtra", "Pali%20Marwar": "Rajasthan", "Ainavilli": "Andhra Pradesh", "Manikpur": "Uttar Pradesh", "Sohna": "Haryana", "Samudrapur": "Maharashtra", "Ashta": "Madhya Pradesh", "Nutakki": "Andhra Pradesh", "Balumath": "Jharkhand", "Govindaraopet": "Telangana", "Veeraballe": "Andhra Pradesh", "Lakhtar": "Gujarat", "Jatara": "Madhya Pradesh", "Tinsukia": "Assam", "Radhakishorepur": "Odisha", "Mangalvedha": "Maharashtra", "Kannad": "Maharashtra", "Haweli%20Kharagpur": "Bihar", "Multai": "Madhya Pradesh", "Ashti": "Maharashtra", "Santalpur": "Gujarat", "Peddapanjani": "Andhra Pradesh", "Khujner": "Madhya Pradesh", "Gariaband": "Chhattisgarh", "Amod": "Gujarat", "Dasada": "Gujarat", "Sultanganj": "Bihar", "Kapasan": "Rajasthan", "Turumella": "Andhra Pradesh", "Rehli": "Madhya Pradesh", "Madanpur%20Rampur": "Odisha", "Cherukupalli": "Andhra Pradesh", "A%20S%20Peta": "Maharashtra", "Kakumanu": "Andhra Pradesh", "Chainpur": "Bihar", "Panduka": "Chhattisgarh", "Gudlavalleru": "Andhra Pradesh", "Bhupalsagar": "Rajasthan", "Gingia": "Assam", "Pavijetpur": "Gujarat", "Dongargarh": "Chhattisgarh", "Sirajuli": "Assam", "Kalimela": "Odisha", "Buchannapet": "Telangana", "Parwathagiri": "Telangana", "Shahuwadi": "Maharashtra", "Duggondi": "Telangana", "Nuzendla": "Andhra Pradesh", "Purnea": "Bihar", "Pathorighat": "Assam", "Simga": "Chhattisgarh", "Khedacherra": "Tripura", "Brahmamgarimattam": "Andhra Pradesh", "Rompicherla": "Andhra Pradesh", "Baloda%20Bazar": "Chhattisgarh", "Pallahara": "Odisha", "Basirhat%20-%20Ii": "West Bengal", "B%20M%20Pur": "Haryana", "Chadi": "Rajasthan", "Barwaha": "Madhya Pradesh", "Bhuj": "Gujarat", "Manesar": "Haryana", "Mohanbari": "Rajasthan", "Shirpur": "Maharashtra", "Lalburra": "Madhya Pradesh", "Cc": "Uttar Pradesh", "Mukhed": "Maharashtra", "Khairlanji": "Madhya Pradesh", "Madhogarh": "Uttar Pradesh", "B%20%20Pali": "Rajasthan", "Obuladevaracheruvu": "Andhra Pradesh", "Kabisuryanagar": "Odisha", "Buldana": "Maharashtra", "Goilkera": "Jharkhand", "Bhim": "Rajasthan", "Barkote": "Odisha", "Manubazar": "Tripura", "Umarkhed": "Maharashtra", "Sibsagar": "Assam", "Chhendipada": "Odisha", "Kodakondla": "Telangana", "Ghansawangi": "Maharashtra", "Paschim%20Madhyampur": "West Bengal", "Vuyyuru": "Andhra Pradesh", "Brahmagiri": "Karnataka", "Mudinepalli": "Andhra Pradesh", "Sinor": "Gujarat", "Chabua": "Assam", "Paddhari": "Gujarat", "Medziphema": "Nagaland", "Ganiyari": "Chhattisgarh", "Sahibganj": "Jharkhand", "Gaya": "Bihar", "Ichawar": "Madhya Pradesh", "Parbatta": "Bihar", "Sekerkote": "Tripura", "Bhinder": "Rajasthan", "Svs": "Tamil Nadu", "Paikmal": "Odisha", "Tikabali": "Odisha", "Ghatshila": "Jharkhand", "Dhankauda": "Odisha", "Amalner": "Maharashtra", "Bhadra": "Rajasthan", "Kutumba": "Bihar", "Sakra": "Bihar", "Amangal": "Telangana", "Omerga": "Maharashtra", "Dobasipara": "Meghalaya", "Portblair": "Andaman and Nicobar Islands", "Sambalpur": "Odisha", "Laljuri": "Tripura", "Sakri": "Maharashtra", "Biaora": "Madhya Pradesh", "Rampur-baghelan": "Madhya Pradesh", "Pataghat": "Kerala", "Namsai": "Arunachal Pradesh", "Barrackpur%20-%20I": "West Bengal", "Sonepur": "Odisha", "Kathikund": "Jharkhand", "Nandgaon": "Maharashtra", "Bantumilli": "Andhra Pradesh", "Ibrahimpatnam": "Telangana", "Cherrabazar": "Meghalaya", "Kasdol": "Chhattisgarh", "Jhajha": "Bihar", "Balianta": "Odisha", "Garbada": "Gujarat", "Vallbhipur": "Gujarat", "Motala": "Gujarat", "Saraiyhat": "Jharkhand", "Sangola": "Maharashtra", "Chandametta": "Madhya Pradesh", "Dhubri": "Assam", "Raghunathapalli": "Telangana", "Patnagarh": "Odisha", "Limbdiq": "Gujarat", "Jharsuguda%20Sadar": "Odisha", "Varni": "Telangana", "Digapahandi": "Odisha", "K%20V%20B%20Puram": "Karnataka", "Bonli": "Rajasthan", "Barisadari": "Rajasthan", "Athagad": "Odisha", "Peda%20%20Araveedu": "Andhra Pradesh", "Hinjli": "Odisha", "Linepada": "Odisha", "Jharbandh": "Odisha", "Veerullapadu": "Andhra Pradesh", "Rajkanika": "Odisha", "Chapar%20Salkocha": "Assam", "Dharmajaigarh": "Chhattisgarh", "Laxmzn%20Garh": "Uttarakhand", "Chandur%20Bazar": "Maharashtra", "Dimapur%20Mdg": "Nagaland", "Tadepalle": "Andhra Pradesh", "Dhakuakhana": "Assam", "Lateri": "Madhya Pradesh", "Aspur": "Rajasthan", "Godda": "Jharkhand", "Doraha": "Punjab", "Pecharthal": "Tripura", "Ghoramari": "Rajasthan", "Valia": "Gujarat", "Bhainsdehi": "Madhya Pradesh", "Pedapalem": "Andhra Pradesh", "Etapalli": "Maharashtra", "Seoni%20Malwa": "Madhya Pradesh", "Kurkheda": "Maharashtra", "Bausi": "Bihar", "Saipau": "Rajasthan", "Ghatanji": "Maharashtra", "Vajrakarur": "Andhra Pradesh", "Shikaripara": "Jharkhand", "Sarwar": "Rajasthan", "Bhatpara": "West Bengal", "Nilgiri": "Tamil Nadu", "Shirur%20Anantpal": "Maharashtra", "Bassi": "Rajasthan", "Ajara": "Maharashtra", "Ss%20Project": "Kerala", "Aibawk": "Mizoram", "Sarwan": "Madhya Pradesh", "Sabarkantha": "Gujarat", "Kochas": "Bihar", "Pandhurna": "Madhya Pradesh", "Chariali": "Assam", "Athpur": "West Bengal", "Basudevpur": "Odisha", "Bhagabannagar": "Maharashtra", "Jakhala": "Haryana", "Bagaicherri": "Tripura", "Bhakatpara": "Assam", "Sindewahi": "Maharashtra", "Ardhapur": "Maharashtra", "Dharmasala": "Odisha", "Pallari": "Chhattisgarh", "Sanawara": "Rajasthan", "Jaysagar": "Assam", "Jajpur%20Road": "Odisha", "Beed": "Maharashtra", "Diphu": "Assam", "Chikiti": "Odisha", "Ranirbazar": "Tripura", "Kundahit": "Jharkhand", "Kachchh": "Gujarat", "Kankalvi": "Maharashtra", "Rahui": "Bihar", "Amer": "Bihar", "Mongkholemba": "Nagaland", "Amet": "Rajasthan", "Revur": "Karnataka", "Bandhu%20Bagicha": "Assam", "Masuda": "Rajasthan", "Barnagar": "Madhya Pradesh", "Ramgarah": "Jharkhand", "Fingapara": "West Bengal", "Karpi": "Bihar", "Kotturu": "Karnataka", "Dhanpur": "Himachal Pradesh", "Tonk": "Rajasthan", "Noamundi": "Jharkhand", "Pathna": "Bihar", "Khambhat": "Gujarat", "Harsud": "Madhya Pradesh", "Begun": "Rajasthan", "Ferrargunj": "Andaman and Nicobar Islands", "Kekri": "Rajasthan", "Borunda": "Rajasthan", "Barkagaon": "Jharkhand", "Rasgovindpur": "Odisha", "Arrah": "Bihar", "Ambikapur": "Chhattisgarh", "Talen": "Madhya Pradesh", "Chikanpara": "West Bengal", "Dunara": "Uttar Pradesh", "Parli": "Maharashtra", "Bagli": "Madhya Pradesh", "Chigurumamidi": "Telangana", "Dhanora": "\u092e\u0939\u093e\u0930\u093e\u0937\u094d\u091f\u094d\u0930", "Itarhi": "Bihar", "Pachora": "Maharashtra", "Pachore": "Madhya Pradesh", "Akodia": "Madhya Pradesh", "Parlu": "Rajasthan", "Kudra": "Bihar", "Agar": "Maharashtra", "Korai": "Odisha", "Chauparan": "Jharkhand", "Sayla": "Gujarat", "Bihariganj": "Bihar", "Tlangnuam%20%28part%29": "Mizoram", "Damavaram": "Andhra Pradesh", "Bochaha": "Bihar", "Surgana": "Maharashtra", "Chozuba": "Nagaland", "Atoizu": "Nagaland", "Poladpur": "Maharashtra", "Lokeswaram": "Telangana", "Barhait": "Jharkhand", "Siwan": "Bihar", "Banagrasm": "West Bengal", "Port%20Blair": "Andaman and Nicobar Islands", "Chandi": "Bihar", "Tileibani": "Odisha", "Kaij": "Maharashtra", "Kopati": "Assam", "Tangi": "Odisha", "Rongjeng": "Meghalaya", "Sidhi": "Madhya Pradesh", "Paranda": "Uttarakhand", "Meghnagar": "Madhya Pradesh", "Gadra%20Road": "Rajasthan", "Danapur": "Bihar", "Kharik": "Bihar", "Majuli": "Assam", "Veldurthy": "Andhra Pradesh", "Ghanpur%28m%29": "Telangana", "Phek": "Nagaland", "Paratwada": "Maharashtra", "Kankrej": "Gujarat", "Veldurthi": "Andhra Pradesh", "Udaipura": "Madhya Pradesh", "Asthawan": "Bihar", "Ladnun": "Rajasthan", "Sindhari": "Rajasthan", "Choppadandi": "Telangana", "Antagarh": "Chhattisgarh", "Mehgoun": "Uttar Pradesh", "Khaira": "Maharashtra", "Gossaigaon": "Assam", "Garautha": "Uttar Pradesh", "Kutra": "Odisha", "Movva": "Andhra Pradesh", "Melaghar": "Tripura", "Jintur": "Maharashtra", "Thingsulthliah%20%28part%29": "Mizoram", "Mundwa": "Rajasthan", "Sarsiwa": "Chhattisgarh", "Jaithari": "Madhya Pradesh", "South%20Salmara": "Assam", "Beniadih": "Jharkhand", "Pottangi": "Odisha", "Kusumanchi": "Telangana", "Sunabeda": "Odisha", "Devipatnam": "Andhra Pradesh", "Duggirala": "Andhra Pradesh", "Triveniganj": "Bihar", "Atpadi": "Maharashtra", "Torpa": "Jharkhand", "Saraipali": "Chhattisgarh", "Nawlgarh": "Rajasthan", "Shalonibari": "Assam", "Balesar": "Rajasthan", "Napaam": "Assam", "Nepanagar": "Madhya Pradesh", "Kalinga": "Haryana", "Vipanakal": "Andhra Pradesh", "Allavaram%20Mandal": "Andhra Pradesh", "Similiguda": "Odisha", "Ambagarh%20Chowki": "Chhattisgarh", "Bero": "Jharkhand", "Shambhuganj": "Uttar Pradesh", "Kiwat": "Maharashtra", "Mangrulpir": "Maharashtra", "Noadih": "Bihar", "Chourai": "Madhya Pradesh", "Vemsur": "Telangana", "Pynursla": "Meghalaya", "Tadpatri": "Andhra Pradesh", "Birendranagar": "Mid-Western Region", "Nabarangpur": "Odisha", "Hnahthial": "Mizoram", "Kumbhraj": "Madhya Pradesh", "Mahagaon": "Maharashtra", "Nilagiri": "Odisha", "Dharmavaram": "Andhra Pradesh", "Anuppur": "Madhya Pradesh", "Kolluru": "Andhra Pradesh", "Angara": "Andhra Pradesh", "Jagatsinghpur": "Odisha", "Laluk": "Assam", "Bokhara": "West Bengal", "Khaniadhana": "Madhya Pradesh", "Jagiroad": "Assam", "Piploda": "Madhya Pradesh", "S%20N%20Puram": "Kerala", "Hrishyamukh": "Tripura", "Kiphire": "Nagaland", "Angalakudur": "Andhra Pradesh", "Raikia": "Odisha", "Thanagazi": "Rajasthan", "Phulumbri": "Maharashtra", "Satana": "Madhya Pradesh", "Kodarma": "Jharkhand", "Piprahi": "Bihar", "Darrang%20Panbari": "Assam", "Manamunda": "Odisha", "Dibrugarh": "Assam", "Nathnagar": "Bihar", "Bongaon%20%28%20Boko%29": "Assam", "Mahroni": "Uttar Pradesh", "Pipariya": "Madhya Pradesh", "Bengtal": "West Bengal", "Kharua": "Assam", "Rengali": "Odisha", "Bhanupratappur": "Chhattisgarh", "Khajipet": "Telangana", "Raxaul": "Bihar", "Bagicha": "Chhattisgarh", "Bhiwapur": "Maharashtra", "Jasarana": "Uttar Pradesh", "Pawai": "Madhya Pradesh", "Udaiprwati": "Rajasthan", "Borjuli": "Assam", "Vrpuram": "Andhra Pradesh", "Pakuria": "Jharkhand", "Burhar": "Madhya Pradesh", "Gogamukh": "Assam", "Manasa": "Madhya Pradesh", "Muniguda": "Odisha", "Salema": "Tripura", "Phenhara": "Bihar", "Kamalghat": "Tripura", "Balayapalli": "Andhra Pradesh", "Penuballi": "Telangana", "Laban": "Rajasthan", "Chhatapur": "Madhya Pradesh", "Itkhori": "Jharkhand", "Damoh": "Madhya Pradesh", "Mantha": "\u092e\u0939\u093e\u0930\u093e\u0937\u094d\u091f\u094d\u0930", "Kishanagnj": "Bihar", "Buxar": "Bihar", "Sanchore": "Rajasthan", "Bholaganj%20Bazar": "Meghalaya", "Dharamgarh": "Odisha", "Muraul": "California", "Birpur": "Bihar", "Dikrong": "Assam", "Doongla": "Rajasthan", "Kholapota": "West Bengal", "Vallabhipur": "Gujarat", "Titilagarh": "Odisha", "Golamunda": "Odisha", "Golakganj": "Assam", "Bhanjanagar": "Odisha", "Rampur%20Naikin": "Madhya Pradesh", "Jeypur": "Odisha", "Jaipatna": "Odisha", "Ghansore": "Madhya Pradesh", "Gandipalem": "Andhra Pradesh", "Shiv": "Rajasthan", "Rahta": "Bihar", "Regonda": "Telangana", "Bidupur": "Bihar", "Daltoganj": "Jharkhand", "Jat": "Maharashtra", "Melchhamunda": "Odisha", "Yellareddipet": "Telangana", "Waraseoni": "Madhya Pradesh", "Pipar%20Road": "Rajasthan", "Gharghoda": "Chhattisgarh", "Rajgarh%28bia%29": "Rajasthan", "Narsinghgarh": "Madhya Pradesh", "I%20Polavaram": "Andhra Pradesh", "Kutiyana": "Gujarat", "Regidi%20Mandal": "Andhra Pradesh", "Jairamnagar": "Chhattisgarh", "Garhakota": "Madhya Pradesh", "Basirhat": "West Bengal", "Sayan": "Gujarat", "K%20Singhpur": "Odisha", "Arwal": "Bihar", "K%20Mahankal": "Himachal Pradesh", "Sedwa": "Chhattisgarh", "Uppununthala": "Telangana", "Singanamala": "Andhra Pradesh", "Nandghat": "Chhattisgarh", "Raneswar": "Jharkhand", "Digras": "Maharashtra", "Saoli": "Maharashtra", "Bheemadevarpalle": "Telangana", "Agartala": "Tripura", "Sakti": "Chhattisgarh", "Tangla": "Maharashtra", "Laukaha": "Bihar", "Laukahi": "Bihar", "Mander": "Uttar Pradesh", "Shahada": "Maharashtra", "Ambabhana": "Odisha", "Shahade": "Maharashtra", "Chandrapur%20Block": "Chittagong Division", "S%20Khawbung": "Mizoram", "Brahma%20Samudram": "Andhra Pradesh", "Ajaygarh": "Madhya Pradesh", "Mawsynram": "Meghalaya", "Chattapur": "Madhya Pradesh", "Devla": "Gujarat", "Lakhanpur": "Jammu and Kashmir", "Mamit": "Mizoram", "Barengapara": "Meghalaya", "Niali": "Odisha", "Keshod": "Gujarat", "Gangavaram": "Andhra Pradesh", "Champua": "Odisha", "Atchampet": "Andhra Pradesh", "Sarath": "Jharkhand", "Billanapalli": "Andhra Pradesh", "Pedaparupudi": "Andhra Pradesh", "Fatehpur%20Shekhawati": "Rajasthan", "Hulasganj": "Bihar", "Kotpad": "Odisha", "Kanipakam": "Andhra Pradesh", "Gomia": "Jharkhand", "Medpalli": "Maharashtra", "Bissamcuttack": "Odisha", "Patna": "Bihar", "Runnisaidpur": "Bihar", "Puri": "Odisha", "Karmala": "Maharashtra", "Manpur": "Chhattisgarh", "Narpala": "Andhra Pradesh", "Shankarpur": "Bihar", "Jorhat": "Assam", "Chhuria": "Bihar", "Bundu": "Jharkhand", "Katihar": "Bihar", "Peddakothapally": "Telangana", "Yedpalle": "Telangana", "Siddanakonduru": "Andhra Pradesh", "Hojai": "Assam", "Rapur": "Andhra Pradesh", "Jajpur": "Odisha", "Chhapiheda": "Madhya Pradesh", "Baitu": "Rajasthan", "Jambughoda": "Gujarat", "Kuru": "Jharkhand", "Benipur": "Bihar", "Muktai%20Nagar": "Maharashtra", "Dhekiajuli": "Assam", "Katangi": "Madhya Pradesh", "T%20Sundupalle": "Andhra Pradesh", "Jainagar": "Bihar", "Namtok": "Arunachal Pradesh", "Bitragunta": "Andhra Pradesh", "Kishanganj": "Bihar", "Guwahati": "Assam", "Nursarai": "Bihar", "Shirur%20K": "Maharashtra", "Thimmapur": "Telangana", "Nizampatnam": "Andhra Pradesh", "Tuli": "Nagaland", "Bhagawanpura": "Rajasthan", "Jolaibari": "Tripura", "Bandra": "Maharashtra", "Tuljapur": "Maharashtra", "Nawgarh": "Rajasthan", "Jabera": "Madhya Pradesh", "Salipur": "Odisha", "Kotabommali": "Andhra Pradesh", "Himayatnagar": "Telangana", "Mawphlang": "Meghalaya", "Narasinghpur": "Odisha", "Satyavedu": "Andhra Pradesh", "Lakhipur": "Assam", "Bamangachi": "West Bengal", "Nandurbar": "Maharashtra", "Belgahana": "Chhattisgarh", "Tankara": "Gujarat", "Paraiya": "Bihar", "Bhua%20Bichhia": "Madhya Pradesh", "Dondi%20Awari": "Chhattisgarh", "Dharampur": "Gujarat", "Mangalwedha": "Maharashtra", "Bhadrak%20Rural": "Odisha", "Ucc": "Meghalaya", "Jaipur%20City": "Rajasthan", "Bodwad": "Maharashtra", "Hemgir": "Odisha", "Simri": "Bihar", "Madgul": "Telangana", "Chatra": "Jharkhand", "Neerada": "Kerala", "Shahpura": "Rajasthan", "Chjandpur": "Uttar Pradesh", "Lakhanadon": "Madhya Pradesh", "Madhepura": "Bihar", "Agomoni": "Assam", "Vallabhnagar": "Rajasthan", "Rani%20Block": "Rajasthan", "Deoghar": "Jharkhand", "Jagatsinghapur": "Odisha", "Rajgir": "Bihar", "Beohari": "Madhya Pradesh", "Bihta": "Bihar", "Amarpatan": "Madhya Pradesh", "Narua": "Odisha", "Resubelpara": "Meghalaya", "Kalapipal": "Madhya Pradesh", "Ramadugu": "Telangana", "Nijhar": "Gujarat", "Begusarai%20H%20O": "Bihar", "Lalpul%20Bazar": "Maharashtra", "Baramchari": "Assam", "Sri%20Madhopur": "Rajasthan", "Tura": "Meghalaya", "Ellanthakunta": "Telangana", "Kovur": "Andhra Pradesh", "Shegaon": "Maharashtra", "Keshkal": "Chhattisgarh", "Nilanga": "Maharashtra", "Parbatpur": "Jharkhand", "Lawan": "Rajasthan", "Champa": "Chhattisgarh", "Rashmi": "Rajasthan", "P%20R%20Gudem": "Telangana", "Parbhani": "Maharashtra", "Armori": "Maharashtra", "Kusmi": "Madhya Pradesh", "Marsaghai": "Odisha", "Nagarnausa": "Bihar", "Paralakhemundi": "Odisha", "Hunterganj": "Jharkhand", "Jeypore%28k%29": "Odisha", "Niwali": "Maharashtra", "Jamugurihat": "Assam", "Kohima%20Sadar": "Nagaland", "Markacho": "Jharkhand", "Sabour": "Bihar", "Satlasana": "Gujarat", "Siha": "Haryana", "Jonai": "Assam", "Pathalgoan": "Chhattisgarh", "Chizami": "Nagaland", "Saitual": "Mizoram", "Kanaganapalli": "Andhra Pradesh", "Rajpipala": "Gujarat", "Kadana": "Gujarat", "Harisinga": "Assam", "Boden": "Odisha", "Jhagroli": "Haryana", "Georai": "Maharashtra", "Malikipuram%20Mandal": "Andhra Pradesh", "Kapadvanj": "Gujarat", "Vijayaraghavgarh": "Madhya Pradesh", "Pathalipam": "Assam", "G%20Mills": "Tamil Nadu", "Bhuragaon": "Assam", "Parigi": "Andhra Pradesh", "Aundha%20Nagnath": "Maharashtra", "Arnod": "Rajasthan", "Tendukheda": "Madhya Pradesh", "Etcherla%20Mandal": "Andhra Pradesh", "Maneswar": "Haryana", "Zotlang": "Mizoram", "Gangadhara": "Telangana", "Mudkhed": "Maharashtra", "Khairagarh": "Chhattisgarh", "Phingeshwar": "Chhattisgarh", "Baihar": "Madhya Pradesh", "Karatampadu": "Andhra Pradesh", "Sohagpur": "Madhya Pradesh", "Ghilamara": "Assam", "Kothur": "Telangana", "Kokrajhar": "Assam", "Jaora": "Madhya Pradesh", "Sarangada": "Odisha", "Khatiguda": "Odisha", "Kherem%20Bisa": "Arunachal Pradesh", "Vijayawada": "Andhra Pradesh", "Gumagarh": "Odisha", "Vankal": "Gujarat", "Sabroom": "Tripura", "Bilha": "Chhattisgarh", "Ranpur": "Gujarat", "Begusarai": "Bihar", "Silwani": "Madhya Pradesh", "Khajuripada": "Odisha", "Deodar": "Jharkhand", "Rajoun": "Bihar", "Barbari": "Assam", "Gajsinghpur": "Rajasthan", "Udakishanganj": "Bihar", "Wardhannapet": "Telangana", "Kinwat": "Maharashtra", "Bijepur": "Karnataka", "Rajakhera": "Rajasthan", "Giridih": "Jharkhand", "Parsauni": "Bihar", "Korpana": "Maharashtra", "Mohania": "Bihar", "Nala": "Jharkhand", "Botad": "Gujarat", "Betnoti": "Odisha", "Mashrakh": "Bihar", "Chotila": "Gujarat", "Rolla": "Andhra Pradesh", "Kotra": "Rajasthan", "Gunnor": "Madhya Pradesh", "Dhenkanal%20Sadar": "Odisha", "Kamptee": "Maharashtra", "Phaileng": "Manipur", "Bhatkuli": "Maharashtra", "Halishahar": "West Bengal", "Araria": "Bihar", "Bethamcherla": "Andhra Pradesh", "Dumraon": "Bihar", "R%20C%20Puram": "Karnataka", "Amadaguru": "Andhra Pradesh", "Belaganj": "Bihar", "B%20Kodur": "Andhra Pradesh", "Lanka": "Assam", "Jodia": "Gujarat", "Bisrampur": "Chhattisgarh", "Doomdooma": "Bihar", "Khalikote": "Odisha", "Kohima": "Nagaland", "Banka": "Bihar", "Kahara": "Odisha", "Nandimandalam": "Andhra Pradesh", "Kandahr": "Maharashtra", "Bhandair": "Nagaland", "Vinukonda": "Andhra Pradesh", "Chohtan": "Rajasthan", "Lunglei": "Mizoram", "Mauganj": "Madhya Pradesh", "Narasimulapet": "Telangana", "Bhaupratappur": "Chhattisgarh", "Cherrapunjee": "Meghalaya", "Buruj": "West Bengal", "Datia": "Madhya Pradesh", "Vedurukuppam": "Andhra Pradesh", "Daroli%20Ahir": "Haryana", "Jama": "Jharkhand", "Bari%20Sadari": "Rajasthan", "Gunga": "Rajasthan", "Sujangahr": "Rajasthan", "Teghra": "Bihar", "Sunpura": "Uttar Pradesh", "Phulparas": "Bihar", "Sadulsahar": "Rajasthan", "Santhipuram": "Tamil Nadu", "Chamata": "Assam", "Seondha": "Madhya Pradesh", "Kargi%20Road": "Uttarakhand", "Uchchhal": "Gujarat", "Hinganghat": "Maharashtra", "Palakurthy": "Telangana", "Chakki": "Punjab", "Narkhed": "Maharashtra", "Bilkisganj": "Madhya Pradesh", "Eturunagaram": "Telangana", "Rehti": "Madhya Pradesh", "Bamori": "Madhya Pradesh", "M%20Rampur": "Uttar Pradesh", "Baktara": "Madhya Pradesh", "Manu": "Tripura", "Chakrayapet": "Andhra Pradesh", "Sandeshkhali": "West Bengal", "Parola": "Maharashtra", "Bajali": "Assam", "Raisen": "Madhya Pradesh", "Kannod": "Madhya Pradesh", "Pratapganj": "Bihar", "Chowhata": "Uttar Pradesh", "Jharsuguda": "Odisha", "Awantipur%20Barodiya": "Madhya Pradesh", "Geesugonda": "Telangana", "Maheshwar": "Madhya Pradesh", "Nr%20Palem": "Telangana", "Jowai": "Meghalaya", "Chaibasa": "Jharkhand", "Ichak": "Jharkhand", "Udala": "Odisha", "Rajanagaram": "Andhra Pradesh", "Konardam": "Jharkhand", "Baldeogarh": "Madhya Pradesh", "Ghantapada": "Odisha", "Ghatagaon": "Odisha", "Sinapalli": "Chhattisgarh", "Baitamari": "Assam", "Hadgaon": "Maharashtra", "Burgamapahad": "Telangana", "Baruakandi": "Tripura", "Mewanagar": "Rajasthan", "Pattamundai": "Odisha", "Machkhowa": "Assam", "Jamner": "Maharashtra", "Sherghati": "Bihar", "Kishan%20Garh%20Bass": "Rajasthan", "Vetapalem": "Andhra Pradesh", "Pandaria": "Chhattisgarh", "Sadiya": "Assam", "Surajpur": "Chhattisgarh", "Bishnupur%20-%20Ii": "West Bengal", "Kheralu": "Gujarat", "Tigiria": "Odisha", "Attair": "Gujarat", "Fatepura": "Gujarat", "Khliehriat": "Meghalaya", "Daringbadi": "Odisha", "Daryapur": "Maharashtra", "Lower%20Chandmari": "Meghalaya", "Chinthakommadinne": "Andhra Pradesh", "Donkarayi": "Odisha", "Paschim%20Hmunpui": "Tripura", "Farooqnagar": "Telangana", "Supaul": "Bihar", "Birasinghpur": "Madhya Pradesh", "Fekamari": "Assam", "Umerkote": "Odisha", "Phiringia": "Odisha", "Pagidyala": "Andhra Pradesh", "Akole": "Maharashtra", "Ghanpur%20%28mulug%29": "Telangana", "Baraily": "Madhya Pradesh", "Kuchinda": "Odisha", "Jirania": "Tripura", "Machalpur": "Madhya Pradesh", "Malkangiri": "Odisha", "Saraiyahat": "Jharkhand", "Longleng": "Nagaland", "Ghanwangi": "Maharashtra", "Deori": "Chhattisgarh", "Champang": "California", "Mahad": "Maharashtra", "Anjad": "Madhya Pradesh", "Darpanigarh": "Odisha", "Chitrakonda": "Odisha", "Gairatganj": "Madhya Pradesh", "Khagaria": "Bihar", "Purushottampur": "Odisha", "Khichan": "Rajasthan", "Kanker": "Chhattisgarh", "Sithanagram": "Andhra Pradesh", "Khacharod": "Madhya Pradesh", "Khurai": "Madhya Pradesh", "Simhadripuram": "Andhra Pradesh", "Halem": "Kerala", "Rampur%20Block": "Bihar", "Ghanpur%20%28station%29": "Telangana", "Chendurthi": "Telangana", "Jamhor": "Bihar", "Pohri": "Madhya Pradesh", "Tekari": "Bihar", "Madhupur": "Jharkhand", "Parli%20Vaij": "Maharashtra", "Bansur": "Rajasthan", "Aska": "Odisha", "Khamnore": "Rajasthan", "Dawath": "Bihar", "Pendlimarri": "Andhra Pradesh", "Sadar%20Madhubani": "Bihar", "Vajrapukotturu%20Mandal": "Andhra Pradesh", "Chitrangi": "Madhya Pradesh", "Lakri%20Nabiganj": "Bihar", "Bayad": "Gujarat", "Chopda": "Maharashtra", "Baramba": "Odisha", "Manjlegaon": "Maharashtra", "Tekkali%20Mandal": "Andhra Pradesh", "Vyara": "Gujarat", "Warora": "Maharashtra", "Jarmundi": "Jharkhand", "Attabira": "Odisha", "Siripuram": "Andhra Pradesh", "Goaldaha": "West Bengal", "Lahoal": "Assam", "Ghograpar": "Assam", "Keonjhar": "Odisha", "Buguda": "Odisha", "Cachar": "Assam", "Nawada": "Bihar", "Machkund": "Odisha", "Sidli%20Chirang": "Assam", "West%20Singhbhum": "Jharkhand", "Ramagiri": "Telangana", "Sindkheda": "Maharashtra", "Pupri": "Bihar", "Umaria": "Madhya Pradesh", "Bathani": "Bihar", "Mangaldoi": "Assam", "Machavaram": "Telangana", "Gariyadhar": "Gujarat", "Toto": "Jharkhand", "Tizit": "Nagaland", "Sindkhed%20Raja": "Maharashtra", "Pabhoi": "Assam", "Kheragarh": "Uttar Pradesh", "Vav": "Gujarat", "Murakambattu": "Andhra Pradesh", "Shirala": "Maharashtra", "Khawbung": "Mizoram", "Thelamara": "Assam", "Beluguppa": "Andhra Pradesh", "Dakkili": "Andhra Pradesh", "Krishnai": "Assam", "S%20Rampur": "Uttar Pradesh", "Sheopur": "Madhya Pradesh", "Deganga": "West Bengal", "Orchha": "Madhya Pradesh", "Surada": "Odisha", "Ch%20Madharam": "Telangana", "Kimin": "Assam", "Kishorenagar": "Odisha", "Gudamalani": "Rajasthan", "Lanjigarh": "Odisha", "Chandbali": "Odisha", "Angul": "Odisha", "Gumparlapadu": "Andhra Pradesh", "Alisinga": "Assam", "Vallur": "Andhra Pradesh", "Ekangersarai": "Bihar", "Umrala": "Gujarat", "Nayagarh": "Odisha", "Lanji": "Madhya Pradesh", "Paliganj": "Bihar", "Pathapatnam%20Mandal": "Andhra Pradesh", "Kalampur": "Odisha", "Dhusuri": "Odisha", "Bukkapatnam": "Andhra Pradesh", "Darpan": "Odisha", "Donkamokam": "Assam", "East%20Champaran": "Bihar", "Anupgarh": "Rajasthan", "Chhotisadari": "Rajasthan", "Mairang": "Meghalaya", "Biswanathghat": "Assam", "Taloda": "Maharashtra", "Gudari": "Odisha", "Girva": "Madhya Pradesh", "Rudri": "Chhattisgarh", "Vontimitta": "Andhra Pradesh", "Thadlasken": "Meghalaya", "Vemuru": "Andhra Pradesh", "Dediapada": "Gujarat", "G%20Udayagiri": "Odisha", "Partur": "Maharashtra", "Salumber": "Rajasthan", "Gandavaram": "Andhra Pradesh", "Laikera": "Odisha", "Shehera": "Gujarat", "Missamari": "Assam", "Kunkuri": "Chhattisgarh", "Chehra%20Kalan": "Bihar", "Kolaras": "Madhya Pradesh", "Behea": "Bihar", "Byrnihat": "Meghalaya", "Junagarh": "Gujarat", "Mawkyrwat": "Meghalaya", "Pfutsero": "Nagaland", "Garobadha": "Meghalaya", "Alamnagar": "Bihar", "Yellanur": "Andhra Pradesh", "Kopargaon": "Maharashtra", "Washim": "Maharashtra", "Lahar": "Madhya Pradesh", "Aul": "Odisha", "Baghmara": "Meghalaya", "Sisai": "Jharkhand", "Jaisalmer": "Rajasthan", "Atreyapuram": "Andhra Pradesh", "Naugachia": "Bihar", "Bhawanipatna": "Odisha", "Tseminyu": "Nagaland", "Akkalkuwa": "Maharashtra", "Kharora": "Chhattisgarh", "Bihupuria": "Assam", "Bolagarh": "Odisha", "P%20Gannavaram": "Andhra Pradesh", "Lakhandur": "Maharashtra", "Dhamotar": "Rajasthan", "Dantewada": "Chhattisgarh", "Kuhi": "Maharashtra", "Banarpal": "Odisha", "Jagra": "Assam", "Kokila": "Uttar Pradesh", "Balasore": "Odisha", "Athmalgola": "Bihar", "Orai": "Uttar Pradesh", "Chandil": "Jharkhand", "Itki": "Jharkhand", "Sahebganj": "Jharkhand", "Garjee": "Tripura", "Mandamarri": "Telangana", "Goregaon": "Maharashtra", "Nekkonda": "Telangana", "Husnabad": "Telangana", "Kamanpur": "Telangana", "Kothagarh": "Odisha", "Matia": "Bihar", "Gummagatta": "Andhra Pradesh", "Dasamantapur": "Odisha", "Khallikote": "Odisha", "Varadaiahpalem": "Andhra Pradesh", "E%20%20Lungdar": "Mizoram", "Munger": "Bihar", "Barwadih": "Jharkhand", "Dabhra": "Chhattisgarh", "Deulgaon%20Raja": "Maharashtra", "Gopalganj": "Bihar", "T%20Palem": "Telangana", "Basta": "Odisha", "Jasrana": "Uttar Pradesh", "Tulluru": "Andhra Pradesh", "Vuyyur": "Andhra Pradesh", "Tharthari": "Bihar", "Hajipur": "Bihar", "Malkharoda": "Chhattisgarh", "Laxmipur": "Tripura", "Udhwa": "Jharkhand", "The%20Dangs": "Gujarat", "Segaon": "Maharashtra", "Batiyagarh": "Madhya Pradesh", "Biraul": "Bihar", "Patepur": "Bihar", "Bahalda": "Odisha", "Ratanpur": "Chhattisgarh", "Lormi": "Chhattisgarh", "Kharupetiaghat": "Assam", "Sindhekela": "Odisha", "Bongaon": "West Bengal", "Kuchinapudi": "Andhra Pradesh", "Mahnar": "Bihar", "Glt": "Delhi", "Sonbarsa": "Bihar", "Jhalod": "Gujarat", "Mopidevi": "Andhra Pradesh", "Udwant%20Nagar": "Bihar", "Sengaon": "Maharashtra", "Teonthar": "Madhya Pradesh", "Bongaigaon": "Assam", "Uravakonda": "Andhra Pradesh", "Kukshi": "Madhya Pradesh", "Pendraroad": "Chhattisgarh", "Teori": "Madhya Pradesh", "Deeg": "Rajasthan", "Kalwan": "Maharashtra", "Sami": "Gujarat", "Bonaigarh": "Odisha", "Jasdan": "Gujarat", "Kirlampudi": "Andhra Pradesh", "Koilwar": "Bihar", "Brajarajnagar": "Odisha", "Gondpipri": "Maharashtra", "Bagasara": "Gujarat", "Kahalgaon": "Bihar", "Kantamal": "Odisha", "Bishala": "Rajasthan", "Kallam": "Maharashtra", "Nabinagar": "Bihar", "Muli": "Gujarat", "Milanpur": "Assam", "Hatigarh": "Assam", "Sydapuram": "Andhra Pradesh", "Bahoriaband": "Madhya Pradesh", "Bhagwanpur%20Hat": "Bihar", "Tamia": "Madhya Pradesh", "Rajborasambar": "Odisha", "Korukonda": "Andhra Pradesh", "Niwari": "Uttar Pradesh", "Nathdwara": "Rajasthan", "Penugolanu": "Andhra Pradesh", "Bandar": "Andhra Pradesh", "G%20K%20Palle": "Telangana", "Tarlupadu": "Andhra Pradesh", "Nalanda": "Bihar", "Chausa": "Bihar", "Doom%20Dooma": "Assam", "Maredumilli": "Andhra Pradesh", "Dharuhera": "Haryana", "Bah": "Uttar Pradesh", "Chawngte": "Mizoram", "Sanjamala": "Andhra Pradesh", "Ranipukur": "Uttarakhand", "Varikuntapadu": "Andhra Pradesh", "Khetri": "Rajasthan", "Katol": "Maharashtra", "Gadhada": "Gujarat", "Dharangaon": "Maharashtra", "Kahra": "Bihar", "Katkamsandi": "Jharkhand", "Dahod": "Gujarat", "Sirmour": "Himachal Pradesh", "Banki": "Odisha", "Kesinga": "Odisha", "Amla": "Madhya Pradesh", "Mul": "Maharashtra", "Vkhani": "Himachal Pradesh", "Gotegaon": "Madhya Pradesh", "Kawakol": "Bihar", "Barapali": "Odisha", "Khawzawl": "Mizoram", "Gurua": "Bihar", "K%20G%20Basss": "Chhattisgarh", "Karlapalem": "Andhra Pradesh", "Gurur": "Chhattisgarh", "Bamunigaon": "Assam", "Jagatdal": "West Bengal", "Dehri%20On%20Sone": "Bihar", "Nalicherra": "Tripura", "Nevasa": "Maharashtra", "Mushahari": "Bihar", "Tsunduru": "Andhra Pradesh", "Chand": "Bihar", "Panna": "Madhya Pradesh", "Samgem": "Telangana", "Govindpur": "Odisha", "Seraikera": "Jharkhand", "Rowta": "Assam", "Benipatti": "Bihar", "Kuarmunda": "Odisha", "Kujang": "Odisha", "Mandavalli": "Andhra Pradesh", "Indergarh": "Uttar Pradesh", "Bhaisma": "Chhattisgarh", "Belpahar": "Odisha", "Bharaf": "Odisha", "Kakatpur": "Odisha", "Konta": "Chhattisgarh", "Malarna%20Dungar": "Rajasthan", "Khowai": "Tripura", "Sootea": "Assam", "Kaler": "Punjab", "Jagdalpur": "Chhattisgarh", "Majauli": "Assam", "Mahadevpur": "Telangana", "Kiriburu": "Jharkhand", "Tingkhong": "Assam", "Bahror": "Rajasthan", "Gujarwas": "Haryana", "Raun": "Madhya Pradesh", "Hazaribagh": "Jharkhand", "Khandala": "Maharashtra", "Ner%20Persopant": "Maharashtra", "Murud": "Maharashtra", "Nagri": "Madhya Pradesh", "Dehri": "Bihar", "Abhayapuri": "Assam", "Bakhtiarpur": "Bihar", "Bhupalapalli": "Telangana", "Pedakurapadu": "Andhra Pradesh", "Lengpui": "Mizoram", "Ambah": "Madhya Pradesh", "Lathi": "Gujarat", "Khalihamari": "Assam", "Kondagaon": "Chhattisgarh", "Kundam": "Madhya Pradesh", "Akkal%20Kuwa": "Maharashtra", "Dharhara": "Bihar", "Rapthadu": "Andhra Pradesh", "Tusra": "Rajasthan", "Nainpur": "Madhya Pradesh", "Kavas": "Gujarat", "Saiha": "Mizoram", "Talcher": "Odisha", "Chennaraopet": "Telangana", "Raver": "Maharashtra", "Peelwa": "Rajasthan", "Gdpeta": "Maharashtra", "Gop": "Odisha", "Rawatbhatta": "Rajasthan", "West%20Bunghmun": "Mizoram", "Goharganj": "Madhya Pradesh", "Tallarevu": "Andhra Pradesh", "Bahoriband": "Madhya Pradesh", "Chandabali": "Odisha", "Khamgaon": "Maharashtra", "Telkoi": "Odisha", "Seoni": "Madhya Pradesh", "Bheden": "Odisha", "Katghora": "Chhattisgarh", "Thingsulthliah": "Mizoram", "Dharmasagar": "Telangana", "Amarawara": "Madhya Pradesh", "Rangapara": "Assam", "Surguja": "Chhattisgarh", "Turrur": "Uttarakhand", "Mathurapur%20-%20I": "West Bengal", "Bishungarh": "Jharkhand", "Bankey%20Bazar": "Bihar", "Talcher%20Sadar": "Odisha", "Madanpur": "West Bengal", "Mandla": "Madhya Pradesh", "Deoli": "Rajasthan", "Balaghat": "Madhya Pradesh", "Nampong": "Arunachal Pradesh", "Ponnekallu": "Andhra Pradesh", "Sabalgarh": "Madhya Pradesh", "Daniyawan": "Bihar", "Raneshwar": "Jharkhand", "Chikhaldara": "Maharashtra", "Ambassa": "Tripura", "Radhanagar": "West Bengal", "Bemetara": "Chhattisgarh", "Ahwa": "Gujarat", "Deogarh": "Odisha", "Sankra": "Chhattisgarh", "Gyaraspur": "Madhya Pradesh", "Akkalkot": "Maharashtra", "Panki": "Jharkhand", "Chimur": "Maharashtra", "Duni": "Rajasthan", "Gunupur": "Odisha", "Roddam": "Andhra Pradesh", "Railmagra": "Rajasthan", "Churhat": "Madhya Pradesh", "Bhadgaon": "Maharashtra", "Tarana": "Madhya Pradesh", "Simen%20Chapori": "Assam", "Harrai": "Madhya Pradesh", "Kamakhyanagar": "Odisha", "Sbraj": "Maharashtra", "Obra": "Uttar Pradesh", "Manugur": "Telangana", "Ratnagiri": "Maharashtra", "Madhubani": "Bihar", "Mahendraganj": "Meghalaya", "Lakhni": "Maharashtra", "Balod": "Chhattisgarh", "Sailana": "Madhya Pradesh", "Jhadol": "Rajasthan", "Duthalur": "Andhra Pradesh", "Bhudargad": "Maharashtra", "Desaiganj": "Maharashtra", "Belsor": "Assam", "Ishupur": "Bihar", "Hingoli": "Maharashtra", "Amberia": "West Bengal", "Bhanpura": "Madhya Pradesh", "Settur": "Tamil Nadu", "Serchhip": "Mizoram", "Boarijore": "Jharkhand", "Chapakhowa": "Assam", "Dibipur": "Uttar Pradesh", "Pipar": "Rajasthan", "Tarbha": "Odisha", "Colliery": "Odisha", "Kurdeg": "Jharkhand", "Murliganj": "Bihar", "Nagarkurnool": "Telangana", "Rawatsar": "Rajasthan", "Kahmgaon": "Maharashtra", "Mhasla": "Maharashtra", "Kolasib": "Mizoram", "Watgan": "Chhattisgarh", "Sono": "Uttar Pradesh", "Setrawa": "Rajasthan", "Khandapara": "Chhattisgarh", "Dabra": "Madhya Pradesh", "Athagarh": "Odisha", "Gumla": "Jharkhand", "Jaffrabad": "Delhi", "Sohella": "Odisha", "Golaghat": "Assam", "Singrauli": "Madhya Pradesh", "Rajapakar": "Bihar", "Nagod": "Madhya Pradesh", "Dang": "Madhya Pradesh", "Sadak-arjuni": "Maharashtra", "Maker": "Bihar", "Lingala": "Andhra Pradesh", "Khoirabari": "Assam", "Jasol": "Rajasthan", "Mahamaya": "Chhattisgarh", "Vijaynagar": "Karnataka", "Bikkavolu": "Andhra Pradesh", "Dhanbil": "Jharkhand", "Sribijaynagar": "Rajasthan", "Chachauda": "Madhya Pradesh", "Karera": "Madhya Pradesh", "Garoth": "Madhya Pradesh", "Kuppam": "Andhra Pradesh", "Islamnagar": "Uttar Pradesh", "Haillymandi": "Haryana", "Chilamathur": "Andhra Pradesh", "Morigaon": "Assam", "Miao": "Arunachal Pradesh", "M%20%20Ganj": "Rajasthan", "Kumbhalgarh": "Rajasthan", "R%20Saidpur": "Uttar Pradesh", "Vashi": "Maharashtra", "Goh": "Bihar", "Gaganbavada": "Maharashtra", "Intur": "Andhra Pradesh", "Nonglyer": "Meghalaya", "Bhograi": "Odisha", "Rayagada": "Odisha", "Dagadarthi": "Andhra Pradesh", "Dhanera": "Gujarat", "Achalpur%20City": "Maharashtra", "Rajim": "Chhattisgarh", "Gerukamukh": "Assam", "Bhavi": "Maharashtra", "Maregaon": "Maharashtra", "Kalamb": "Maharashtra", "Dumka": "Jharkhand", "Jamkalyanpur": "Gujarat", "Yerrupalem": "Telangana", "Harabhanga": "Odisha", "Pithora": "Chhattisgarh", "Jalaun": "Uttar Pradesh", "Partabgarh": "Rajasthan", "Sujathanagar": "Andhra Pradesh", "Narayanapur": "Assam", "Nagar%20Utari": "Jharkhand", "Bargarh": "Odisha", "Raipur%20-%20Karchuliyan": "Madhya Pradesh", "Tisri": "Jharkhand", "Harda": "Madhya Pradesh", "Mazbat": "Assam", "Bhiloda": "Gujarat", "Margherita": "Assam", "City": "State", "Khurda": "Odisha", "Salmara%20South": "Assam", "Penagalur": "Andhra Pradesh", "Pathergama": "Jharkhand", "Ratnifaridpur": "Bihar", "Parner": "Maharashtra", "Rithi": "Madhya Pradesh", "Shamshabad": "Telangana", "Bindukuri": "Assam", "Banswada": "Telangana", "Falta": "West Bengal", "Dalgaon": "Assam", "Dhadgaon": "Maharashtra", "Amarapuram": "Andhra Pradesh", "Tuensang": "Nagaland", "Nabi%20Nagar": "Uttar Pradesh", "Bhabua": "Bihar", "Vairengte": "Mizoram", "Sissiborgaon": "Assam", "Pripainti": "Bihar", "Sirdala": "Bihar", "Lajpore": "Gujarat", "Bishramganj": "Tripura", "Rayadurg": "Andhra Pradesh", "Bankatwa": "Bihar", "Ratu": "Mizoram", "Rayavaram": "Andhra Pradesh", "Rawabhatta": "Chhattisgarh", "Odagaon": "Odisha", "Gonegandla": "Andhra Pradesh", "Pulicherla": "\u0c24\u0c46\u0c32\u0c02\u0c17\u0c3e\u0c23", "Bhinai": "Rajasthan", "Bhatli": "Odisha", "Alirajpur": "Madhya Pradesh", "Pamgarh": "Chhattisgarh", "Anantasagaram": "Andhra Pradesh", "Reamal": "Odisha", "Arvi": "Maharashtra", "Hathin": "Haryana", "Chandwa": "Jharkhand", "Deomornoi": "Assam", "Bhabhar": "Gujarat", "Kodimial": "Telangana", "Bhikangaon": "Madhya Pradesh", "Jairampur": "Arunachal Pradesh", "Rangjuli": "Assam", "Talaja": "Gujarat", "Sonpeth": "Maharashtra", "Ramsar": "Rajasthan", "Neora": "West Bengal", "Changtongya": "Nagaland", "Karauli": "Rajasthan", "Bhandra": "Maharashtra", "Saja": "Chhattisgarh", "Ghoshwari": "Bihar", "Irani": "Tripura", "Sangrampur": "Maharashtra", "Nasirabad": "Rajasthan", "Vijoynagar": "Karnataka", "Diu": "Daman and Diu", "Litipara": "Jharkhand", "Mahda": "Maharashtra", "Silapathar": "Assam", "Talupula": "Andhra Pradesh", "Gopalnagar": "West Bengal", "Binjharpur": "Odisha", "Rayagada%28k%29": "Odisha", "Kareli": "Madhya Pradesh", "Sironj": "Madhya Pradesh", "Tanikella": "Telangana", "Bhatgaon": "Chhattisgarh", "R%20G%20Pur": "Haryana", "Gangakhed": "Maharashtra", "Karepalli": "Telangana", "Bachra": "Jharkhand", "Kotturu%20Mandal": "Andhra Pradesh", "Nalbari": "Assam", "Obulavaripalle": "Andhra Pradesh", "Bilaigarh": "Chhattisgarh", "Baliapal": "Odisha", "Sangamjagarlamudi": "Andhra Pradesh", "Vadnagar": "Gujarat", "Kodinda": "Odisha", "Navapur": "Maharashtra", "Keolari": "Madhya Pradesh", "Palta": "Uttar Pradesh", "Atreyapuram%20Mandal": "Andhra Pradesh", "Birra": "Chhattisgarh", "Taljhari": "Jharkhand", "Chousa": "West Bengal", "Radhanpur": "Gujarat", "Bagodar": "Jharkhand", "Upleta": "Gujarat", "Siswan": "Bihar", "Maddur": "Karnataka", "Dummagudem": "Telangana", "Masturi": "Chhattisgarh", "Dotma": "Chhattisgarh", "Naktideul": "Odisha", "Sigadam%20Mandal": "Andhra Pradesh", "Tilakwada": "Gujarat", "Barpeta": "Assam", "Bodhgaya": "Bihar", "Kolhapur": "Maharashtra", "Bishalgarh": "Tripura", "Roh": "Bihar", "Dhalpur": "Himachal Pradesh", "Mokama": "Bihar", "Chapad": "Gujarat", "Jagganathpur": "Jharkhand", "Dwarikapur": "Tripura", "Ramapuram": "Tamil Nadu", "Talasara": "Odisha", "Bari": "Rajasthan", "Barh": "Bihar", "Dhalbhum%2C%20Jamshedpur": "Jharkhand", "Kollipara": "Andhra Pradesh", "Talasari": "Maharashtra", "R%20Udayagiri": "Odisha", "Khargone": "Madhya Pradesh", "Vidapanakal": "Andhra Pradesh", "Lakhnadon": "Madhya Pradesh", "Dantiwada": "Gujarat", "Pakribarawan": "Bihar", "Amba": "Maharashtra", "Vangara": "Telangana", "Andhratharhi": "Bihar", "Choraut": "Bihar", "Murhu": "Jharkhand", "Udaipur%20%28dharamjaigarh%29": "Rajasthan", "Hinjili": "Odisha", "Dawki": "Meghalaya", "Umerkhed": "Maharashtra", "Halvad": "Gujarat", "Bonakal": "Telangana", "Marripadu": "Andhra Pradesh", "Khairagarh%20Raj": "Chhattisgarh", "Patharia": "Madhya Pradesh", "Pipili": "Odisha", "Gopavaram": "Andhra Pradesh", "Rangat": "Andaman and Nicobar Islands", "Rasol": "Himachal Pradesh", "Bokajan": "Assam", "Asarganj": "Bihar", "Yerpedu": "Andhra Pradesh", "Debitola": "Assam", "Helana": "Maharashtra", "Banar": "Rajasthan", "Cheepurupalle": "Andhra Pradesh", "Aheri": "Maharashtra", "Seraikela": "Jharkhand", "Bhopalpatnam": "Maharashtra", "Akaltara": "Chhattisgarh", "Kathalia": "Tripura", "Agar%20Malwa": "Madhya Pradesh", "Dhemaji": "Assam", "Devanakonda": "Andhra Pradesh", "Gua": "Goa", "Rajupalam": "Andhra Pradesh", "Bamunbari": "Assam", "Mayabander": "Andaman and Nicobar Islands", "Pathalipahar": "Assam", "Zeerapur": "Madhya Pradesh", "Ben": "Uttar Pradesh", "Tirodi": "Madhya Pradesh", "Kamarkuchi": "Assam", "Nandivada": "Andhra Pradesh", "Paharpur": "Bihar", "Khunti": "Jharkhand", "Imamganj": "Bihar", "Haflong": "Assam", "Bakola": "Uttarakhand", "Khunta": "Odisha", "Krosuru": "Andhra Pradesh", "Surajgarha": "Bihar", "Dulhin%20Bazar": "Bihar", "Kesli": "Madhya Pradesh", "Kurud": "Chhattisgarh", "Baghiabahal": "Odisha", "Seloo": "Maharashtra", "Williamnagar": "Meghalaya", "Chhatrapur": "Odisha", "Boenpalli": "Telangana", "Nateran": "Madhya Pradesh", "Degloor": "Maharashtra", "Itarsi": "Madhya Pradesh", "Jhirniya": "Madhya Pradesh", "Danguaposi": "Jharkhand", "Wokha": "Nagaland", "Masalia": "Jharkhand", "Bandhogarh": "Madhya Pradesh", "Kalwakurthy": "Telangana", "Moth": "Uttar Pradesh", "Udaipurwati": "Rajasthan", "Lephripara": "Odisha", "Motu": "Odisha", "Bargaon": "Odisha", "Sarangarh": "Chhattisgarh", "Kawardha": "Chhattisgarh", "Vakadu": "Andhra Pradesh", "Manoharpur": "Jharkhand", "Sarmera": "Bihar", "Satyabadi": "Odisha", "Chinnamandem": "Andhra Pradesh", "Olpad": "Gujarat", "Seethampeta": "Andhra Pradesh", "Rapar": "Gujarat", "Belsand": "Bihar", "Pauni": "Maharashtra", "Boko": "Assam", "Giriak": "Bihar", "Balikuda": "Odisha", "Jagannathpur": "Jharkhand", "Dimapur%20Sadar": "Nagaland", "Srikakulam%20Mandal": "Andhra Pradesh", "Tumudibandha": "Odisha", "Weir": "Rajasthan", "Siwana": "Rajasthan", "Loisingha": "Odisha", "Gogunda": "Rajasthan", "Peterbar": "Jharkhand", "Motihari": "Bihar", "Hatadihi": "Odisha", "Dharampuri": "Madhya Pradesh", "Balisankara": "Odisha", "Dammapeta": "Telangana", "Veeravalli": "Andhra Pradesh", "Deoni": "Maharashtra", "Chhatarpur": "Madhya Pradesh", "Bhangar%20-%20I": "West Bengal", "Gahtagaon": "Odisha", "North%20Thingdawl": "Mizoram", "Vvpalem": "Andhra Pradesh", "N%20P%20%20Kunta": "Andhra Pradesh", "Vaghodia": "Gujarat", "Nongstoin": "Meghalaya", "Sarara": "Bihar", "K%20C%20Works": "Madhya Pradesh", "Kathalapur": "Telangana", "Laxmangarh": "Rajasthan", "Lungsen": "Mizoram", "Mothugudem": "Telangana", "Gudibanda": "Karnataka", "Birni": "Uttar Pradesh", "Karjan": "Gujarat", "R%20N%20Project": "Uttar Pradesh", "Gurh": "Madhya Pradesh", "Jaynagar": "Gujarat", "Parasia": "Madhya Pradesh", "Khategaon": "Madhya Pradesh", "Junnardeo": "Madhya Pradesh", "Durgi": "Andhra Pradesh", "Mahidpur": "Madhya Pradesh", "Mandrail": "Rajasthan", "Balipara": "Assam", "Shindkheda": "Maharashtra", "Ferozepur%20Jhirka": "Haryana", "Pendra": "Chhattisgarh", "Bhadesar": "Rajasthan", "Khowang": "Assam", "Chalisgaon": "Maharashtra", "Khandala%20Bawada": "Maharashtra", "Chillakur": "Andhra Pradesh", "Thuamulrampur": "Odisha", "Reiek": "Mizoram", "Jaijaipur": "Chhattisgarh", "Akunuru": "Andhra Pradesh", "Baleshwar%20Sadar": "Odisha", "Tandwa": "Jharkhand", "Patratu": "Jharkhand", "Tengakhat": "Assam", "Ttb": "West Bengal", "Pathadi": "Chhattisgarh", "Dahisara": "Gujarat", "Nimkathana": "Rajasthan", "Kuravi": "Telangana", "Valod": "Gujarat", "Nandipadu": "Andhra Pradesh", "Samastipur": "Bihar", "Bihpur": "Bihar", "Narayanpur": "Assam", "Palkot": "Jharkhand", "Ausa": "Maharashtra", "Sardarpur": "Madhya Pradesh", "Jagdishpur": "Uttar Pradesh", "Salkhua": "Bihar", "Mokhada": "Maharashtra", "Allavaram": "Andhra Pradesh", "Bhitarwar": "Madhya Pradesh", "Salepur": "Odisha", "Dalu": "Himachal Pradesh", "Mahasamund": "Chhattisgarh", "Bhairamgarh": "Chhattisgarh", "Barhampur": "Odisha", "Akkurthi": "Andhra Pradesh", "Amnour": "Bihar", "Guma": "Gujarat", "Bayana": "Rajasthan", "Arang": "Chhattisgarh", "Mallial": "Telangana", "Bilasipara": "Assam", "Kodinga": "Odisha", "Pirpainti": "Bihar", "Rewari": "Haryana", "Nakrekal": "Telangana", "Jaladanki": "Andhra Pradesh", "Gopal%3Bganj": "Bihar", "Kelaras": "Kerala", "Podalakur": "Andhra Pradesh", "Sankheda": "Gujarat", "Babhulgaon": "Maharashtra", "Mydekur": "Andhra Pradesh", "Kelapur": "Maharashtra", "Sihora": "Madhya Pradesh", "Sonapur%20Block": "Assam", "Kathlal": "Gujarat", "Boro%20Bazar": "Assam", "Pisangan": "Rajasthan", "Chintakani": "Telangana", "Pendra%20Road": "Madhya Pradesh", "Bhairabkunda": "Assam", "Naya%20Harsud": "Madhya Pradesh", "Vidisha": "Madhya Pradesh", "Vaijapur": "Maharashtra", "Kesamudram": "Telangana", "Malkapur": "Maharashtra", "Malsisar": "Rajasthan", "Rg%20Pur": "Uttar Pradesh", "Bhokardan": "Maharashtra", "Kalaigaon": "Assam", "Kadegaon": "Maharashtra", "Farrukh%20Nagar": "Haryana", "Santhabommali%20Mandal": "Andhra Pradesh", "Badnagar": "Madhya Pradesh", "Cherukupalle": "Andhra Pradesh", "Santirbazar": "Tripura", "Pangal": "Telangana", "Kothapeta%20Taluk": "Andhra Pradesh", "Bijni": "Assam", "Chirimiri": "Chhattisgarh", "Nabarangour": "Odisha", "Nawadha": "Bihar", "Dhamnagar": "Odisha", "Balasinor": "Gujarat", "Bajpatti": "Bihar", "Garhwa": "Jharkhand", "Sarsara": "Odisha", "Hut%20Bay": "Andaman and Nicobar Islands", "Fatehpur%20Block": "Haryana", "Udalguri": "Assam", "Seraikella%20Kharsawan": "Jharkhand", "Karempudi": "Andhra Pradesh", "Purna": "Maharashtra", "Shrigoda": "Maharashtra", "Phulbani": "Odisha", "Sidhai": "West Bengal", "Saraiya": "Bihar", "Guraora": "Haryana", "Cherial": "Telangana", "Besseria": "Assam", "Manwath": "Maharashtra", "Bhachau": "Gujarat", "Rafiganj": "Bihar", "Halflong": "Assam", "Pipra%20Bazar": "Uttar Pradesh", "Bellamkonda": "Andhra Pradesh", "Kurtamgarh": "Odisha", "Tikamgarh": "Madhya Pradesh", "Vijapur": "Gujarat", "Shevgaon": "Maharashtra", "Ramgarh": "Jharkhand", "Depalpur": "Madhya Pradesh", "Sonkutch": "Madhya Pradesh", "Petlawad": "Madhya Pradesh", "Boudh": "Odisha", "Budge%20Budge%20-%20Ii": "West Bengal", "Kothapalli": "Telangana", "Khariar": "Odisha", "Seetharamapuram": "Andhra Pradesh", "Srimadhopur": "Rajasthan", "Basmath": "Maharashtra", "Savalyapuram": "Andhra Pradesh", "Somandepalli": "Andhra Pradesh", "Lohardags": "Jharkhand", "Somandepalle": "Andhra Pradesh", "Balapanur": "Andhra Pradesh", "Lohardaga": "Jharkhand", "Kondurgu": "Andhra Pradesh", "Koderma": "Jharkhand", "Beloniya": "Tripura", "Chhotaudepur": "Gujarat", "Sundargarh": "Odisha", "Baripada": "Odisha", "Minapur": "Manipur", "Mendipathar": "Meghalaya", "Lakhpat": "Gujarat", "Nowgong": "Madhya Pradesh", "Artc": "Assam", "Lesliganj": "Jharkhand", "Sasaram": "Bihar", "Chauth%20Ka%20Barwara": "Rajasthan", "Tirtol": "Odisha", "Mangaon": "Maharashtra", "Moman%20Badodiya": "Madhya Pradesh", "Upper%20Shillong": "Meghalaya", "Chandwad": "Maharashtra", "Palwancha": "Telangana", "Yadiki": "Andhra Pradesh", "Kalabari": "West Bengal", "Sarubujjili": "Andhra Pradesh", "Dhaltita": "West Bengal", "Khargapur": "Madhya Pradesh", "Sumer": "Meghalaya", "Shrivardhan": "Maharashtra", "Bamanwas": "Rajasthan", "Naugaon": "Odisha", "Laxaman%20Garh": "Uttarakhand", "Jalgoan": "Maharashtra", "Raghopur": "Bihar", "Thelkapally": "Telangana", "Bali": "West Bengal", "Kalidindi": "Andhra Pradesh", "Purunakatak": "Odisha", "Mathania": "Rajasthan", "Bankimongra": "Chhattisgarh", "Dekargaon": "Assam", "Tharad": "Gujarat", "Birmaharajpur": "Odisha", "Bhadrak": "Odisha", "Laxmangarh%20Alwar": "Rajasthan", "Doomni": "Assam", "Nawagarh": "Chhattisgarh", "Nabarangapur": "Odisha", "Pedanandipadu": "Andhra Pradesh", "Alair": "Telangana", "Nandalur": "Andhra Pradesh", "Chandur": "Maharashtra", "Dhrangadhra": "Gujarat", "Didwana": "Rajasthan", "R%20C%20Project": "Assam", "Borio": "Jharkhand", "Telaprolu": "Andhra Pradesh", "Paralkhemundi": "Odisha", "Lungdar": "Mizoram", "Ketekibari": "Assam", "Harij": "Gujarat", "Bina": "Madhya Pradesh", "Kankipadu": "Andhra Pradesh", "Narwar": "Madhya Pradesh", "Jambusar": "Gujarat", "Ngopa": "Mizoram", "Pusad": "Maharashtra", "Kalasapadu": "Andhra Pradesh", "Narayanpatna": "Odisha", "Rohat": "Rajasthan", "Jaisinghnagar": "Madhya Pradesh", "Jamalpur": "Bihar", "Amrabad": "Telangana", "Jhandaha": "Madhya Pradesh", "Kunavaram": "Andhra Pradesh", "Jangalpur": "West Bengal", "Thondangi": "Andhra Pradesh", "Badamba": "Odisha", "Talbehat": "Uttar Pradesh", "Danta%20Ramgarh": "Rajasthan", "Bhella": "Assam", "Rajibpur": "West Bengal", "Balat": "Bihar", "Dhansura": "Gujarat", "Barachatti": "Bihar", "Lakhinagar": "Uttar Pradesh", "Shri%20Amirgadh": "Gujarat", "Chakur": "Maharashtra", "Gunderdehi": "Chhattisgarh", "Naswadi": "Gujarat", "Paravada": "Andhra Pradesh", "Simaria": "Madhya Pradesh", "Kakulapadu": "Andhra Pradesh", "Bhurkunda": "Jharkhand", "Pindwara": "Rajasthan", "Morvi": "Gujarat", "Kurhani": "Bihar", "Piro": "Bihar", "Tuggali": "Andhra Pradesh", "Rairangpur": "Odisha", "Hilsa": "Bihar", "S%20Solapur": "Maharashtra", "Mawlai": "Meghalaya", "Chakapad": "Odisha", "Piru": "Uttar Pradesh", "Pegadapalli": "Telangana", "Bhattiprolu": "Andhra Pradesh", "Magrahat%20-%20Ii": "West Bengal", "Garakupi": "West Bengal", "A%20Konduru": "Andhra Pradesh", "Nasrullaganj": "Madhya Pradesh", "Bhesan": "Gujarat", "Bichhua": "Madhya Pradesh", "Barode": "Gujarat", "Balangir": "Odisha", "Badgaon": "Maharashtra", "Sudhagad": "Maharashtra", "Kumarkhand": "Bihar", "Janakpur": "Chhattisgarh", "Noklak": "Nagaland", "Tirora": "Maharashtra", "K%20Dharur": "Maharashtra", "Rudrampur": "Telangana", "Narnaul": "Haryana", "Bakrahat": "West Bengal", "Jujumura": "Odisha", "Mehidpur": "Madhya Pradesh", "Shambhupura": "Rajasthan", "Dornakal": "Telangana", "Th%20Rampur": "Odisha", "Khaknar": "Chhattisgarh", "Ahmedpur": "Maharashtra", "Mon": "Nagaland", "Musunuru": "Andhra Pradesh", "Gadarwara": "Madhya Pradesh", "Chiechama": "Nagaland", "Jashpurnagar": "Chhattisgarh", "Alsisar": "Rajasthan", "Sanwer": "Madhya Pradesh", "Amadagur": "Andhra Pradesh", "Gohpur": "Assam", "Shajapur": "Madhya Pradesh", "Namrup": "Assam", "Phirangipuram": "Andhra Pradesh", "Jaitaran": "Rajasthan", "Garladinne": "Andhra Pradesh", "Jehanabad": "Bihar", "Aurai": "Uttar Pradesh", "Chanasma": "Gujarat", "Gurundia": "Odisha", "Dhulipudi": "\u0c06\u0c02\u0c27\u0c4d\u0c30 \u0c2a\u0c4d\u0c30\u0c26\u0c47\u0c36\u0c4d", "Dhjar": "Madhya Pradesh", "Bengabad": "Jharkhand", "Lohara": "Maharashtra", "Hirakud": "Odisha", "Impur": "Nagaland", "Santhal%20Parganas": "Jharkhand", "Dabhoi": "Gujarat", "Mahudha": "Gujarat", "Rohtas": "Bihar", "Tihidi": "Odisha", "Ismailpur": "Uttar Pradesh", "Maheshpur": "Jharkhand", "Sailu": "Maharashtra", "Lokra": "West Bengal", "Kendrapara": "Odisha", "Gamharia": "Bihar", "Ner%20Parsopant": "Maharashtra", "Hindol": "Odisha", "Etcherla": "Andhra Pradesh", "Gaurihar": "Madhya Pradesh", "Gouthampur": "Madhya Pradesh", "Kohima%20Village": "Nagaland", "Tangarpali": "Odisha", "Rynjah": "Meghalaya", "Chityal": "Telangana", "Dornipadu": "Andhra Pradesh", "Dumra": "Bihar", "Kohima%20Science%20College": "Nagaland", "Kapileswarapuram": "Andhra Pradesh", "Jawar": "Uttar Pradesh", "Barun": "Bihar", "Dumri": "Jharkhand", "Ghoghamba": "Gujarat", "Putlur": "Andhra Pradesh", "Nadoti": "Rajasthan", "Araimile": "Meghalaya", "Morena": "Madhya Pradesh", "Sikaripara": "Jharkhand", "Tezu": "Arunachal Pradesh", "Hamren": "Assam", "Cheruvu": "Andhra Pradesh", "Shayampet": "Telangana", "Paburia": "Odisha", "Barhat": "Bihar", "Lonar": "Maharashtra", "Chandvad": "Maharashtra", "Kankavli": "Maharashtra", "Dimapur%20Bazar": "Nagaland", "Chanderi": "Madhya Pradesh", "Garla": "Telangana", "Dakra": "Uttarakhand", "Kotma": "Madhya Pradesh", "Balliguda": "Odisha", "Baresei": "Uttar Pradesh", "Barbil": "Odisha", "Lahunipara": "Odisha", "Banekuchi": "Assam", "Hanuman%20Bhagda": "Gujarat", "Dhanwar": "Jharkhand", "Seraikella": "Jharkhand", "Jarada": "Odisha", "Dholka": "Gujarat", "Pansemal": "Madhya Pradesh", "Mokalsar": "Rajasthan", "Emani": "Andhra Pradesh", "Sheohar": "Bihar", "Dumaria": "Bihar", "Salekasa": "Maharashtra", "Manjhi": "Bihar", "Nongpoh": "Meghalaya", "Kosli%20R%20S": "Haryana", "Bhapur": "Odisha", "Nagaram": "Andhra Pradesh", "Ichapur": "West Bengal", "Banaharapali": "Odisha", "Kawant": "Gujarat", "Bhandari": "Nagaland", "Lodhika": "Gujarat", "Pachpadra%20City": "Rajasthan", "Jamai": "Madhya Pradesh", "Devsar": "Gujarat", "Pannur": "Tamil Nadu", "Samalkot": "Andhra Pradesh", "Esagarh": "Madhya Pradesh", "Pichhore": "Madhya Pradesh", "Bhawanathpur": "Jharkhand", "Dheknamari": "West Bengal", "Unchehara": "Madhya Pradesh", "Kantabanji": "Odisha", "Lohawat": "Rajasthan", "Koraput": "Odisha", "P%20Dayal": "Punjab", "Diglipur": "Andaman and Nicobar Islands", "Sandheli": "Assam", "Mangapet": "Telangana", "Nadbai": "Rajasthan", "Matar": "Gujarat", "Burla": "Odisha", "Shujalpur": "Madhya Pradesh", "Kambadur": "Andhra Pradesh", "Bukkrayasamudram": "Andhra Pradesh", "Vijayraghavgarh": "Madhya Pradesh", "Behali": "Assam", "Rajpur": "Madhya Pradesh", "Zawlnuam": "Mizoram", "Soro": "Odisha", "Nariyara": "Chhattisgarh", "Jhadrajing": "Odisha", "Daltonganj": "Jharkhand", "Gadhinglaj": "Maharashtra", "Kodinar": "Gujarat", "Mohana": "Odisha", "Palair": "Telangana", "Jatanbari": "West Bengal", "Darwha": "Maharashtra", "A%20I%20%20Area": "Maharashtra", "Meral": "Jharkhand", "Nagbhid": "Maharashtra", "Latehar": "Jharkhand", "Goroul": "Bihar", "Gothra": "Rajasthan", "Barangabari": "Assam", "Bangarupalem": "Andhra Pradesh", "Nagbhir": "Maharashtra", "Sillod": "Maharashtra", "Bhopalgarh": "Rajasthan", "Tauru": "Haryana", "Morva%20Hadaf": "Gujarat", "Runija": "Madhya Pradesh", "Pathariya": "Madhya Pradesh", "Sorojini": "Assam", "Tezpur": "Assam", "Abhanga": "Tripura", "Ambejogai": "Maharashtra", "Similia": "Odisha", "Meghalaya": "Meghalaya", "Nasriganj": "Bihar", "Kalpi": "Uttar Pradesh", "Amas": "Bihar", "Raiparthy": "Telangana", "Azadnagar": "Karnataka", "Megahatuburu": "Jharkhand", "Kakranan": "Rajasthan", "Tarapur": "Maharashtra", "Kurwai": "Madhya Pradesh", "Mechuka": "Uttar Pradesh", "Dakhin%20Sarubanswar%20%28%20Rampur%29": "Uttar Pradesh", "Araraia": "Bihar", "Chandragiri": "Andhra Pradesh", "Barhi": "Jharkhand", "Madnoor": "Telangana", "Lemalle": "Andhra Pradesh", "Ghantasala": "Andhra Pradesh", "Bhoom": "Maharashtra", "Budni": "Madhya Pradesh", "Nagar": "Rajasthan", "Parchur": "Andhra Pradesh", "Sakhigopal": "Odisha", "Guhagar": "Maharashtra", "Likabali": "Assam", "Prantij": "Gujarat", "Mandu": "Jharkhand", "Nallacheruvu": "Andhra Pradesh", "Chandgad": "Maharashtra", "Kesath": "Bihar", "Lawngtlai": "Mizoram", "Sakoli": "Maharashtra", "North%20Lakhimpur": "Assam", "Tripuranthakam": "Andhra Pradesh", "Simdega": "Jharkhand", "Barghat": "Madhya Pradesh", "Veldanda": "Telangana", "Panyam": "Andhra Pradesh", "Dodamarg": "Maharashtra", "Sihor": "Madhya Pradesh", "Porsa": "Madhya Pradesh", "Sahdei%20Buzurg": "Bihar", "Gogha": "Gujarat", "Vidavalur": "Andhra Pradesh", "Pandhana": "Madhya Pradesh", "Thondamanadu": "Andhra Pradesh", "Thethaitangar": "Jharkhand", "Padma": "Jharkhand", "Choudwar": "Odisha", "Churchu": "Jharkhand", "Birigumma": "Odisha", "Nindra": "Andhra Pradesh", "Dharmanagar": "Tripura", "Sambepalle": "Andhra Pradesh", "Sonbersa": "Bihar", "Orang": "Assam", "Naharkatia": "Assam", "Jalumuru%20Mandal": "Andhra Pradesh", "Diu%20U%20T": "Daman and Diu", "Talod": "Madhya Pradesh", "Chariduar": "Assam", "Koheda": "Telangana", "Longkhim": "Nagaland", "Khonsa": "Arunachal Pradesh", "Dausa": "Rajasthan", "Bastar": "Chhattisgarh", "Mauranipur": "Uttar Pradesh", "Nuapada": "Odisha", "Pratappur": "Chhattisgarh", "Alote": "Madhya Pradesh", "Mihona": "Madhya Pradesh", "Mijikajan": "Assam", "Chakalakonda": "Andhra Pradesh", "Tikrikilla": "Meghalaya", "Atri": "Odisha", "Barharwa": "Jharkhand", "Palsana": "Gujarat", "Bala": "Uttar Pradesh", "Jaipatn%20A": "Odisha", "Sahpura%20Niwas": "Madhya Pradesh", "Kishanpur": "Uttarakhand", "Vajrapukothuru": "Andhra Pradesh", "Tlangnuam": "Mizoram", "Silli": "Jharkhand", "Ichhawar": "Madhya Pradesh", "Kankroli": "Rajasthan", "Lakkireddipalle": "Andhra Pradesh", "Vaishali": "Bihar", "Gurramkonda": "Andhra Pradesh", "Bhogpur": "Punjab", "Deo": "Bihar", "Kankraj": "Madhya Pradesh", "Himatnagar": "Gujarat", "Limbdi": "Gujarat", "Konch": "Uttar Pradesh", "Joura": "Madhya Pradesh", "Mungaoli": "Madhya Pradesh", "Hanumana": "Madhya Pradesh", "Anandapur": "Odisha", "Bijawar": "Madhya Pradesh", "Biloli": "Maharashtra", "Bilara": "Rajasthan", "Mandawar": "Rajasthan", "Mallapur": "Telangana", "Arunachal%20Pradesh": "Arunachal Pradesh", "Dimakuchi": "Assam", "Jammalamadugu": "Andhra Pradesh", "Riga": "Bihar", "Gampalagudem": "Andhra Pradesh", "Kahalgoan": "Bihar", "Dhenkanal": "Odisha", "Laxman%20Garh": "Uttar Pradesh", "Sihawal": "Madhya Pradesh", "Mawpat": "Meghalaya", "Bihaguri": "Assam", "Bkt": "Haryana", "Palasamudram": "Andhra Pradesh", "Darlawn": "Mizoram", "Ranigaon": "Rajasthan", "Amarpur": "Bihar", "Shriwardhan": "Maharashtra", "Lalbarra": "Madhya Pradesh", "Saharsa": "Bihar", "Karanja": "Maharashtra", "Jogipet": "Telangana", "Songadh": "Gujarat", "Parihar": "Bihar", "Kotda": "Rajasthan", "Dhoraji": "Gujarat", "Bijaypur": "Madhya Pradesh", "Ekma": "Bihar", "Gamaharia": "Bihar", "Ladrymbai": "Meghalaya", "Paikamal": "Odisha", "Duliajan": "Assam", "Nauhatta": "Bihar" , "Gopannapalem": "Andhra Pradesh", "Sringeri": "Karnataka", "Kalgahtgi": "Karnataka", "Kollegal": "Karnataka", "Bantwal": "Karnataka", "Ganapavaramandalam": "Andhra Pradesh", "Pandavapura": "Karnataka", "Palakoderu%20Mandalam": "Andhra Pradesh", "Bagepalli": "Karnataka", "Bonangi": "Andhra Pradesh", "Gajapathinagaram": "Andhra Pradesh", "Badangi": "Andhra Pradesh", "Alamanda": "Andhra Pradesh", "Narasimharajapura": "Karnataka", "Honnali": "Karnataka", "Chickballapur": "Karnataka", "Tanuku%20%28mdl%29": "Andhra Pradesh", "Palakoderu%20%28mdl%29": "Andhra Pradesh", "Jeelugumilli": "Andhra Pradesh", "Y%20%20Ramavaram": "Andhra Pradesh", "Komarada": "Andhra Pradesh", "Kanakapura": "Karnataka", "Garugubilli": "Andhra Pradesh", "Ramanagara": "Karnataka", "Hirekerur": "Karnataka", "Mulbagal": "Karnataka", "Jiyyammavalasa": "Andhra Pradesh", "Sira": "Karnataka", "Thirthahalli": "Karnataka", "Malur": "Karnataka", "Jami": "Andhra Pradesh", "Bhadravathi": "Karnataka", "Lakkavaram": "Andhra Pradesh", "Pavagada": "Karnataka", "Nallajerla%20Mandal": "Andhra Pradesh", "Chik%20Ballapur": "Karnataka", "Channapatna": "Karnataka", "Kovvuru%20Mandalam": "Andhra Pradesh", "Sidlaghatta": "Karnataka", "Seethanagaram": "Andhra Pradesh", "Bondapalli": "Andhra Pradesh", "Challakere": "Karnataka", "Hangal": "Karnataka", "Belur": "Karnataka", "Nellimarla": "Andhra Pradesh", "Dodballapura": "Karnataka", "Srinivasapura": "Karnataka", "Ramabhadrapuram": "Andhra Pradesh", "Gurla": "Andhra Pradesh", "Vepada": "Andhra Pradesh", "Arsiekre": "Karnataka", "K%20R%20Nagar": "Karnataka", "Kajuluru": "Andhra Pradesh", "Nidadavole%20Mandalam": "Andhra Pradesh", "Hunsur": "Karnataka", "Buttayagudem": "\u0c06\u0c02\u0c27\u0c4d\u0c30 \u0c2a\u0c4d\u0c30\u0c26\u0c47\u0c36\u0c4d", "Nargund": "Karnataka", "Vijaayrai": "Andhra Pradesh", "Tadikalapudi": "Andhra Pradesh", "Periyapatna": "Karnataka", "Channagiri": "Karnataka", "Mudigere": "Karnataka", "Shiggoan": "Karnataka", "Koppa": "Karnataka", "Ron": "Karnataka", "Navalgund": "Karnataka", "Kadur": "Karnataka", "Davangere": "Karnataka", "Belthagady": "Karnataka", "Malavalli": "Karnataka", "Magadi": "Karnataka", "Shiggaon": "Karnataka", "Dodbalapura": "Karnataka", "Kaikaram": "Andhra Pradesh", "Polavaram%20Mandal": "Andhra Pradesh", "Chebrole": "Andhra Pradesh", "Sendurai": "Tamil Nadu", "Gopalapuram%20Mandalam": "Telangana", "Channarayapatna": "Karnataka", "Harihara": "Karnataka", "Gantyada": "Andhra Pradesh", "Shiratti": "Karnataka", "T%20Narasapuram": "Andhra Pradesh", "Mavelikara": "Kerala", "Arsikere": "Karnataka", "Nallajarla%20Mandalam": "Andhra Pradesh", "Harihra": "Karnataka", "Srinivaspur": "Karnataka", "Skaleshpur": "Karnataka", "Gauribidanur": "Karnataka", "Sorab": "Karnataka", "Hiriyur": "Karnataka", "Hasadurga": "Karnataka", "Hoadurga": "Karnataka", "C%20N%20Hally": "Karnataka", "Turuvekere": "Karnataka", "Doddaballapura": "Karnataka", "Balijipeta": "Andhra Pradesh", "C%20N%20Halli": "Karnataka", "Nagamangala": "Karnataka", "Hosadurga": "Karnataka", "Parvatipuram": "Andhra Pradesh", "S%20Kota": "Rajasthan", "Bgnorth": "West Bengal", "Chipurupalle": "Andhra Pradesh", "Chamarajanagara": "Karnataka", "Therlam": "Andhra Pradesh", "Yelandur": "Karnataka", "Navunda": "Karnataka", "Denkada": "Andhra Pradesh", "Gundugolanu": "Andhra Pradesh", "City": "State", "Harapanahalli": "Karnataka", "Kovvali": "Andhra Pradesh", "Sulya": "Karnataka", "Shirahatti": "Karnataka", "Kundapura": "Karnataka", "Beltangadi": "Karnataka", "Gundlupet": "Karnataka", "Ainavilli%20Mandal": "Andhra Pradesh", "H%20D%20Kote": "Karnataka", "Alur": "Karnataka", "Somvarpet": "Karnataka", "Undrajavaram%20Mandalam": "Andhra Pradesh", "Hosanagara": "Karnataka", "Mundargi": "Karnataka", "Holenarsipur": "Karnataka", "Pusapatirega": "Andhra Pradesh", "Shirhatti": "Karnataka", "Merakamudidam": "Andhra Pradesh", "Pedapadu": "Andhra Pradesh", "Kuttanad": "Kerala", "Hosanagar": "Karnataka", "Holalkere": "Karnataka", "Tadepalligudem%20Mandalam": "Andhra Pradesh", "Sakleshpur": "Karnataka", "Bg%20South": "West Bengal", "Pachipenta": "Andhra Pradesh", "Pragadavaram": "Andhra Pradesh", "Karkal": "Karnataka", "Pulla": "Andhra Pradesh", "Madikeri": "Karnataka", "Kannapuram": "Andhra Pradesh", "Denduluru": "Andhra Pradesh" ,"Jammu":"Jammu and Kashmir" , "Panaji":"Goa" ,"Goa":"Goa"}
class MultipartResource(object):
	def deserialize(self, request, data, format=None):
		if not format:
			format = request.META.get('CONTENT_TYPE', 'application/json')

		if format == 'application/x-www-form-urlencoded':
			return request.POST

		if format.startswith('multipart'):
			data = request.POST.copy()
			data.update(request.FILES)

			return data

		return super(MultipartResource, self).deserialize(request, data, format)


class BaseCorsResource(Resource):
	"""
	Class implementing CORS
	"""
	def error_response(self, *args, **kwargs):
		response = super(BaseCorsResource, self).error_response(*args, **kwargs)
		return self.add_cors_headers(response, expose_headers=True)
		
	def add_cors_headers(self, response, expose_headers=False):
		response['Access-Control-Allow-Origin'] = '*'
		response['Access-Control-Allow-Headers'] = 'content-type, authorization, x-requested-with, x-csrftoken'
		if expose_headers:
			response['Access-Control-Expose-Headers'] = 'Location'
		return response    
	
	def create_response(self, *args, **kwargs):
		"""
		Create the response for a resource. Note this will only
		be called on a GET, POST, PUT request if 
		always_return_data is True
		"""
		response = super(BaseCorsResource, self).create_response(*args, **kwargs)
		return self.add_cors_headers(response)

	def post_list(self, request, **kwargs):
		"""
		In case of POST make sure we return the Access-Control-Allow Origin
		regardless of returning data
		"""
		#logger.debug("post list %s\n%s" % (request, kwargs));
		response = super(BaseCorsResource, self).post_list(request, **kwargs)
		return self.add_cors_headers(response, True)
	
	def post_detail(self, request, **kwargs):
		"""
		In case of POST make sure we return the Access-Control-Allow Origin
		regardless of returning data
		"""
		#logger.debug("post detail %s\n%s" (request, **kwargs));
		response = super(BaseCorsResource, self).post_list(request, **kwargs)
		return self.add_cors_headers(response, True)
	
	def put_list(self, request, **kwargs):
		"""
		In case of PUT make sure we return the Access-Control-Allow Origin
		regardless of returning data
		"""
		response = super(BaseCorsResource, self).put_list(request, **kwargs)
		return self.add_cors_headers(response, True)    
	
	def put_detail(self, request, **kwargs):
		response = super(BaseCorsResource, self).put_detail(request, **kwargs)
		return self.add_cors_headers(response, True)
		
	def method_check(self, request, allowed=None):
		"""
		Check for an OPTIONS request. If so return the Allow- headers
		"""
		if allowed is None:
			allowed = []
			
		request_method = request.method.lower()
		allows = ','.join(map(lambda s: s.upper(), allowed))

		if request_method == 'options':
			response = HttpResponse(allows)
			response['Access-Control-Allow-Origin'] = '*'
			response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-CSRFToken, X-HTTP-Method-Override'
			response['Access-Control-Allow-Methods'] = "GET, PUT, POST, PATCH"
			response['Allow'] = allows
			raise ImmediateHttpResponse(response=response)

		if not request_method in allowed:
			response = http.HttpMethodNotAllowed(allows)
			response['Allow'] = allows
			raise ImmediateHttpResponse(response=response)

		return request_method
	
	def wrap_view(self, view):
		@csrf_exempt
		def wrapper(request, *args, **kwargs):
			request.format = kwargs.pop('format', None)
			wrapped_view = super(BaseCorsResource, self).wrap_view(view)
			return wrapped_view(request, *args, **kwargs)
		return wrapper

#Base Extended Abstract Model
class CORSModelResource(BaseCorsResource, ModelResource):
	pass

class CORSResource(BaseCorsResource, Resource):
	pass


class UserResource2(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
		authorization= Authorization()
		always_return_data = True
	def hydrate(self, bundle):
		print bundle.request
		try:
			override_method=bundle.request.META['HTTP_X_HTTP_METHOD_OVERRIDE']
			print "changed to PATCH"
		except:
			override_method='none'
			print "hello"

		if bundle.request.META['REQUEST_METHOD'] == 'POST' and override_method!='PATCH':
			print "went in"
			try:
				if (bundle.data['web']=="Y"):
					pass
					

			except: 
				try:
					user=User.objects.get(pk=bundle.data['phone'])
					print "fuck"
					#undle.data['phone']=0
					bundle.data["msg"]='olduser'
					bundle.data['otp'] = randint(1000, 9999)
					msg0="http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to="
					msga=str(bundle.data['phone'])
					msg1="&msg=Welcome+to+Sendd.+Your+OTP+is+"
					msg2=str(bundle.data['otp'])
					msg3=".This+message+is+for+automated+verification+purpose.+No+action+required.&msg_type=TEXT&userid=2000142364&auth_scheme=plain&password=h0s6jgB4N&v=1.1&format=text"
					#url1="http://49.50.69.90//api/smsapi.aspx?username=doormint&password=naman123&to="+ str(bundle.data['phone']) +"&from=DORMNT&message="
					query=''.join([msg0,msga,msg1,msg2,msg3])
					print query
					x=urllib2.urlopen(query).read()
					print x
					print "hjhjhjhj"

					try:
						gcmdevice=GCMDevice.objects.filter(device_id=bundle.data['deviceid'])
						if (gcmdevice.count()==0) :
							gcmdevice = GCMDevice.objects.create(registration_id=bundle.data['gcmid'],device_id=bundle.data['deviceid'])
						else:
							print "GCM device already exist"
							
					except:
						print "GCM device not created"
					
				except:
					print "shit"
					bundle.data["msg"]='newuser'	
					bundle.data['otp'] = randint(1000, 9999)
					msg0="http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to="
					msga=str(bundle.data['phone'])
					msg1="&msg=Welcome+to+Sendd.+Your+OTP+is+"
					msg2=str(bundle.data['otp'])
					msg3=".This+message+is+for+automated+verification+purpose.+No+action+required.&msg_type=TEXT&userid=2000142364&auth_scheme=plain&password=h0s6jgB4N&v=1.1&format=text"
					#url1="http://49.50.69.90//api/smsapi.aspx?username=doormint&password=naman123&to="+ str(bundle.data['phone']) +"&from=DORMNT&message="
					query=''.join([msg0,msga,msg1,msg2,msg3])
					print query
					urllib2.urlopen(query).read()
					#mail="Dear "+str(bundle.data['name'])+",\n\nWe are excited to have you join us and start shipping in a hassle free and convenient manner.\n\nOur team is always there to ensure that you have the best possible experience with us. Some of the questions that are frequently asked can be seen on the website as well as the app.\n\nIf you have any other query, you can get in touch with us at +91-8080028081 or mail us at help@sendd.co\n\n\nRegards,\nTeam Sendd"
					#subject=str(bundle.data["name"])+", Thanks for signing up with sendd."
					#send_mail(subject, mail, "Team Sendd <hello@sendd.co>", [str(bundle.data["email"])])


					try:
						gcmdevice=GCMDevice.objects.filter(device_id=bundle.data['deviceid'])
						if (gcmdevice.count()==0) :
							gcmdevice = GCMDevice.objects.create(registration_id=bundle.data['gcmid'],device_id=bundle.data['deviceid'])
						else:
							print "GCM device already exist"
							
					except:
						print "GCM device not created"



			return bundle
		if bundle.request.META['REQUEST_METHOD'] == 'PUT':
			print "dfjfsdkjfdskj"
			queryset= User.objects.get(phone=bundle.data['phone'])
			print bundle.data['otp1']
			print queryset.otp

			if (str(bundle.data['otp1'])==str(queryset.otp)):
			 #generate apikey if otp recieved = otp sent
				bundle.data['apikey']=hashlib.sha224( str(random.getrandbits(256)) ).hexdigest();
				print bundle.data['apikey']
				bundle.data['valid']=1
			else:
				#bundle.data['otp'].del()
				print "nahi hua"
				bundle.data['valid']=0
			return bundle

		if bundle.request.META['REQUEST_METHOD'] == 'POST' and override_method=='PATCH':
			print "patch"
			try:
				gcmdevice=GCMDevice.objects.filter(device_id=bundle.data['deviceid'])
				if (gcmdevice.count()==0) :
					gcmdevice = GCMDevice.objects.create(registration_id=bundle.data['gcmid'],device_id=bundle.data['deviceid'])
				else:
					print "GCM device already exist"
					
			except:
				print "GCM device not created"


			return bundle


class AddressResource2(MultipartResource,ModelResource):
	class Meta:
		queryset = Address.objects.all()
		resource_name = 'address'
		authorization= Authorization()
		always_return_data = True


class NamemailResource2(MultipartResource,ModelResource):
	user = fields.ForeignKey(UserResource2, 'user')
	class Meta:
		queryset = Namemail.objects.all()
		resource_name = 'namemail'
		authorization= Authorization()
		always_return_data = True


class WeborderResource2(CORSModelResource):
	class Meta:
		queryset = Weborder.objects.all()
		resource_name = 'weborder'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self, bundle):
		
		r.publish("b2c", "message")
		
		#creating user if doesnt exist
		try:
			newuser=User.objects.get(pk=bundle.data['sender_number'])
		except:
			newuser= User.objects.create(phone=bundle.data['sender_number'])
			#newuser.save()
			pk=newuser.pk

			print "try"

			
		
		#create nameemail
		try:
			newnamemail=Namemail.objects.filter(user=newuser,name=bundle.data['sender_name'],email=bundle.data['sender_email'])
			print newnamemail.count()

			if (newnamemail.count()==0) :
				print "hi"
				newnamemail = Namemail.objects.create(user=newuser,name=bundle.data['sender_name'],email=bundle.data['sender_email'])
				newnamemail.save()
				pk=newnamemail.pk
			#bundle.obj = Address(address="nick", locality = "", password,timezone.now(),"od_test")
			else:
				print "here"
				for x in newnamemail:
					print "there"
					print x.__dict__
					pk= x.pk
					print "pk"
					print pk
					newnamemail=x
					break

		except:	
			print "cool shit"
		

		#create order
		try:
			neworder=Order.objects.create(namemail=newnamemail,user=newuser,address=bundle.data['pickup_location'],way='W',pick_now='N',pincode=bundle.data['pickup_pincode'])
		#neworder.save()
			print "here2"
			order_pk=neworder.pk
		except:
			print "cool shit"
		
		#create address
		try:
			address=Address.objects.create(flat_no=bundle.data['destination_address1'],locality=bundle.data['destination_address2'],city=bundle.data['destination_city'],state=bundle.data['destination_state'],pincode=bundle.data['destination_pincode'],country=bundle.data['destination_country'])
		except:
			print "haw"
			

		#create shipment
		try:
			shipment=Shipment.objects.create(order=neworder,item_name=bundle.data['item_details'],drop_address=address,drop_phone=bundle.data['recipient_phone'],drop_name=bundle.data['recipient_name'])
		except:
			print "haw"

		bundle.data['tracking_id']=shipment.real_tracking_no

		try:	
			mail="Dear "+str(bundle.data["sender_name"]) +",\n\nWe have successfully received your booking.\n\nOur Pickup representative will contact you as per your scheduled pickup time.\n\nIf you have any query, you can get in touch with us at +91-8080028081 or mail us at help@sendd.co\n\n\nHappy Sendd-ing!\n\nRegards,\nTeam Sendd"
			subject=str(bundle.data["sender_name"]) + ", We have received your parcel booking."
			send_mail(subject, mail, "Team Sendd <order@sendd.co>", [str(bundle.data["sender_email"]),"Team Sendd <order@sendd.co>"])
		except:
			print "mail not sent"
		
		return bundle


class ForgotpassResource2(MultipartResource,ModelResource):
	user = fields.ForeignKey(UserResource2, 'user')
	class Meta:
		queryset = Forgotpass.objects.all()
		resource_name = 'forgotpass'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self,bundle):
		try:
			user=User.objects.get(pk=bundle.data['phone'])
			bundle.data['user']="/api/v2/user/"+str(bundle.data['phone'])+"/"
			bundle.data['msg']="user exists"
			bundle.data['auth']=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
		
		except:
			bundle.data['user']="/api/v2/user/0/"	
			bundle.data['msg']="user not exist"

		return bundle

	def dehydrate(self,bundle):
		bundle.data['auth']="GEN"
		return bundle

class PromocodeResource2(MultipartResource,ModelResource):
	#user = fields.ForeignKey(UserResource2, 'user' ,null=True)
	class Meta:
		queryset = Promocode.objects.all()
		resource_name = 'promocode'
		authorization= Authorization()
		always_return_data = True


class OrderResource2(MultipartResource,ModelResource):
	user = fields.ForeignKey(UserResource2, 'user')
	namemail = fields.ForeignKey(NamemailResource2, 'namemail',null=True,blank=True)
	promocode = fields.ForeignKey(PromocodeResource2, 'promocode',null=True,blank=True)
	
	class Meta:
		queryset = Order.objects.all()
		resource_name = 'order'
		authorization= Authorization()
		always_return_data = True
		filtering = {
			"user": ALL,
		}

	def hydrate(self,bundle):
		r.publish("b2c", "message")
		pk=int(bundle.data['user'])
		
		bundle.data['user']="/api/v2/user/"+str(bundle.data['user'])+"/"
		print bundle.data['user']
		cust=User.objects.get(pk=pk)

		#promocode

		#print int(bundle.data['user'])
		try:
			promocode=Promocode.objects.get(pk=bundle.data['code'])

			print '1'	
			
			if (promocode.only_for_first=='Y'):

				shipment=Shipment.objects.filter(order__user__phone=pk,order__way='A')#pk is the number
				print "normal"
				print shipment.count
				print "with bracket"
				print shipment.count()
				if (shipment.count()==0):
					#everything good
					bundle.data['promocode']="/api/v2/promocode/"+str(promocode.pk)+"/"
					print str(bundle.data['code'])
					bundle.data['valid']='Y'
				else:
					print "purane users"
					bundle.data['promomsg']="You are not a first time user"
					#bundle.data['valid']='N'
			else:
				bundle.data['promocode']="/api/v2/promocode/"+str(promocode.pk)+"/"
				print str(bundle.data['code'])
				#bundle.data['valid']='Y'
		except:
			bundle.data['promomsg']="Wrong promo code"
			#bundle.data['valid']='N'
			print '2'
		#print bundle.data['promocode']

		#create nameemail
		try:
			newnamemail=Namemail.objects.filter(user=cust,name=bundle.data['name'],email=bundle.data['email'])
			if (newnamemail.count()==0) :
				newnamemail = Namemail.objects.create(user=cust,name=bundle.data['name'],email=bundle.data['email'])
				newnamemail.save()
				nm_pk=newnamemail.pk
			#bundle.obj = Address(address="nick", locality = "", password,timezone.now(),"od_test")
			else :
				for x in newnamemail:
					nm_pk= x.pk
			bundle.data['namemail']="/api/v2/namemail/"+str(nm_pk)+"/"
		
		except:
			print "cool shit"

		
		return bundle


class ShipmentResource2(MultipartResource,CORSModelResource):
	order=fields.ForeignKey(OrderResource2, 'order', null=True, blank=True)
	drop_address= fields.ForeignKey(AddressResource2, 'drop_address', null=True, blank=True)
	img = fields.FileField(attribute="img", null=True, blank=True)
	class Meta:
		queryset = Shipment.objects.all()
		resource_name = 'shipment'
		detail_uri_name = 'real_tracking_no'
		authorization=Authorization()
		always_return_data = True
		filtering = {
			"drop_address": ALL,
		}

	def prepend_urls(self):
		return [
            url(r"^(?P<resource_name>%s)/(?P<real_tracking_no>)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]



	#def over_urls(self):
	#	return [
    #   	url(r'^(?P<resource_name>%s)/(?P<track>[\w\.-]+)/$' % self._meta.resource_name, self.wrap_view('dispatch_detail'), name='api_dispatch_detail_track'),
    #        ]

	def build_filters(self, filters=None):
		print "shit"
		print filters
		if filters is None:
			filters = {}
		orm_filters = super(ShipmentResource2, self).build_filters(filters)

		if 'q' in filters:
			orm_filters['q'] = filters['q']
		return orm_filters

	def apply_filters(self, request, orm_filters):
		base_object_list = super(ShipmentResource2, self).apply_filters(request, {})
		print orm_filters
		if 'q' in orm_filters:
			return base_object_list.filter(order__user__phone=orm_filters['q'])
		print base_object_list
		return base_object_list

	def hydrate(self,bundle):

		print (bundle.data)

		try:
			override_method=bundle.request.META['HTTP_X_HTTP_METHOD_OVERRIDE']
			print "changed to PATCH"
		except:
			override_method='none'
			print "hello"
			
		if bundle.request.META['REQUEST_METHOD'] == 'POST' and override_method=='PATCH':
			print "patch"
			try:
				address=Address.objects.create(flat_no=bundle.data['flat_no'],locality=bundle.data['locality'],city=bundle.data['city'],state=bundle.data['state'],pincode=bundle.data['pincode'],country=bundle.data['country'])
				address.save()

				bundle.data['drop_address']="/api/v2/order/"+str(address.pk)+"/"
			except:
				pass
			
			
			return bundle

#sending mail and sms
		try:
			order=Order.objects.get(pk=bundle.data['order'])
			email= order.namemail.email
			name= order.namemail.name
			phone= order.user.phone

			

			
			msg0="http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to="
			msga=urllib.quote(str(phone))
			msg1="&msg=Hi+"
			msg2=urllib.quote(str(name))
			msg3="%2C+your+booking+for+parcel+has+been+received.+You+will+shortly+receive+the+contact+of+our+authorized+pickup+boy+and+a+call+on+"
			#url1="http://49.50.69.90//api/smsapi.aspx?username=doormint&password=naman123&to="+ str(bundle.data['phone']) +"&from=DORMNT&message="
			msg4=urllib.quote(str(phone))
			msg5="+for+details.&msg_type=TEXT&userid=2000142364&auth_scheme=plain&password=h0s6jgB4N&v=1.1&format=text"
			query=''.join([msg0,msga,msg1,msg2,msg3,msg4,msg5])
			print query
			#bundle.data['query']=query
			urllib2.urlopen(query)
			try:	
				mail="Dear "+str(name) +",\n\nWe have successfully received your booking.\n\nOur Pickup representative will contact you as per your scheduled pickup time.\n\nIf you have any query, you can get in touch with us at +91-8080028081 or mail us at help@sendd.co\n\n\nHappy Sendd-ing!\n\nRegards,\nTeam Sendd"
				subject=str(name) + ", We have received your parcel booking."
				send_mail(subject, mail, "Team Sendd <order@sendd.co>", [str(email),"Team Sendd <order@sendd.co>"])
			except:
				print "mail not sent"	



		except:
			print "error"

#
		try:
			bundle.data['order']="/api/v2/order/"+str(bundle.data['order'])+"/"
		except:
			print "sd"

		try:
			address_on_database=Address.objects.filter(flat_no=bundle.data['drop_flat_no'],locality=bundle.data['drop_locality'],city=bundle.data['drop_city'],state=bundle.data['drop_state'],country=bundle.data['drop_country'],pincode=bundle.data['drop_pincode'])


			if (address_on_database.count()==0) :
				address_on_database = Address.objects.create(flat_no=bundle.data['drop_flat_no'],locality=bundle.data['drop_locality'],city=bundle.data['drop_city'],state=bundle.data['drop_state'],country=bundle.data['drop_country'],pincode=bundle.data['drop_pincode'])
				address_on_database.save()
				pk=address_on_database.pk
			#bundle.obj = Address(address="nick", locality = "", password,timezone.now(),"od_test")
			else :
				for x in address_on_database:
					pk= x.id
			#queryset= Address.objects.get(number=bundle.data['number'])
			bundle.data['drop_address']="/api/v2/address/"+str(pk)+"/"

		except:
			print "fu"

		return bundle

	def dehydrate(self,bundle):
		try:
			override_method=bundle.request.META['HTTP_X_HTTP_METHOD_OVERRIDE']
			print "changed to PATCH"
		except:
			override_method='none'
			print "hello"
			
		if bundle.request.META['REQUEST_METHOD'] == 'POST' and override_method=='PATCH':
			print "patch"
			return bundle

		try:
			print 'dfd'
			print bundle.data['drop_address']
			pk=bundle.data['drop_address'].split('/')[4]
			print pk
			address=Address.objects.get(pk=pk)
			bundle.data['drop_address']=address
			print address
			bundle.data['pincode']=address.pincode
			print "shit"
		except:
			print "df"




		try:
			img_name=bundle.data['img'].split('/')[2]

			bundle.data['img']='http://128.199.159.90/static/'+ img_name
		except:
			print 'img'


		try:
			order_pk=pk=bundle.data['order'].split('/')[4]
			order=Order.objects.get(pk=pk)
			bundle.data['date']=order.date
			bundle.data['time']=order.time
			bundle.data['address']=order.address

			bundle.data['name']=order.name
			bundle.data['email']=order.email
			user=order.user
			bundle.data['name']=order.name
			bundle.data['phone']=user.phone
			bundle.data['order']=bundle.data['order'].split('/')[4]	


		except:
			print "sad"

		try:
			bundle.data['tracking_no'],bundle.data['real_tracking_no']=bundle.data['real_tracking_no'],bundle.data['tracking_no']
		except:
			'tracking number failed'
		return bundle


class XResource2(MultipartResource,ModelResource):
	C = fields.FileField(attribute="C", null=True, blank=True)
	order=fields.ForeignKey(OrderResource2, 'order' , null=True , blank =True)
	class Meta:
		queryset = X.objects.all()
		resource_name = 'x'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self, bundle):



		# print bundle.request
		#print bundle.data['Name']
		bundle.data['Cd']='dsds'
		return bundle



class PriceappResource2(CORSModelResource):
	class Meta:
		queryset = Priceapp.objects.all()
		resource_name = 'priceapp'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self, bundle):
		premium=[(60,30),(90,45),(120,50),(140,60),(160,65)]
		standard=[(30,28),(60,42),(80,47),(100,57),(105,62)]
		economy=[(240,15,30),(260,15,32),(280,15,34),(290,15,35),(290,15,35)]

		try:
			zipcode=Zipcode.objects.get(pincode=bundle.data['pincode'])
		except:
			bundle.data['msg']='invalid pin'
			return bundle

		print "count"

#		print zipcode.count()==0

		print "count"

#		if (zipcode.count()==0):
			
		bundle.data['msg']='ok'
		zone=3
		pin=bundle.data['pincode']
		if(pin.isdigit()):
			#getting zone

			t=pin[:2]
			z=pin[:3]
			bundle.data['zone']=zone

			if (t=='40' and z!= '403'):
				zone=0
				bundle.data['zone']=zone

			if (t=='41' or t=='42' or t=='43' or t=='44'):
				zone=1
				bundle.data['zone']=zone

			if (t=='56' or t=='11' or t=='60' or t=='70'):
				zone=2
				bundle.data['zone']=zone

			if (t=='78' or t=='79' or t=='18' or t=='19'):
				zone=4
				bundle.data['zone']=zone


		else:
			pin=str(pin)
			pin=urllib.quote(pin)
			state= cities[pin]
			if 'Mumbai' in pin: 
				zone=0
			elif state=='Maharashtra':
				zone=1
			elif (('Chennai' in pin) or ('Delhi' in pin) or ('Kolkata' in pin) or ('Banglore' in pin) or ('Bangalore' in pin)):
				zone=2
			elif ((state=='Jammu and Kashmir') or (state=='Assam') or (state=='Arunachal Pradesh') or (state=='Manipur') or (state=='Meghalaya') or (state=='Mizoram') or (state=='Nagaland')or (state=='Tripura')):
				zone=4

			bundle.data['zone']=zone


		try:
			l=float(bundle.data['l'])
			b=float(bundle.data['b'])
			h=float(bundle.data['h'])
			vol=(l*b*h)/5000
		except:
			vol=0	

		w=float(bundle.data['weight'])

		if (vol>w):
			w=vol
		print w
		premiumprice=1*premium[zone][0]+ (math.ceil(2*w-1))*premium[zone][1]
		standardprice=1*standard[zone][0]+ (math.ceil(2*w-1))*standard[zone][1]
		if (w>=10):
			economyprice=economy[zone][0]+4*economy[zone][1]+math.ceil(w-10)*economy[zone][2]
		elif(w>=6):
			economyprice=economy[zone][0]+math.ceil(w-6)*economy[zone][1]
		else:
			economyprice='-'

		bundle.data['premium']=premiumprice
		bundle.data['standard']=standardprice
		bundle.data['economy']=economyprice
			
			#premium

			# print bundle.request
			#print bundle.data['Name']
		return bundle			


class DateappResource2(CORSModelResource):
	class Meta:
		queryset = Dateapp.objects.all()
		resource_name = 'dateapp'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self, bundle):
		premium=[('1 Day'),('1-2 Days'),('1-2 Days'),('2-3 Days'),('2-3 Days')]
		standard=[('2 Days'),('2-3 Days'),('2-3 Days'),('3-4 Days'),('3-4 Days')]
		economy=[('2-3 Days'),('3-4 Days'),('5-6 Days'),('5-6 Days'),('7-8 Days')]
		pin=bundle.data['pincode']
	
		try:
			zipcode=Zipcode.objects.get(pincode=bundle.data['pincode'])
		except:
			bundle.data['msg']='invalid pin'
			return bundle


		bundle.data['msg']='ok'


		#getting zone
		zone=3
		pin=bundle.data['pincode']
		if(pin.isdigit()):
			#getting zone

			t=pin[:2]
			bundle.data['zone']=zone

			if (t=='40'):
				zone=0
				bundle.data['zone']=zone

			if (t=='41' or t=='42' or t=='43' or t=='44'):
				zone=1
				bundle.data['zone']=zone

			if (t=='56' or t=='11' or t=='60' or t=='70'):
				zone=2
				bundle.data['zone']=zone

			if (t=='78' or t=='79' or t=='18' or t=='19'):
				zone=4
				bundle.data['zone']=zone


		else:
			pin=str(pin)
			pin=urllib.quote(pin)
			state= cities[pin]
			if 'Mumbai' in pin: 
				zone=0
			elif state=='Maharashtra':
				zone=1
			elif (('Chennai' in pin) or ('Delhi' in pin) or ('Kolkata' in pin) or ('Banglore' in pin) or ('Bangalore' in pin)):
				zone=2
			elif ((state=='Jammu and Kashmir') or (state=='Assam') or (state=='Arunachal Pradesh') or (state=='Manipur') or (state=='Meghalaya') or (state=='Mizoram') or (state=='Nagaland')or (state=='Tripura')):
				zone=4

			bundle.data['zone']=zone



		premiumprice=premium[zone]
		standardprice=standard[zone]
		economyprice=economy[zone]
		bundle.data['premium']=premiumprice
		bundle.data['standard']=standardprice
		bundle.data['economy']=economyprice
		
		#premium

		# print bundle.request
		#print bundle.data['Name']
		return bundle


class LoginSessionResource2(MultipartResource,ModelResource):
	user = fields.ForeignKey(UserResource2, 'user' ,null=True)
	class Meta:
		queryset = LoginSession.objects.all()
		resource_name = 'loginsession'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self,bundle):
		try:
			user=User.objects.get(pk=bundle.data['phone'])
		except:
			print "fuck"
			bundle.data["success"]='notregistered'
			return bundle

		password=user.password
		bundle.data['user']="/api/v2/user/"+str(bundle.data['phone'])+"/"
		salt='crawLINGINmySKin'
		passw= str(bundle.data['password'])
		print passw
		hsh = hashlib.sha224(passw+salt).hexdigest()

		print user.name
		
		if (hsh== password):
			bundle.data["success"]='success'
			bundle.data['email']=user.email
			bundle.data['phone']=user.phone
			bundle.data['name']=user.name
			bundle.data['apikey']=user.apikey
		print bundle.data['user']
		print bundle.data['password']
		return bundle


class PromocheckResource2(MultipartResource,ModelResource):
	user = fields.ForeignKey(UserResource2, 'user' ,null=True)
	class Meta:
		queryset = Promocheck.objects.all()
		resource_name = 'promocheck'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self,bundle):
		try:
			user=User.objects.get(pk=bundle.data['phone'])
			bundle.data['user']="/api/v2/user/"+str(bundle.data['phone'])+"/"
		except:
			bundle.data["promomsg"]='Please register first'
			return bundle

		try:
			promocode=Promocode.objects.get(pk=bundle.data['code'])
			
			if (promocode.only_for_first=='Y'):
				shipment=Shipment.objects.filter(order__user__phone=bundle.data['phone'],order__way='A')
				if (shipment.count()==0):
					#everything good
					bundle.data['promomsg']=promocode.msg
					bundle.data['valid']='Y'
				else:
					bundle.data['promomsg']="You are not a first time user"
					bundle.data['valid']='N'
			else:
				bundle.data['promomsg']=promocode.msg
				bundle.data['valid']='Y'
		except:
			bundle.data['promomsg']="Wrong promo code"
			bundle.data['valid']='N'
		return bundle

	

class InvoicesentResource2(MultipartResource,ModelResource):
	order=fields.ForeignKey(OrderResource2, 'order' , null=True , blank =True)
	class Meta:
		queryset =Invoicesent.objects.all()
		resource_name = 'invoicesent'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self,bundle):
		

		order_pk=bundle.data['order'].split('/')[4]
		order=Order.objects.get(pk=order_pk)
		order.status="C"
		order.save()
			
		return bundle



class PincodecheckResource2(MultipartResource,ModelResource):
	class Meta:
		queryset = Pincodecheck.objects.all()
		resource_name = 'pincodecheck'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self,bundle):

		goodpincodes=['400076','400072','400078','400077','400080','400079','400069','400086']

		if bundle.data['pincode'] in goodpincodes:
			bundle.data['valid']=1
		else:
			bundle.data['valid']=0
			bundle.data['msg']='we dont have pickup service available in your desired pickup location.'


		return bundle


class ZipcodeResource2(MultipartResource,CORSModelResource):

	class Meta:
		queryset =Zipcode.objects.all()
		resource_name = 'zipcode'
		authorization= Authorization()
		always_return_data = True