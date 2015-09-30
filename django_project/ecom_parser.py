from bs4 import BeautifulSoup
import urllib2
import json

def parser(url):

    soup = BeautifulSoup(urllib2.urlopen(url).read(),"lxml")
    col = [i.string.encode('utf-8').strip().replace('\xc2\xa0\xc2\xa0\xc2\xa0', "") for i in soup('td') if i.string != None and i.parent.a == None]
    del col[0]

    data =[]
    date = []
    new_data = []
    exp_date = [] #This variable stores the ETA of packages
    s = 0
    a = 0
    b = 0
    c = 0

    while s < len(col): #This loop is used to split the date and location
        date.append(col[s].split(','))
        s += 2

    while a < len(date): #This adds all the items to the list
        data.append(date[a][0].strip()), data.append(date[a][1].strip()), data.append(col[b + 1])
        exp_date.append(date[a][0])
        b += 2
        a += 1

    while c < len(data):
        new_data.append({"Location": data[c + 1], "Status" : data[c + 2], "Date" : data[c]})
        c += 3

    new_tracking = sorted(new_data, key=lambda k: k["Date"])

    l=[]
    for row in new_tracking:
	l.append(row)
	print ""
	print row["Status"]
	print "delivered" in row["Status"].lower()
        print ""

    print l
    print exp_date

parser("https://billing.ecomexpress.in/track_me/multipleawb_open/?awb=122066652&order&news_go=track+now")