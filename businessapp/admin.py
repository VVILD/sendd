from django.contrib import admin
from .models import *
# Register your models here.
class BusinessAdmin(admin.ModelAdmin):
	search_fields=['phone','name']
	list_display = ('phone','name','email','time')
	list_editable = ('name',)




admin.site.register(Business,BusinessAdmin)

admin.site.register(BusinessManager)