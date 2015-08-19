import datetime
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from businessapp.models import Business, Product

__author__ = 'vatsalshah'


class Command(BaseCommand):
    help = 'Generates bills for businesses'

    option_list = BaseCommand.option_list + (
        make_option('--month',
                    dest='month',
                    default=datetime.datetime.now().month,
                    help='Bill month'),
        make_option('--year',
                    dest='year',
                    default=datetime.datetime.now().year,
                    help='Bill year'),
    )

    def handle(self, *args, **options):
        start_date = datetime.datetime(options['year'], options['month'], 1)
        end_date = datetime.datetime(options['year'], options['month'] + 1, 1) - datetime.timedelta(days=1)
        if len(args) > 0:
            business_products = []
            for business in args:
                try:
                    business_obj = Business.objects.get(pk=business)
                except Business.DoesNotExist:
                    raise CommandError('Business "%s" does not exist' % business)
                products = Product.objects.filter(Q(order__business=business), Q(status='C') | Q(status='R'),
                                                  Q(date__lt=end_date), Q(date__gt=start_date))
                business_products.append((business_obj, products))
                self.stdout.write('Successfully found business "%s"' % business)
            result = {}
            for obj in business_products:
                orders = {}
                for product in obj[1]:
                    p_order = str(product.order)
                    if p_order in orders:
                        orders[p_order]['products'].append({
                            "date": product.date,
                            "name": product.name,
                            "applied_weight": product.applied_weight,
                            "shipping_cost": product.shipping_cost,
                            "cod_cost": product.cod_cost,
                            "return_cost": product.return_cost,
                            "price": product.price,
                            "remittance": product.remittance
                        })
                        orders[p_order]["total_shipping_cost"] += int(product.shipping_cost) + int(product.return_cost) + int(
                            product.cod_cost)
                        if product.order.payment_method == 'C' and product.status != 'R':
                            orders[p_order]["total_cod_remittance"] += int(product.price)
                            if not product.remittance:
                                orders[p_order]["total_remittance_pending"] += int(product.price)
                    else:
                        orders[p_order] = {
                            "drop_address_city": product.order.city,
                            "receiver_name": product.order.name,
                            "total_shipping_cost": int(product.shipping_cost) + int(product.return_cost) + int(
                                product.cod_cost),
                            "total_cod_remittance": 0,
                            "total_remittance_pending": 0
                        }
                        orders[p_order]['products'] = [{
                                                           "date": product.date,
                                                           "name": product.name,
                                                           "applied_weight": product.applied_weight,
                                                           "shipping_cost": product.shipping_cost,
                                                           "cod_cost": product.cod_cost,
                                                           "return_cost": product.return_cost,
                                                           "price": product.price,
                                                           "remittance": product.remittance
                                                       }]
                        if product.order.payment_method == 'C' and product.status != 'R':
                            orders[p_order]["total_cod_remittance"] += int(product.price)
                            if not product.remittance:
                                orders[p_order]["total_remittance_pending"] += int(product.price)
                result[obj[0].pk] = orders
