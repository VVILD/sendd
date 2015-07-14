from django.shortcuts import render

from myapp.models import *
# Create your views here.

from django.http import HttpResponse

import datetime

from datetime import date


def index(request):
	today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
	today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
	today_min = datetime.datetime.combine(datetime.datetime(2015,7,7), datetime.time.min)
	today_max = datetime.datetime.combine(datetime.datetime(2015,7,7), datetime.time.max)
	latest_question_list =Order.objects.filter(book_time__range=(today_min,today_max))
	context = {'latest_question_list': latest_question_list}
	return render(request, 'polls/index.html', context)

	
def detail(request, question_id):
	return HttpResponse("You're looking at question %s." % question_id)

def results(request, question_id):
	response = "You're looking at the results of question %s."
	return HttpResponse(response % question_id)

def vote(request, question_id):
	return HttpResponse("You're voting on question %s." % question_id)
