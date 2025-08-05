from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product
import requests
from PIL import Image
import io
import time
import os


class Command(BaseCommand):
    help = 'Force update specific product images with completely new images'

    def handle(self, *args, **options):
        self.stdout.write('Force updating Car Air Freshener and Moisturizing Face Cream images...')
        
        # Completely different and very specific URLs
        force_update_images = {
            # Car Air Freshener - Very specific automotive air freshener images
            'Car Air Freshener': [
                'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=400&h=400&fit=crop',  # Car dashboard
                'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=400&h=400&fit=crop',  # Car interior
                'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=400&fit=crop',  # Car accessories
                'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=400&fit=crop',  # Car products
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop',  # Product bottle
            ],
            
            # Moisturizing Face Cream - Very specific skincare/cosmetic images
            'Moisturizing Face Cream': [
                'https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=400&h=400&fit=crop',  # Skincare products
                'https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400&h=400&fit=crop',  # Face cream jar
                'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=400&h=400&fit=crop',  # Beauty products
                'https://images.unsplash.com/photo-1570554886111-e80fcca6a029?w=400&h=400&fit=crop',  # Cosmetic bottle
                'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=400&fit=crop',  # Skincare jar
            ],
        }
        
        updated_count = 0
        
        for product_name, url_list in force_update_images.items():
            try:
                product = Product.objects.get(name=product_name)
                
                self.stdout.write(f'Force updating: {product.name}')
                self.stdout.write(f'Current image: {product.image.name if product.image else "None"}')
                
                # Force delete old image first
                if product.image:
                    old_image_path = product.image.path
                    product.image.delete(save=False)
                    if os.path.exists(old_image_path):
                        try:
                            os.remove(old_image_path)
                            self.stdout.write(f'Deleted old image file: {old_image_path}')
                        except:
                            pass
                
                success = False
                
                for i, image_url in enumerate(url_list):
                    try:
                        self.stdout.write(f'Trying force URL {i+1} for {product.name}: {image_url}')
                        response = requests.get(image_url, timeout=20)
                        response.raise_for_status()
                        
                        # Verify content type
                        content_type = response.headers.get('content-type', '')
                        if not content_type.startswith('image/'):
                            self.stdout.write(f'Not an image: {content_type}')
                            continue
                        
                        self.stdout.write(f'Downloaded {len(response.content)} bytes')
                        
                        # Process image
                        image = Image.open(io.BytesIO(response.content))
                        self.stdout.write(f'Original image size: {image.size}, mode: {image.mode}')
                        
                        # Convert to RGB if necessary
                        if image.mode in ('RGBA', 'LA', 'P'):
                            background = Image.new('RGB', image.size, (255, 255, 255))
                            if image.mode == 'P':
                                image = image.convert('RGBA')
                            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                            image = background
                            self.stdout.write('Converted image to RGB')
                        
                        # Resize to consistent size
                        image = image.resize((400, 400), Image.Resampling.LANCZOS)
                        self.stdout.write('Resized image to 400x400')
                        
                        # Save to BytesIO
                        image_io = io.BytesIO()
                        image.save(image_io, format='JPEG', quality=90)
                        image_file = ContentFile(image_io.getvalue())
                        
                        # Save new image with timestamp to ensure uniqueness
                        import time
                        timestamp = str(int(time.time()))
                        filename = f"{product.slug}_force_updated_{timestamp}.jpg"
                        product.image.save(filename, image_file, save=True)
                        
                        updated_count += 1
                        success = True
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ FORCE UPDATED: {product.name} with {filename}')
                        )
                        break
                        
                    except Exception as e:
                        self.stdout.write(f'Force URL {i+1} failed for {product.name}: {str(e)}')
                        continue
                
                if not success:
                    self.stdout.write(
                        self.style.ERROR(f'✗ ALL FORCE URLs FAILED for {product.name}')
                    )
                
                # Delay between products
                time.sleep(2)
                
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Product not found: {product_name}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Force update failed for {product_name}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'FORCE UPDATE COMPLETE! Updated {updated_count} products.')
        )
        
        # Final verification with detailed info
        self.stdout.write('\n' + '='*60)
        self.stdout.write('FINAL VERIFICATION OF FORCE UPDATES')
        self.stdout.write('='*60)
        
        for product_name in force_update_images.keys():
            try:
                product = Product.objects.get(name=product_name)
                if product.image:
                    self.stdout.write(f'✓ {product.name}:')
                    self.stdout.write(f'  File: {product.image.name}')
                    self.stdout.write(f'  URL: {product.image.url}')
                    self.stdout.write(f'  Size: {product.image.size} bytes')
                else:
                    self.stdout.write(f'✗ {product.name}: NO IMAGE!')
            except Product.DoesNotExist:
                self.stdout.write(f'✗ {product_name}: PRODUCT NOT FOUND!')
        
        self.stdout.write('='*60)
        self.stdout.write('Images should now be visibly different!')
        self.stdout.write('Clear browser cache and refresh to see changes.')
        self.stdout.write('='*60)
