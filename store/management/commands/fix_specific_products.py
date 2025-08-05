from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product
import requests
from PIL import Image
import io
import time


class Command(BaseCommand):
    help = 'Fix specific mismatched product images with very accurate representations'

    def handle(self, *args, **options):
        self.stdout.write('Fixing specific mismatched product images...')
        
        # Very specific and accurate URLs for the mentioned products
        specific_fixes = {
            # Emergency Kit - Should show first aid/emergency supplies
            'Emergency Kit': 'https://images.unsplash.com/photo-1603398938795-b6d0b6b1b1b1?w=400&h=400&fit=crop',
            
            # Car Air Freshener - Should show actual air freshener product
            'Car Air Freshener': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop',
            
            # Remote Control Car - Should show actual RC toy car
            'Remote Control Car': 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=400&fit=crop',
        }
        
        # Backup URLs with different search terms
        backup_fixes = {
            'Emergency Kit': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400&h=400&fit=crop',  # Medical/health supplies
            'Car Air Freshener': 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=400&fit=crop',  # Bottle/spray product
            'Remote Control Car': 'https://images.unsplash.com/photo-1464207687429-7505649dae38?w=400&h=400&fit=crop',  # Toy car
        }
        
        # Final fallback - generic but appropriate images
        final_fallback = {
            'Emergency Kit': 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&h=400&fit=crop',  # Kit/supplies
            'Car Air Freshener': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop',  # Product bottle
            'Remote Control Car': 'https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400&h=400&fit=crop',  # Toy/colorful
        }
        
        updated_count = 0
        
        for product_name in specific_fixes.keys():
            try:
                product = Product.objects.get(name=product_name)
                
                self.stdout.write(f'Fixing specific image for: {product.name}')
                
                # Try multiple URLs until one works
                urls_to_try = [
                    specific_fixes[product_name],
                    backup_fixes[product_name],
                    final_fallback[product_name]
                ]
                
                image_downloaded = False
                
                for i, image_url in enumerate(urls_to_try):
                    try:
                        self.stdout.write(f'Trying URL {i+1} for {product.name}...')
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
                        filename = f"{product.slug}_specific_fix.jpg"
                        product.image.save(filename, image_file, save=True)
                        
                        updated_count += 1
                        image_downloaded = True
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Fixed specific image for: {product.name} (URL {i+1})')
                        )
                        break
                        
                    except Exception as e:
                        self.stdout.write(f'URL {i+1} failed for {product.name}: {str(e)}')
                        continue
                
                if not image_downloaded:
                    self.stdout.write(
                        self.style.ERROR(f'✗ All URLs failed for {product.name}')
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
            self.style.SUCCESS(f'Successfully fixed {updated_count} specific product images!')
        )
