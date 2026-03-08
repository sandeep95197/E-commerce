"""
Management command to add sample products with images
"""
import os
import urllib.request
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Product, Category


class Command(BaseCommand):
    help = 'Add sample products with categories and images'

    def handle(self, *args, **options):
        self.stdout.write('Creating categories...')
        
        # Create categories
        categories = {
            'Mobile': 'mobile',
            'Laptop': 'laptop',
            'Recipe': 'recipe',
        }
        
        created_categories = {}
        
        for name, slug in categories.items():
            category, created = Category.objects.get_or_create(
                name=name,
                slug=slug,
                description=f'{name} products'
            )
            created_categories[name] = category
            if created:
                self.stdout.write(f'  Created category: {name}')
        
        # Define sample products with image URLs
        products_data = [
            # Mobile phones
            {
                'name': 'iPhone 15 Pro',
                'category': 'Mobile',
                'price': 999.00,
                'description': 'Latest iPhone with A17 chip, titanium design, and advanced camera system.',
                'stock': 50,
                'image_url': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400',
            },
            {
                'name': 'Samsung Galaxy S24',
                'category': 'Mobile',
                'price': 849.00,
                'description': 'Premium Android smartphone with AI features and stunning display.',
                'stock': 45,
                'image_url': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400',
            },
            {
                'name': 'Google Pixel 8',
                'category': 'Mobile',
                'price': 699.00,
                'description': 'Pure Android experience with incredible camera and AI features.',
                'stock': 40,
                'image_url': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400',
            },
            {
                'name': 'OnePlus 12',
                'category': 'Mobile',
                'price': 799.00,
                'description': 'Flagship killer with Hasselblad cameras and fast charging.',
                'stock': 35,
                'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400',
            },
            # Laptops
            {
                'name': 'MacBook Pro 16"',
                'category': 'Laptop',
                'price': 2499.00,
                'description': 'Powerful laptop with M3 Max chip for professionals.',
                'stock': 25,
                'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400',
            },
            {
                'name': 'Dell XPS 15',
                'category': 'Laptop',
                'price': 1799.00,
                'description': 'Premium Windows laptop with stunning OLED display.',
                'stock': 30,
                'image_url': 'https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400',
            },
            {
                'name': 'HP Spectre x360',
                'category': 'Laptop',
                'price': 1499.00,
                'description': '2-in-1 convertible with sleek design and long battery life.',
                'stock': 28,
                'image_url': 'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400',
            },
            {
                'name': 'Lenovo ThinkPad X1',
                'category': 'Laptop',
                'price': 1699.00,
                'description': 'Business laptop with legendary keyboard and durability.',
                'stock': 22,
                'image_url': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400',
            },
            # Recipe / Food
            {
                'name': 'Pizza Margherita',
                'category': 'Recipe',
                'price': 12.99,
                'description': 'Classic Italian pizza with fresh mozzarella, tomatoes, and basil.',
                'stock': 100,
                'image_url': 'https://images.unsplash.com/photo-1604068549290-dea0e4a305ca?w=400',
            },
            {
                'name': 'Chocolate Cake',
                'category': 'Recipe',
                'price': 25.00,
                'description': 'Rich and moist chocolate cake with creamy frosting.',
                'stock': 50,
                'image_url': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400',
            },
            {
                'name': 'Grilled Salmon',
                'category': 'Recipe',
                'price': 28.00,
                'description': 'Fresh Atlantic salmon with herbs and lemon butter sauce.',
                'stock': 40,
                'image_url': 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=400',
            },
            {
                'name': 'Caesar Salad',
                'category': 'Recipe',
                'price': 9.99,
                'description': 'Crisp romaine lettuce with classic Caesar dressing and croutons.',
                'stock': 60,
                'image_url': 'https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=400',
            },
        ]
        
        self.stdout.write('Downloading images and creating products...')
        
        media_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        os.makedirs(media_dir, exist_ok=True)
        
        for product_data in products_data:
            category_name = product_data.pop('category')
            image_url = product_data.pop('image_url')
            
            # Check if product already exists
            if Product.objects.filter(name=product_data['name']).exists():
                self.stdout.write(f'  Product already exists: {product_data["name"]}')
                continue
            
            # Download image
            filename = f"{product_data['name'].lower().replace(' ', '_')}.jpg"
            filepath = os.path.join(media_dir, filename)
            
            try:
                urllib.request.urlretrieve(image_url, filepath)
                product_data['image'] = f'products/{filename}'
                self.stdout.write(f'  Downloaded: {product_data["name"]}')
            except Exception as e:
                self.stdout.write(f'  Warning: Could not download image for {product_data["name"]}: {e}')
                product_data['image'] = ''
            
            # Create product
            product = Product.objects.create(
                **product_data,
                category=created_categories[category_name]
            )
            self.stdout.write(f'  Created product: {product.name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully added sample products!'))
        
        # Print summary
        total_products = Product.objects.count()
        self.stdout.write(f'\nTotal products in database: {total_products}')
        
        for category in Category.objects.all():
            count = Product.objects.filter(category=category).count()
            self.stdout.write(f'  - {category.name}: {count} products')

