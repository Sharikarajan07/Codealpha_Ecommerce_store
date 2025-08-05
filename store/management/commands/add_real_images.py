from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product
import requests
from PIL import Image
import io
import time


class Command(BaseCommand):
    help = 'Add real product images from URLs'

    def handle(self, *args, **options):
        self.stdout.write('Adding real product images...')
        
        # Real product image URLs (using free stock images)
        product_images = {
            'Smartphone Pro': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop',
            'Laptop Ultra': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop',
            'Wireless Headphones': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop',
            'Smart Watch': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
            
            'Cotton T-Shirt': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop',
            'Denim Jeans': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop',
            'Winter Jacket': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=400&fit=crop',
            'Running Shoes': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop',
            
            'Python Programming Guide': 'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400&h=400&fit=crop',
            'Web Development Handbook': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop',
            'Science Fiction Novel': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=400&fit=crop',
            
            'Coffee Maker': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&h=400&fit=crop',
            'Garden Tools Set': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=400&fit=crop',
            'LED Desk Lamp': 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&h=400&fit=crop',
            
            'Yoga Mat': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=400&fit=crop',
            'Basketball': 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=400&h=400&fit=crop',
            'Fitness Tracker': 'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=400&h=400&fit=crop',

            # Groceries
            'Organic Apples': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400&h=400&fit=crop',
            'Whole Grain Bread': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&h=400&fit=crop',
            'Premium Coffee Beans': 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&h=400&fit=crop',
            'Greek Yogurt': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&h=400&fit=crop',

            # Beauty & Health
            'Vitamin C Serum': 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=400&fit=crop',
            'Moisturizing Face Cream': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop',
            'Multivitamin Supplements': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400&h=400&fit=crop',

            # Toys & Games
            'Building Blocks Set': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop',
            'Board Game Collection': 'https://images.unsplash.com/photo-1606092195730-5d7b9af1efc5?w=400&h=400&fit=crop',
            'Remote Control Car': 'https://images.unsplash.com/photo-1464207687429-7505649dae38?w=400&h=400&fit=crop',

            # Automotive
            'Car Phone Mount': 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=400&fit=crop',
            'Car Air Freshener': 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=400&fit=crop',
            'Emergency Kit': 'https://images.unsplash.com/photo-1581833971358-2c8b550f87b3?w=400&h=400&fit=crop',

            # Music & Movies
            'Bluetooth Speaker': 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop',
            'Guitar Picks Set': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400&h=400&fit=crop',
            'Movie Collection Box Set': 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=400&h=400&fit=crop',
        }
        
        products = Product.objects.all()
        
        for product in products:
            if product.name in product_images:
                image_url = product_images[product.name]
                
                try:
                    # Download image
                    self.stdout.write(f'Downloading image for {product.name}...')
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
                    filename = f"{product.slug}_real.jpg"
                    product.image.save(filename, image_file, save=True)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Added real image to: {product.name}')
                    )
                    
                    # Small delay to be respectful to the image service
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed to add image for {product.name}: {str(e)}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ No image URL defined for: {product.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Finished adding real product images!')
        )
