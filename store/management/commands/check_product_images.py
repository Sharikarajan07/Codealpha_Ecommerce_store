from django.core.management.base import BaseCommand
from store.models import Product
import os


class Command(BaseCommand):
    help = 'Check product images status'

    def handle(self, *args, **options):
        self.stdout.write('Checking product images...')
        
        products = Product.objects.all()
        total_products = products.count()
        products_with_images = 0
        products_without_images = 0
        
        for product in products:
            if product.image:
                if os.path.exists(product.image.path):
                    products_with_images += 1
                    self.stdout.write(f'✓ {product.name}: {product.image.name}')
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ {product.name}: Image file missing - {product.image.name}')
                    )
            else:
                products_without_images += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ {product.name}: No image assigned')
                )
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Total products: {total_products}')
        self.stdout.write(
            self.style.SUCCESS(f'Products with images: {products_with_images}')
        )
        if products_without_images > 0:
            self.stdout.write(
                self.style.WARNING(f'Products without images: {products_without_images}')
            )
        
        if products_with_images == total_products:
            self.stdout.write(
                self.style.SUCCESS('🎉 All products have images!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Some products are missing images.')
            )
