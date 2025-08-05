from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product
import requests
from PIL import Image
import io
import time


class Command(BaseCommand):
    help = 'Ultra-precise fixes for any remaining image mismatches'

    def handle(self, *args, **options):
        self.stdout.write('Applying ultra-precise image fixes...')
        
        # Ultra-specific URLs for products that commonly have mismatches
        ultra_precise_images = {
            # Electronics - Most specific tech product images
            'Smartphone Pro': [
                'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop',  # iPhone
                'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop',  # Modern phone
                'https://images.unsplash.com/photo-1556656793-08538906a9f8?w=400&h=400&fit=crop',  # Smartphone
            ],
            
            'Laptop Ultra': [
                'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop',  # MacBook
                'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&h=400&fit=crop',  # Laptop
                'https://images.unsplash.com/photo-1484788984921-03950022c9ef?w=400&h=400&fit=crop',  # Computer
            ],
            
            'Wireless Headphones': [
                'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop',  # Over-ear
                'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&h=400&fit=crop',  # Headphones
                'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400&h=400&fit=crop',  # Audio
            ],
            
            'Smart Watch': [
                'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',  # Apple Watch
                'https://images.unsplash.com/photo-1551816230-ef5deaed4a26?w=400&h=400&fit=crop',  # Smartwatch
                'https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400&h=400&fit=crop',  # Watch
            ],
            
            # Automotive - Very specific car products
            'Emergency Kit': [
                'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400&h=400&fit=crop',  # Medical kit
                'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&h=400&fit=crop',  # First aid
                'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=400&fit=crop',  # Emergency
            ],
            
            'Car Air Freshener': [
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop',  # Bottle
                'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=400&fit=crop',  # Spray
                'https://images.unsplash.com/photo-1570554886111-e80fcca6a029?w=400&h=400&fit=crop',  # Product
            ],
            
            'Car Phone Mount': [
                'https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=400&h=400&fit=crop',  # Phone mount
                'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop',  # Car accessory
                'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=400&fit=crop',  # Car interior
            ],
            
            # Toys & Games - Actual toy images
            'Remote Control Car': [
                'https://images.unsplash.com/photo-1464207687429-7505649dae38?w=400&h=400&fit=crop',  # Toy car
                'https://images.unsplash.com/photo-1607734834519-d8576ae60ea4?w=400&h=400&fit=crop',  # RC car
                'https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400&h=400&fit=crop',  # Colorful toy
            ],
            
            'Building Blocks Set': [
                'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop',  # Lego blocks
                'https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400&h=400&fit=crop',  # Building blocks
                'https://images.unsplash.com/photo-1515630278258-407f66498911?w=400&h=400&fit=crop',  # Toys
            ],
            
            'Board Game Collection': [
                'https://images.unsplash.com/photo-1606092195730-5d7b9af1efc5?w=400&h=400&fit=crop',  # Board games
                'https://images.unsplash.com/photo-1611891487122-207579d67d98?w=400&h=400&fit=crop',  # Games
                'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=400&fit=crop',  # Game box
            ],
            
            # Music & Movies - Entertainment products
            'Guitar Picks Set': [
                'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400&h=400&fit=crop',  # Guitar picks
                'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=400&h=400&fit=crop',  # Guitar accessory
                'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400&h=400&fit=crop',  # Music accessory
            ],
            
            'Movie Collection Box Set': [
                'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=400&h=400&fit=crop',  # DVD collection
                'https://images.unsplash.com/photo-1489599904472-84b0e19be5b9?w=400&h=400&fit=crop',  # Movies
                'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=400&fit=crop',  # Media collection
            ],
            
            'Bluetooth Speaker': [
                'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop',  # Speaker
                'https://images.unsplash.com/photo-1545454675-3531b543be5d?w=400&h=400&fit=crop',  # Portable speaker
                'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400&h=400&fit=crop',  # Audio device
            ],
        }
        
        updated_count = 0
        
        for product_name, url_list in ultra_precise_images.items():
            try:
                product = Product.objects.get(name=product_name)
                
                self.stdout.write(f'Ultra-precise fix for: {product.name}')
                
                success = False
                
                for i, image_url in enumerate(url_list):
                    try:
                        self.stdout.write(f'Trying ultra-precise URL {i+1} for {product.name}...')
                        response = requests.get(image_url, timeout=15)
                        response.raise_for_status()
                        
                        # Verify content type
                        content_type = response.headers.get('content-type', '')
                        if not content_type.startswith('image/'):
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
                        filename = f"{product.slug}_ultra_precise.jpg"
                        product.image.save(filename, image_file, save=True)
                        
                        updated_count += 1
                        success = True
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Ultra-precise fix applied: {product.name} (URL {i+1})')
                        )
                        break
                        
                    except Exception as e:
                        self.stdout.write(f'Ultra-precise URL {i+1} failed for {product.name}: {str(e)}')
                        continue
                
                if not success:
                    self.stdout.write(
                        self.style.ERROR(f'✗ All ultra-precise URLs failed for {product.name}')
                    )
                
                # Small delay
                time.sleep(1)
                
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Product not found: {product_name}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Ultra-precise fix failed for {product_name}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Ultra-precise fixes complete! Updated {updated_count} products.')
        )
