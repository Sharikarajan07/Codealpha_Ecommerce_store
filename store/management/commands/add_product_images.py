from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product
from PIL import Image, ImageDraw, ImageFont
import io
import random


class Command(BaseCommand):
    help = 'Add sample images to products'

    def handle(self, *args, **options):
        self.stdout.write('Adding sample images to products...')
        
        # Define colors for different categories
        category_colors = {
            'Electronics': ['#1e3a8a', '#3b82f6', '#60a5fa'],  # Blues
            'Clothing': ['#7c2d12', '#ea580c', '#fb923c'],     # Oranges
            'Books': ['#166534', '#16a34a', '#4ade80'],        # Greens
            'Home & Garden': ['#7c2d12', '#dc2626', '#f87171'], # Reds
            'Sports': ['#581c87', '#9333ea', '#c084fc'],       # Purples
        }
        
        # Product image mappings with appropriate colors and icons
        product_images = {
            'Smartphone Pro': {'color': '#1e3a8a', 'icon': '📱', 'bg_color': '#dbeafe'},
            'Laptop Ultra': {'color': '#1e40af', 'icon': '💻', 'bg_color': '#dbeafe'},
            'Wireless Headphones': {'color': '#1e3a8a', 'icon': '🎧', 'bg_color': '#dbeafe'},
            'Smart Watch': {'color': '#3730a3', 'icon': '⌚', 'bg_color': '#dbeafe'},
            
            'Cotton T-Shirt': {'color': '#ea580c', 'icon': '👕', 'bg_color': '#fed7aa'},
            'Denim Jeans': {'color': '#1e40af', 'icon': '👖', 'bg_color': '#dbeafe'},
            'Winter Jacket': {'color': '#7c2d12', 'icon': '🧥', 'bg_color': '#fed7aa'},
            'Running Shoes': {'color': '#dc2626', 'icon': '👟', 'bg_color': '#fecaca'},
            
            'Python Programming Guide': {'color': '#16a34a', 'icon': '📚', 'bg_color': '#dcfce7'},
            'Web Development Handbook': {'color': '#059669', 'icon': '📖', 'bg_color': '#dcfce7'},
            'Science Fiction Novel': {'color': '#166534', 'icon': '📘', 'bg_color': '#dcfce7'},
            
            'Coffee Maker': {'color': '#dc2626', 'icon': '☕', 'bg_color': '#fecaca'},
            'Garden Tools Set': {'color': '#16a34a', 'icon': '🛠️', 'bg_color': '#dcfce7'},
            'LED Desk Lamp': {'color': '#eab308', 'icon': '💡', 'bg_color': '#fef3c7'},
            
            'Yoga Mat': {'color': '#9333ea', 'icon': '🧘', 'bg_color': '#e9d5ff'},
            'Basketball': {'color': '#ea580c', 'icon': '🏀', 'bg_color': '#fed7aa'},
            'Fitness Tracker': {'color': '#7c3aed', 'icon': '📊', 'bg_color': '#e9d5ff'},
        }
        
        products = Product.objects.all()
        
        for product in products:
            if not product.image:  # Only add image if product doesn't have one
                image_info = product_images.get(product.name, {
                    'color': '#6b7280', 
                    'icon': '📦', 
                    'bg_color': '#f3f4f6'
                })
                
                # Create image
                image = self.create_product_image(
                    product.name,
                    image_info['color'],
                    image_info['icon'],
                    image_info['bg_color']
                )
                
                # Save image to product
                image_io = io.BytesIO()
                image.save(image_io, format='PNG', quality=95)
                image_file = ContentFile(image_io.getvalue())
                
                filename = f"{product.slug}.png"
                product.image.save(filename, image_file, save=True)
                
                self.stdout.write(f'Added image to: {product.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully added images to all products!')
        )

    def create_product_image(self, product_name, color, icon, bg_color):
        """Create a sample product image with product name and icon"""
        # Image dimensions
        width, height = 400, 400
        
        # Create image with background
        image = Image.new('RGB', (width, height), color=self.hex_to_rgb(bg_color))
        draw = ImageDraw.Draw(image)
        
        # Add gradient effect
        for i in range(height):
            alpha = i / height
            gradient_color = self.blend_colors(
                self.hex_to_rgb(bg_color),
                self.hex_to_rgb(color),
                alpha * 0.3
            )
            draw.line([(0, i), (width, i)], fill=gradient_color)
        
        # Add main color rectangle
        margin = 40
        rect_color = self.hex_to_rgb(color)
        draw.rounded_rectangle(
            [margin, margin, width-margin, height-margin],
            radius=20,
            fill=rect_color
        )
        
        # Add icon (large emoji)
        try:
            # Try to use a system font that supports emojis
            icon_font = ImageFont.truetype("seguiemj.ttf", 80)  # Windows emoji font
        except:
            try:
                icon_font = ImageFont.truetype("arial.ttf", 60)
            except:
                icon_font = ImageFont.load_default()
        
        # Calculate icon position (center)
        icon_bbox = draw.textbbox((0, 0), icon, font=icon_font)
        icon_width = icon_bbox[2] - icon_bbox[0]
        icon_height = icon_bbox[3] - icon_bbox[1]
        icon_x = (width - icon_width) // 2
        icon_y = (height - icon_height) // 2 - 30
        
        # Draw icon
        draw.text((icon_x, icon_y), icon, fill='white', font=icon_font)
        
        # Add product name
        try:
            text_font = ImageFont.truetype("arial.ttf", 24)
        except:
            text_font = ImageFont.load_default()
        
        # Wrap text if too long
        words = product_name.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=text_font)
            if bbox[2] - bbox[0] <= width - 80:  # 40px margin on each side
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw text lines
        total_text_height = len(lines) * 30
        start_y = height - margin - total_text_height - 20
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=text_font)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
            text_y = start_y + i * 30
            
            # Add text shadow
            draw.text((text_x + 2, text_y + 2), line, fill='black', font=text_font)
            # Add main text
            draw.text((text_x, text_y), line, fill='white', font=text_font)
        
        return image

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def blend_colors(self, color1, color2, factor):
        """Blend two RGB colors"""
        return tuple(
            int(color1[i] + (color2[i] - color1[i]) * factor)
            for i in range(3)
        )
