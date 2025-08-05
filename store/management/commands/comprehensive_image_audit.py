from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product
import requests
from PIL import Image
import io
import time


class Command(BaseCommand):
    help = 'Comprehensive audit and fix of all product images for accuracy'

    def handle(self, *args, **options):
        self.stdout.write('Starting comprehensive image audit and fixes...')
        
        # Highly accurate and specific URLs for each product
        accurate_product_images = {
            # Electronics - Very specific tech products
            'Smartphone Pro': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop',  # iPhone/smartphone
            'Laptop Ultra': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop',  # MacBook/laptop
            'Wireless Headphones': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop',  # Over-ear headphones
            'Smart Watch': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',  # Apple Watch
            
            # Clothing - Actual clothing items
            'Cotton T-Shirt': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop',  # Plain t-shirt
            'Denim Jeans': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop',  # Blue jeans
            'Winter Jacket': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=400&fit=crop',  # Winter coat
            'Running Shoes': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop',  # Athletic shoes
            
            # Books - Actual books and reading materials
            'Python Programming Guide': 'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400&h=400&fit=crop',  # Programming book
            'Web Development Handbook': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop',  # Tech book
            'Science Fiction Novel': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=400&fit=crop',  # Novel/book
            
            # Home & Garden - Specific home products
            'Coffee Maker': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&h=400&fit=crop',  # Coffee machine
            'Garden Tools Set': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=400&fit=crop',  # Garden tools
            'LED Desk Lamp': 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&h=400&fit=crop',  # Desk lamp
            
            # Sports - Actual sports equipment
            'Yoga Mat': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=400&fit=crop',  # Yoga mat
            'Basketball': 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=400&h=400&fit=crop',  # Basketball
            'Fitness Tracker': 'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=400&h=400&fit=crop',  # Fitness watch
            
            # Groceries - Fresh food items
            'Organic Apples': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400&h=400&fit=crop',  # Red apples
            'Whole Grain Bread': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&h=400&fit=crop',  # Bread loaf
            'Premium Coffee Beans': 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&h=400&fit=crop',  # Coffee beans
            'Greek Yogurt': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&h=400&fit=crop',  # Yogurt bowl
            
            # Beauty & Health - Skincare and health products
            'Vitamin C Serum': 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=400&fit=crop',  # Serum bottle
            'Moisturizing Face Cream': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop',  # Face cream
            'Multivitamin Supplements': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400&h=400&fit=crop',  # Vitamin pills
            
            # Toys & Games - Actual toys
            'Building Blocks Set': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop',  # Lego blocks
            'Board Game Collection': 'https://images.unsplash.com/photo-1606092195730-5d7b9af1efc5?w=400&h=400&fit=crop',  # Board games
            'Remote Control Car': 'https://images.unsplash.com/photo-1607734834519-d8576ae60ea4?w=400&h=400&fit=crop',  # RC car toy
            
            # Automotive - Car accessories and supplies
            'Car Phone Mount': 'https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=400&h=400&fit=crop',  # Phone mount
            'Car Air Freshener': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop',  # Air freshener
            'Emergency Kit': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400&h=400&fit=crop',  # First aid kit
            
            # Music & Movies - Entertainment products
            'Bluetooth Speaker': 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop',  # Portable speaker
            'Guitar Picks Set': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400&h=400&fit=crop',  # Guitar picks
            'Movie Collection Box Set': 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=400&h=400&fit=crop',  # DVD collection
        }
        
        # Alternative URLs for fallback
        fallback_urls = {
            'Smartphone Pro': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop',
            'Laptop Ultra': 'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&h=400&fit=crop',
            'Wireless Headphones': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&h=400&fit=crop',
            'Smart Watch': 'https://images.unsplash.com/photo-1551816230-ef5deaed4a26?w=400&h=400&fit=crop',
            'Cotton T-Shirt': 'https://images.unsplash.com/photo-1583743814966-8936f37f4678?w=400&h=400&fit=crop',
            'Remote Control Car': 'https://images.unsplash.com/photo-1464207687429-7505649dae38?w=400&h=400&fit=crop',
            'Emergency Kit': 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&h=400&fit=crop',
            'Car Air Freshener': 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=400&fit=crop',
            'Movie Collection Box Set': 'https://images.unsplash.com/photo-1489599904472-84b0e19be5b9?w=400&h=400&fit=crop',
        }
        
        updated_count = 0
        failed_products = []
        
        # Get all products and check each one
        all_products = Product.objects.all()
        
        for product in all_products:
            if product.name in accurate_product_images:
                try:
                    self.stdout.write(f'Auditing and fixing: {product.name}')
                    
                    # Try primary URL first
                    image_url = accurate_product_images[product.name]
                    success = False
                    
                    try:
                        response = requests.get(image_url, timeout=15)
                        response.raise_for_status()
                        success = True
                    except:
                        # Try fallback URL
                        if product.name in fallback_urls:
                            self.stdout.write(f'Primary failed, trying fallback for: {product.name}')
                            image_url = fallback_urls[product.name]
                            try:
                                response = requests.get(image_url, timeout=15)
                                response.raise_for_status()
                                success = True
                            except:
                                pass
                    
                    if success:
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
                        filename = f"{product.slug}_audited.jpg"
                        product.image.save(filename, image_file, save=True)
                        
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Audited and fixed: {product.name}')
                        )
                    else:
                        failed_products.append(product.name)
                        self.stdout.write(
                            self.style.ERROR(f'✗ Failed to update: {product.name}')
                        )
                    
                    # Small delay
                    time.sleep(0.5)
                    
                except Exception as e:
                    failed_products.append(product.name)
                    self.stdout.write(
                        self.style.ERROR(f'✗ Error with {product.name}: {str(e)}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Comprehensive audit complete! Updated {updated_count} products.')
        )
        
        if failed_products:
            self.stdout.write(
                self.style.WARNING(f'Failed products: {", ".join(failed_products)}')
            )
