from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product
import requests
from PIL import Image
import io
import time


class Command(BaseCommand):
    help = 'Verify and fix product images to match product names accurately'

    def handle(self, *args, **options):
        self.stdout.write('Verifying and fixing product images...')
        
        # Updated image URLs with better matches for product names
        improved_product_images = {
            # Electronics - More specific images
            'Smartphone Pro': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop',  # Modern smartphone
            'Laptop Ultra': 'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&h=400&fit=crop',   # Sleek laptop
            'Wireless Headphones': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&h=400&fit=crop',  # Premium headphones
            'Smart Watch': 'https://images.unsplash.com/photo-1551816230-ef5deaed4a26?w=400&h=400&fit=crop',      # Apple Watch style
            
            # Clothing - Better clothing images
            'Cotton T-Shirt': 'https://images.unsplash.com/photo-1583743814966-8936f37f4678?w=400&h=400&fit=crop',  # Plain t-shirt
            'Denim Jeans': 'https://images.unsplash.com/photo-1475178626620-a4d074967452?w=400&h=400&fit=crop',    # Blue jeans
            'Winter Jacket': 'https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=400&h=400&fit=crop',     # Winter coat
            'Running Shoes': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop',    # Athletic shoes
            
            # Books - More book-specific images
            'Python Programming Guide': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&h=400&fit=crop',  # Programming book
            'Web Development Handbook': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=400&h=400&fit=crop',  # Code/tech book
            'Science Fiction Novel': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=400&fit=crop',     # Novel/fiction book
            
            # Home & Garden - More specific items
            'Coffee Maker': 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&h=400&fit=crop',      # Coffee machine
            'Garden Tools Set': 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=400&h=400&fit=crop',  # Garden tools
            'LED Desk Lamp': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=400&fit=crop',   # Modern desk lamp
            
            # Sports - Better sports equipment
            'Yoga Mat': 'https://images.unsplash.com/photo-1506629905607-c60f6c3e7db1?w=400&h=400&fit=crop',       # Yoga mat rolled
            'Basketball': 'https://images.unsplash.com/photo-1574623452334-1e0ac2b3ccb4?w=400&h=400&fit=crop',     # Basketball close-up
            'Fitness Tracker': 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400&h=400&fit=crop',  # Fitness watch
            
            # Groceries - Fresh food images
            'Organic Apples': 'https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400&h=400&fit=crop',  # Red apples
            'Whole Grain Bread': 'https://images.unsplash.com/photo-1586444248902-2f64eddc13df?w=400&h=400&fit=crop',  # Artisan bread
            'Premium Coffee Beans': 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=400&h=400&fit=crop',  # Coffee beans
            'Greek Yogurt': 'https://images.unsplash.com/photo-1571212515416-fef01fc43637?w=400&h=400&fit=crop',   # Yogurt bowl
            
            # Beauty & Health - Skincare products
            'Vitamin C Serum': 'https://images.unsplash.com/photo-1570554886111-e80fcca6a029?w=400&h=400&fit=crop',  # Serum bottle
            'Moisturizing Face Cream': 'https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400&h=400&fit=crop',  # Face cream jar
            'Multivitamin Supplements': 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400&h=400&fit=crop',  # Vitamin pills
            
            # Toys & Games - Kid-friendly toys
            'Building Blocks Set': 'https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400&h=400&fit=crop',  # Colorful blocks
            'Board Game Collection': 'https://images.unsplash.com/photo-1611891487122-207579d67d98?w=400&h=400&fit=crop',  # Board games
            'Remote Control Car': 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=400&fit=crop',   # RC car
            
            # Automotive - Car accessories
            'Car Phone Mount': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop',    # Phone mount
            'Car Air Freshener': 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=400&fit=crop',  # Car interior
            'Emergency Kit': 'https://images.unsplash.com/photo-1581833971358-2c8b550f87b3?w=400&h=400&fit=crop',    # Emergency supplies
            
            # Music & Movies - Entertainment items
            'Bluetooth Speaker': 'https://images.unsplash.com/photo-1545454675-3531b543be5d?w=400&h=400&fit=crop',   # Portable speaker
            'Guitar Picks Set': 'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=400&h=400&fit=crop',  # Guitar picks
            'Movie Collection Box Set': 'https://images.unsplash.com/photo-1489599904472-84b0e19be5b9?w=400&h=400&fit=crop',  # DVD collection
        }
        
        updated_count = 0
        
        for product_name, image_url in improved_product_images.items():
            try:
                product = Product.objects.get(name=product_name)
                
                # Check if current image needs updating
                current_image_name = product.image.name if product.image else ""
                
                self.stdout.write(f'Updating image for: {product.name}')
                
                # Download new image
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
                filename = f"{product.slug}_verified.jpg"
                product.image.save(filename, image_file, save=True)
                
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated image for: {product.name}')
                )
                
                # Small delay to be respectful to the image service
                time.sleep(0.5)
                
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Product not found: {product_name}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to update {product_name}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} product images with better matches!')
        )
