import difflib

__author__ = 'vatsalshah'

states = ['Andaman and Nicobar Islands',	'Andhra Pradesh',	'Arunachal Pradesh',	'Assam',	'Bihar',	'Chandigarh',	'Chhattisgarh',	'Dadra and Nagar Haveli',	'Daman and Diu',	'Delhi',	'Goa',	'Gujarat',	'Haryana',	'Himachal Pradesh',	'Jammu and Kashmir',	'Jharkhand',	'Karnataka',	'Kerala',	'Lakshadweep',	'Madhya Pradesh',	'Maharashtra',	'Manipur',	'Meghalaya',	'Mizoram',	'Nagaland',	'Orissa',	'Puducherry',	'Punjab',	'Rajasthan',	'Sikkim',	'Tamil Nadu',	'Tripura',	'Uttar Pradesh',	'Uttarakhand',	'West Bengal',	'Telangana',	'Odisha',	'Uttaranchal']


def get_closest_state(state):
    return difflib.get_close_matches(state, states, cutoff=0.60)