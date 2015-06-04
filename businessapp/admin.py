from django.contrib import admin
from .models import *
# Register your models here.
class BusinessAdmin(admin.ModelAdmin):
	#search_fields=['name']
	list_display = ('username','business_name','username')
	#list_editable = ('name',)


admin.site.register(X)

admin.site.register(Business,BusinessAdmin)

admin.site.register(LoginSession)
admin.site.register(Order)
class ProductAdmin(admin.ModelAdmin):
	#search_fields=['name']
	list_display = ('name','price','weight')
	#list_editable = ('name',)

admin.site.register(Product,ProductAdmin)


admin.site.register(Payment)

admin.site.register(BusinessManager)