import difflib

__author__ = 'vatsalshah'

states = ['Andaman and Nicobar Islands',	'Andhra Pradesh',	'Arunachal Pradesh',	'Assam',	'Bihar',	'Chandigarh',	'Chhattisgarh',	'Dadra and Nagar Haveli',	'Daman and Diu',	'Delhi',	'Goa',	'Gujarat',	'Haryana',	'Himachal Pradesh',	'Jammu and Kashmir',	'Jharkhand',	'Karnataka',	'Kerala',	'Lakshadweep',	'Madhya Pradesh',	'Maharashtra',	'Manipur',	'Meghalaya',	'Mizoram',	'Nagaland',	'Orissa',	'Puducherry',	'Punjab',	'Rajasthan',	'Sikkim',	'Tamil Nadu',	'Tripura',	'Uttar Pradesh',	'Uttarakhand',	'West Bengal',	'Telangana',	'Odisha',	'Uttaranchal']
restricted_states = ['Bihar', 'Jharkhand', 'Madhya Pradesh', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Sikkim', 'Tripura', 'Uttar Pradesh']


def get_closest_state(state):
    return difflib.get_close_matches(str(state).title(), states, cutoff=0.60)


def is_state(state):
    if state in states:
        return True
    else:
        return False


def is_restricted(state):
    if state in restricted_states:
        return True
    else:
        return False