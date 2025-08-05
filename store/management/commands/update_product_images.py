from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product
import requests
from PIL import Image
import io
import time


class Command(BaseCommand):
    help = 'Update product images with real images from Unsplash'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all images, even if they already exist',
        )
        parser.add_argument(
            '--product',
            type=str,
            help='Update image for specific product by name',
        )

    def handle(self, *args, **options):
        self.stdout.write('Updating product images...')
        
        # Extended image mappings with more options
        product_image_urls = {
            'Smartphone Pro': [
                'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=400&h=400&fit=crop'
            ],
            'Laptop Ultra': [
                'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1484788984921-03950022c9ef?w=400&h=400&fit=crop'
            ],
            'Wireless Headphones': [
                'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400&h=400&fit=crop'
            ],
            'Smart Watch': [
                'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1551816230-ef5deaed4a26?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400&h=400&fit=crop'
            ],
            'Cotton T-Shirt': [
                'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1583743814966-8936f37f4678?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=400&h=400&fit=crop'
            ],
            'Denim Jeans': [
                'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1475178626620-a4d074967452?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop'
            ],
            'Winter Jacket': [
                'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=400&fit=crop'
            ],
            'Running Shoes': [
                'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop'
            ],
            'Python Programming Guide': [
                'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=400&h=400&fit=crop'
            ],
            'Web Development Handbook': [
                'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=400&h=400&fit=crop'
            ],
            'Science Fiction Novel': [
                'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=400&fit=crop'
            ],
            'Coffee Maker': [
                'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400&h=400&fit=crop'
            ],
            'Garden Tools Set': [
                'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1592150621744-aca64f48394a?w=400&h=400&fit=crop'
            ],
            'LED Desk Lamp': [
                'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400&h=400&fit=crop'
            ],
            'Yoga Mat': [
                'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1506629905607-c60f6c3e7db1?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop'
            ],
            'Basketball': [
                'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1574623452334-1e0ac2b3ccb4?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1519861531473-9200262188bf?w=400&h=400&fit=crop'
            ],
            'Fitness Tracker': [
                'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop'
            ],
        }
        
        # Filter products based on options
        if options['product']:
            products = Product.objects.filter(name__icontains=options['product'])
            if not products.exists():
                self.stdout.write(
                    self.style.ERROR(f'No product found with name containing: {options["product"]}')
                )
                return
        else:
            products = Product.objects.all()
        
        for product in products:
            # Skip if product already has image and not forcing update
            if product.image and not options['force']:
                self.stdout.write(f'Skipping {product.name} (already has image)')
                continue
                
            if product.name in product_image_urls:
                urls = product_image_urls[product.name]
                
                # Try each URL until one works
                for i, image_url in enumerate(urls):
                    try:
                        self.stdout.write(f'Downloading image {i+1}/{len(urls)} for {product.name}...')
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
                            self.style.SUCCESS(f'✓ Updated image for: {product.name}')
                        )
                        break  # Success, move to next product
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Failed to download image {i+1} for {product.name}: {str(e)}')
                        )
                        if i == len(urls) - 1:  # Last URL failed
                            self.stdout.write(
                                self.style.ERROR(f'✗ All image URLs failed for {product.name}')
                            )
                    
                    # Small delay between attempts
                    time.sleep(0.5)
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ No image URLs defined for: {product.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Finished updating product images!')
        )
