from django.core.management.base import BaseCommand
from businessapp.models import Product


class Command(BaseCommand):
  args = 'Arguments is not needed'
  help = 'Django admin custom command poc.'
 
  def handle(self, *args, **options):
    
    self.stdout.write("starting DTDC api")
    required_product = Product.objects.filter(company='DT')
    for product in required_product:
    	print product.mapped_tracking_no
