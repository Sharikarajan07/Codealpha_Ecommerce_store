from django.core.management.base import BaseCommand
from store.models import Product
import random


class Command(BaseCommand):
    help = 'Simulate product popularity by updating stock levels based on efficiency'

    def handle(self, *args, **options):
        self.stdout.write('Simulating product popularity...')
        
        # Define popularity tiers based on product efficiency
        high_demand_products = [
            'Premium Coffee Beans',    # Daily consumable
            'Greek Yogurt',           # Healthy daily essential
            'Organic Apples',         # Fresh, affordable
            'Whole Grain Bread',      # Daily staple
        ]
        
        popular_tech_products = [
            'Wireless Headphones',    # Popular tech accessory
            'Smartphone Pro',         # High-demand device
            'Fitness Tracker',        # Wellness trend
            'Bluetooth Speaker',      # Entertainment essential
        ]
        
        moderate_demand_products = [
            'Cotton T-Shirt',         # Basic clothing
            'Running Shoes',          # Fitness essential
            'LED Desk Lamp',          # Home office
            'Vitamin C Serum',        # Beauty routine
        ]
        
        # Simulate high demand (lower stock = higher sales)
        for product_name in high_demand_products:
            try:
                product = Product.objects.get(name=product_name)
                # Simulate high sales by reducing stock
                product.stock = random.randint(5, 15)  # Lower stock indicates high sales
                product.save()
                self.stdout.write(f'High demand: {product.name} - Stock: {product.stock}')
            except Product.DoesNotExist:
                continue
        
        # Simulate popular tech products
        for product_name in popular_tech_products:
            try:
                product = Product.objects.get(name=product_name)
                product.stock = random.randint(8, 20)
                product.save()
                self.stdout.write(f'Popular tech: {product.name} - Stock: {product.stock}')
            except Product.DoesNotExist:
                continue
        
        # Simulate moderate demand
        for product_name in moderate_demand_products:
            try:
                product = Product.objects.get(name=product_name)
                product.stock = random.randint(15, 35)
                product.save()
                self.stdout.write(f'Moderate demand: {product.name} - Stock: {product.stock}')
            except Product.DoesNotExist:
                continue
        
        # Set higher stock for less popular items
        other_products = Product.objects.exclude(
            name__in=high_demand_products + popular_tech_products + moderate_demand_products
        )
        
        for product in other_products:
            product.stock = random.randint(25, 50)
            product.save()
            self.stdout.write(f'Standard stock: {product.name} - Stock: {product.stock}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully simulated product popularity based on efficiency!')
        )
