from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product
import requests
from PIL import Image
import io
import time


class Command(BaseCommand):
    help = 'Final fix for product images with most accurate representations'

    def handle(self, *args, **options):
        self.stdout.write('Applying final image fixes...')
        
        # Most accurate and reliable URLs for the specific products
        final_accurate_images = {
            # Emergency Kit - Medical/first aid supplies
            'Emergency Kit': [
                'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400&h=400&fit=crop',  # Medical supplies
                'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&h=400&fit=crop',  # Kit/supplies
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop',  # Health products
            ],
            
            # Car Air Freshener - Automotive product
            'Car Air Freshener': [
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop',  # Product bottle
                'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=400&fit=crop',  # Cosmetic/spray bottle
                'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=400&fit=crop',  # Car interior
            ],
            
            # Remote Control Car - Toy car
            'Remote Control Car': [
                'https://images.unsplash.com/photo-1464207687429-7505649dae38?w=400&h=400&fit=crop',  # Toy car
                'https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400&h=400&fit=crop',  # Colorful toys
                'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop',  # Toy/game
            ],
        }
        
        updated_count = 0
        
        for product_name, url_list in final_accurate_images.items():
            try:
                product = Product.objects.get(name=product_name)
                
                self.stdout.write(f'Applying final fix for: {product.name}')
                
                image_success = False
                
                for i, image_url in enumerate(url_list):
                    try:
                        self.stdout.write(f'Trying final URL {i+1} for {product.name}...')
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
                        filename = f"{product.slug}_final.jpg"
                        product.image.save(filename, image_file, save=True)
                        
                        updated_count += 1
                        image_success = True
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Applied final fix for: {product.name} (URL {i+1})')
                        )
                        break
                        
                    except Exception as e:
                        self.stdout.write(f'Final URL {i+1} failed for {product.name}: {str(e)}')
                        continue
                
                if not image_success:
                    self.stdout.write(
                        self.style.ERROR(f'✗ All final URLs failed for {product.name}')
                    )
                
                # Small delay
                time.sleep(1)
                
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Product not found: {product_name}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed final fix for {product_name}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully applied final fixes to {updated_count} product images!')
        )
        
        # Verify the fixes
        self.stdout.write('\nVerifying final image fixes...')
        for product_name in final_accurate_images.keys():
            try:
                product = Product.objects.get(name=product_name)
                if product.image:
                    self.stdout.write(f'✓ {product.name}: {product.image.name}')
                else:
                    self.stdout.write(f'✗ {product.name}: No image')
            except Product.DoesNotExist:
                self.stdout.write(f'✗ {product_name}: Product not found')
