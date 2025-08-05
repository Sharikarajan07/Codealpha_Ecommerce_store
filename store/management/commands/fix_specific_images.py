from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product
import requests
from PIL import Image
import io
import time


class Command(BaseCommand):
    help = 'Fix specific product images: Car Air Freshener and Moisturizing Face Cream'

    def handle(self, *args, **options):
        self.stdout.write('Fixing Car Air Freshener and Moisturizing Face Cream images...')
        
        # Specific accurate URLs for the requested products
        specific_product_fixes = {
            # Car Air Freshener - Should show actual air freshener products
            'Car Air Freshener': [
                'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=400&fit=crop',  # Car accessories
                'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=400&fit=crop',  # Car interior
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop',  # Product bottle
                'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=400&fit=crop',  # Spray bottle
                'https://images.unsplash.com/photo-1570554886111-e80fcca6a029?w=400&h=400&fit=crop',  # Cosmetic bottle
            ],
            
            # Moisturizing Face Cream - Should show actual face cream/skincare products
            'Moisturizing Face Cream': [
                'https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400&h=400&fit=crop',  # Face cream jar
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop',  # Skincare product
                'https://images.unsplash.com/photo-1570554886111-e80fcca6a029?w=400&h=400&fit=crop',  # Beauty product
                'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=400&fit=crop',  # Cosmetic jar
                'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=400&h=400&fit=crop',  # Skincare cream
            ],
        }
        
        updated_count = 0
        
        for product_name, url_list in specific_product_fixes.items():
            try:
                product = Product.objects.get(name=product_name)
                
                self.stdout.write(f'Fixing image for: {product.name}')
                
                success = False
                
                for i, image_url in enumerate(url_list):
                    try:
                        self.stdout.write(f'Trying URL {i+1} for {product.name}...')
                        response = requests.get(image_url, timeout=15)
                        response.raise_for_status()
                        
                        # Verify it's actually an image
                        content_type = response.headers.get('content-type', '')
                        if not content_type.startswith('image/'):
                            self.stdout.write(f'Not an image: {content_type}')
                            continue
                        
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
                        filename = f"{product.slug}_updated.jpg"
                        product.image.save(filename, image_file, save=True)
                        
                        updated_count += 1
                        success = True
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Updated image for: {product.name} (URL {i+1})')
                        )
                        break
                        
                    except Exception as e:
                        self.stdout.write(f'URL {i+1} failed for {product.name}: {str(e)}')
                        continue
                
                if not success:
                    self.stdout.write(
                        self.style.ERROR(f'✗ All URLs failed for {product.name}')
                    )
                
                # Small delay between requests
                time.sleep(1)
                
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Product not found: {product_name}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to fix {product_name}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} specific product images!')
        )
        
        # Verify the updates
        self.stdout.write('\nVerifying updated images...')
        for product_name in specific_product_fixes.keys():
            try:
                product = Product.objects.get(name=product_name)
                if product.image:
                    self.stdout.write(f'✓ {product.name}: {product.image.name}')
                else:
                    self.stdout.write(f'✗ {product.name}: No image')
            except Product.DoesNotExist:
                self.stdout.write(f'✗ {product_name}: Product not found')
