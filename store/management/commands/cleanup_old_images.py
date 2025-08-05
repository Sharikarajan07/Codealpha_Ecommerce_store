from django.core.management.base import BaseCommand
from store.models import Product
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Clean up old product images and ensure new ones are used'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning up old product images...')
        
        products = Product.objects.all()
        
        for product in products:
            # Check if product has an old PNG image
            if product.image and product.image.name.endswith('.png'):
                old_image_path = product.image.path
                old_image_name = product.image.name
                
                # Look for the corresponding real JPG image
                new_image_name = f"products/{product.slug}_real.jpg"
                new_image_path = os.path.join(settings.MEDIA_ROOT, new_image_name)
                
                if os.path.exists(new_image_path):
                    # Delete the old PNG file
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                        self.stdout.write(f'Deleted old image: {old_image_name}')
                    
                    # Update the product to use the new image
                    product.image.name = new_image_name
                    product.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Updated {product.name} to use real image')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ No real image found for {product.name}')
                    )
            elif product.image and product.image.name.endswith('_real.jpg'):
                self.stdout.write(f'✓ {product.name} already using real image')
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ {product.name} has no image')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Finished cleaning up old images!')
        )
