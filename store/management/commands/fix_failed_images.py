from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product
import requests
from PIL import Image
import io
import time


class Command(BaseCommand):
    help = 'Fix the failed product images with alternative URLs'

    def handle(self, *args, **options):
        self.stdout.write('Fixing failed product images...')
        
        # Alternative URLs for the failed products
        failed_product_fixes = {
            'Cotton T-Shirt': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop',
            'Winter Jacket': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=400&fit=crop',
            'Yoga Mat': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=400&fit=crop',
            'Remote Control Car': 'https://images.unsplash.com/photo-1464207687429-7505649dae38?w=400&h=400&fit=crop',
            'Movie Collection Box Set': 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=400&h=400&fit=crop',
        }
        
        updated_count = 0
        
        for product_name, image_url in failed_product_fixes.items():
            try:
                product = Product.objects.get(name=product_name)
                
                self.stdout.write(f'Fixing image for: {product.name}')
                
                # Download image
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                
                # Process image
                image = Image.open(io.BytesIO(response.content))
                
                # Convert to RGB if necessary
                if image.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                
                # Resize to consistent size
                image = image.resize((400, 400), Image.Resampling.LANCZOS)
                
                # Save to BytesIO
                image_io = io.BytesIO()
                image.save(image_io, format='JPEG', quality=90)
                image_file = ContentFile(image_io.getvalue())
                
                # Remove old image if exists
                if product.image:
                    product.image.delete(save=False)
                
                # Save new image
                filename = f"{product.slug}_fixed.jpg"
                product.image.save(filename, image_file, save=True)
                
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Fixed image for: {product.name}')
                )
                
                # Small delay
                time.sleep(0.5)
                
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Product not found: {product_name}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to fix {product_name}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully fixed {updated_count} product images!')
        )
