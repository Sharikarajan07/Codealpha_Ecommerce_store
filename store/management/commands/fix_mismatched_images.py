from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product
import requests
from PIL import Image
import io
import time


class Command(BaseCommand):
    help = 'Fix mismatched product images with accurate representations'

    def handle(self, *args, **options):
        self.stdout.write('Fixing mismatched product images...')
        
        # Corrected URLs for mismatched products
        corrected_images = {
            # Automotive - More specific product images
            'Emergency Kit': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=400&fit=crop',  # First aid/emergency kit
            'Car Air Freshener': 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=400&fit=crop',  # Car accessories/interior
            
            # Toys & Games - Actual toy images
            'Remote Control Car': 'https://images.unsplash.com/photo-1607734834519-d8576ae60ea4?w=400&h=400&fit=crop',  # RC toy car
            
            # Additional improvements for better accuracy
            'Car Phone Mount': 'https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=400&h=400&fit=crop',  # Phone mount in car
            'Guitar Picks Set': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400&h=400&fit=crop',  # Guitar picks close-up
            'Building Blocks Set': 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=400&fit=crop',  # Colorful building blocks
        }
        
        # Alternative URLs in case primary ones fail
        fallback_images = {
            'Emergency Kit': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400&h=400&fit=crop',  # Medical supplies
            'Car Air Freshener': 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=400&fit=crop',  # Car interior
            'Remote Control Car': 'https://images.unsplash.com/photo-1464207687429-7505649dae38?w=400&h=400&fit=crop',  # Toy car
            'Car Phone Mount': 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=400&fit=crop',  # Car dashboard
            'Guitar Picks Set': 'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=400&h=400&fit=crop',  # Guitar accessories
            'Building Blocks Set': 'https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400&h=400&fit=crop',  # Toy blocks
        }
        
        updated_count = 0
        
        for product_name, image_url in corrected_images.items():
            try:
                product = Product.objects.get(name=product_name)
                
                self.stdout.write(f'Fixing mismatched image for: {product.name}')
                
                # Try primary URL first
                try:
                    response = requests.get(image_url, timeout=10)
                    response.raise_for_status()
                except:
                    # Use fallback URL if primary fails
                    self.stdout.write(f'Primary URL failed, trying fallback for: {product.name}')
                    fallback_url = fallback_images.get(product_name)
                    if fallback_url:
                        response = requests.get(fallback_url, timeout=10)
                        response.raise_for_status()
                    else:
                        raise Exception("No fallback URL available")
                
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
                filename = f"{product.slug}_corrected.jpg"
                product.image.save(filename, image_file, save=True)
                
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Fixed mismatched image for: {product.name}')
                )
                
                # Small delay to be respectful to the image service
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
            self.style.SUCCESS(f'Successfully fixed {updated_count} mismatched product images!')
        )
