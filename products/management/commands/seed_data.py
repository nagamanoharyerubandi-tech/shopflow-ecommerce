from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from accounts.models import UserProfile, Address
from products.models import Category, Product, ProductReview
from orders.models import Order, OrderItem
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Seeds database with initial sample categories, products, users, and orders'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting database seed...'))

        # 1. Create Superuser (Admin)
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@shopflow.com',
                'first_name': 'Admin',
                'last_name': 'Manager',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Admin user created: admin / admin123'))
        else:
            self.stdout.write('Admin user already exists.')

        # 2. Create Test Customer
        customer, created = User.objects.get_or_create(
            username='krish',
            defaults={
                'email': 'krish@example.com',
                'first_name': 'Krish',
                'last_name': 'Kumar',
            }
        )
        if created:
            customer.set_password('password123')
            customer.save()
            customer.profile.phone = '+91 9876543210'
            customer.profile.gender = 'M'
            customer.profile.save()
            self.stdout.write(self.style.SUCCESS('Customer created: krish / password123'))
        else:
            self.stdout.write('Customer krish already exists.')

        # Add customer default address
        address, _ = Address.objects.get_or_create(
            user=customer,
            full_name='Krish Kumar',
            phone='9876543210',
            address_line_1='Flat 402, Sunshine Residency, Bannerghatta Road',
            address_line_2='Near Apollo Hospital',
            city='Bengaluru',
            state='Karnataka',
            postal_code='560076',
            country='India',
            address_type='Home',
            is_default=True
        )

        # 3. Create Categories
        categories_data = [
            {
                'name': 'Electronics & Gadgets',
                'description': 'Latest smartphones, premium laptops, wireless audio, smartwatches and accessories.',
                'icon': 'bi-laptop',
                'is_featured': True,
            },
            {
                'name': 'Fashion & Apparel',
                'description': 'Trendy clothing, stylish footwear, watches, sunglasses and bags for men and women.',
                'icon': 'bi-bag-heart',
                'is_featured': True,
            },
            {
                'name': 'Home & Kitchen',
                'description': 'Modern cookware, home decor essentials, appliances and comfortable bedding.',
                'icon': 'bi-house-heart',
                'is_featured': True,
            },
            {
                'name': 'Books & Stationery',
                'description': 'Bestselling fiction, technology guides, business classics and artistic notebooks.',
                'icon': 'bi-book',
                'is_featured': True,
            },
            {
                'name': 'Beauty & Personal Care',
                'description': 'Premium skincare, hair treatments, wellness products and signature fragrances.',
                'icon': 'bi-flower1',
                'is_featured': True,
            },
            {
                'name': 'Sports & Fitness',
                'description': 'Gym gear, yoga mats, resistance bands, sports accessories and outdoor equipment.',
                'icon': 'bi-activity',
                'is_featured': False,
            },
        ]

        categories = {}
        for cat_info in categories_data:
            cat, _ = Category.objects.update_or_create(
                name=cat_info['name'],
                defaults=cat_info
            )
            categories[cat.name] = cat
        self.stdout.write(self.style.SUCCESS(f'Created/Updated {len(categories)} categories.'))

        # 4. Create Products
        products_data = [
            # Electronics
            {
                'category': categories['Electronics & Gadgets'],
                'name': 'Sony WH-1000XM5 Noise Canceling Wireless Headphones',
                'brand': 'Sony',
                'short_description': 'Industry-leading noise cancellation with 2 processors, 8 mics, 30hr battery.',
                'description': 'The Sony WH-1000XM5 wireless noise cancelling headphones rewrite the rules for distraction-free listening. Equipped with two processors controlling eight microphones, Auto NC Optimizer for automatically optimizing noise cancellation based on your wearing conditions and environment, and a specially designed driver unit.',
                'price': Decimal('29990.00'),
                'discount_price': Decimal('24990.00'),
                'stock': 25,
                'is_available': True,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.8'),
                'num_reviews': 38,
            },
            {
                'category': categories['Electronics & Gadgets'],
                'name': 'Apple MacBook Air M3 (13-inch, 16GB Unified Memory, 512GB SSD)',
                'brand': 'Apple',
                'short_description': 'Blazing-fast M3 chip, Liquid Retina display, up to 18 hours battery life.',
                'description': 'The 13-inch MacBook Air is impossibly thin and fast. Supercharged by the next-generation M3 chip, it delivers extraordinary performance and up to 18 hours of battery life to breeze through work and play.',
                'price': Decimal('134900.00'),
                'discount_price': Decimal('119900.00'),
                'stock': 12,
                'is_available': True,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.9'),
                'num_reviews': 54,
            },
            {
                'category': categories['Electronics & Gadgets'],
                'name': 'Samsung Galaxy S24 Ultra 5G (Titanium Gray, 256GB)',
                'brand': 'Samsung',
                'short_description': '200MP camera with Galaxy AI, Snapdragon 8 Gen 3, S-Pen included.',
                'description': 'Meet Galaxy S24 Ultra, the ultimate form of Galaxy Ultra with a new titanium exterior and a 6.8-inch flat display. It is an absolute design marvel with Galaxy AI built-in.',
                'price': Decimal('129999.00'),
                'discount_price': Decimal('114999.00'),
                'stock': 18,
                'is_available': True,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.7'),
                'num_reviews': 42,
            },
            {
                'category': categories['Electronics & Gadgets'],
                'name': 'Apple Watch Series 9 GPS 45mm Midnight Aluminum Case',
                'brand': 'Apple',
                'short_description': 'Powerful S9 SiP, Double Tap gesture, Blood Oxygen and ECG monitoring.',
                'description': 'Smarter, brighter, mightier. Apple Watch Series 9 helps you stay connected, active, healthy, and safe. Featuring the double tap gesture, a magical way to interact with Apple Watch without touching the screen.',
                'price': Decimal('44900.00'),
                'discount_price': Decimal('38900.00'),
                'stock': 15,
                'is_available': True,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.6'),
                'num_reviews': 29,
            },

            # Fashion
            {
                'category': categories['Fashion & Apparel'],
                'name': "Levi's Men's 511 Slim Fit Stretchable Denim Jeans",
                'brand': "Levi's",
                'short_description': 'Classic modern slim fit with room to move, premium denim craftsmanship.',
                'description': 'A modern slim with room to move, the 511 Slim Fit Stretch Jeans are a classic since right now. These jeans sit below the waist with a slim leg from hip to ankle.',
                'price': Decimal('3499.00'),
                'discount_price': Decimal('2299.00'),
                'stock': 40,
                'is_available': True,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1542272604-780c96856592?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.5'),
                'num_reviews': 65,
            },
            {
                'category': categories['Fashion & Apparel'],
                'name': "Nike Air Max 270 Men's Running Shoes (Black/White)",
                'brand': 'Nike',
                'short_description': 'Large Max Air unit for responsive cushioning, breathable mesh upper.',
                'description': "Nike's first lifestyle Air Max brings you style, comfort and big attitude in the Nike Air Max 270. The design draws inspiration from Air Max icons, showcasing Nike's greatest innovation with its large window and fresh array of colors.",
                'price': Decimal('13995.00'),
                'discount_price': Decimal('10995.00'),
                'stock': 22,
                'is_available': True,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.8'),
                'num_reviews': 88,
            },
            {
                'category': categories['Fashion & Apparel'],
                'name': "Fossil Grant Chronograph Blue Dial Men's Watch",
                'brand': 'Fossil',
                'short_description': 'Genuine leather strap, roman numeral hour markers, 50m water resistant.',
                'description': 'Modeled after vintage clocks, our Grant collection has a timeless appeal. Roman numerals are paired with precise chronograph movement and a rich luggage-leather strap.',
                'price': Decimal('12495.00'),
                'discount_price': Decimal('8995.00'),
                'stock': 14,
                'is_available': True,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.6'),
                'num_reviews': 31,
            },
            {
                'category': categories['Fashion & Apparel'],
                'name': "Ray-Ban Classic Polarized Aviator Sunglasses",
                'brand': 'Ray-Ban',
                'short_description': 'Iconic teardrop shape, 100% UV protection polarized crystal green lenses.',
                'description': 'Currently one of the most iconic sunglass models in the world, Ray-Ban Aviator Classic sunglasses were originally designed for U.S. aviators in 1937. Timeless style meets high-tech optics.',
                'price': Decimal('10890.00'),
                'discount_price': Decimal('8490.00'),
                'stock': 20,
                'is_available': True,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.7'),
                'num_reviews': 45,
            },

            # Home & Kitchen
            {
                'category': categories['Home & Kitchen'],
                'name': 'Philips Digital Air Fryer with Rapid Air Technology (4.1 Litre)',
                'brand': 'Philips',
                'short_description': 'Fry with up to 90% less fat, digital touch screen with 7 presets.',
                'description': 'Philips brings the world’s No. 1 Airfryer to everyone’s home. Enjoy healthy food that’s crispy on the outside and tender on the inside, thanks to Rapid Air Technology.',
                'price': Decimal('9995.00'),
                'discount_price': Decimal('6999.00'),
                'stock': 30,
                'is_available': True,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.6'),
                'num_reviews': 52,
            },
            {
                'category': categories['Home & Kitchen'],
                'name': 'Prestige Iris Plus 750 Watt Mixer Grinder with 4 Jars',
                'brand': 'Prestige',
                'short_description': 'Heavy duty 750W motor, stainless steel multipurpose grinding jars.',
                'description': 'Prestige Iris Plus delivers fast and fine grinding. Powerful 750 watt motor allows you to grind even the toughest ingredients with ease.',
                'price': Decimal('6295.00'),
                'discount_price': Decimal('3299.00'),
                'stock': 35,
                'is_available': True,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.3'),
                'num_reviews': 77,
            },
            {
                'category': categories['Home & Kitchen'],
                'name': 'Milton Stainless Steel Vacuum Insulated Water Bottle (1000ml)',
                'brand': 'Milton',
                'short_description': '24 hours hot and cold retention, 100% leak proof rust-free steel.',
                'description': 'Double walled vacuum insulated bottle made from food grade 304 stainless steel. Keeps beverages hot or cold for a full 24 hours.',
                'price': Decimal('1199.00'),
                'discount_price': Decimal('849.00'),
                'stock': 50,
                'is_available': True,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.5'),
                'num_reviews': 110,
            },

            # Books & Stationery
            {
                'category': categories['Books & Stationery'],
                'name': 'Atomic Habits by James Clear (Hardcover Collector Edition)',
                'brand': 'Penguin Random House',
                'short_description': 'An Easy & Proven Way to Build Good Habits & Break Bad Ones.',
                'description': 'No matter your goals, Atomic Habits offers a proven framework for improving every day. James Clear, one of the world’s leading experts on habit formation, reveals practical strategies that will teach you exactly how to form good habits, break bad ones, and master tiny behaviors.',
                'price': Decimal('899.00'),
                'discount_price': Decimal('549.00'),
                'stock': 60,
                'is_available': True,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.9'),
                'num_reviews': 240,
            },
            {
                'category': categories['Books & Stationery'],
                'name': 'The Psychology of Money by Morgan Housel',
                'brand': 'Harriman House',
                'short_description': 'Timeless lessons on wealth, greed, and happiness.',
                'description': 'Doing well with money isn’t necessarily about what you know. It’s about how you behave. And behavior is hard to teach, even to really smart people. Morgan Housel shares 19 short stories exploring the strange ways people think about money.',
                'price': Decimal('499.00'),
                'discount_price': Decimal('320.00'),
                'stock': 45,
                'is_available': True,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.8'),
                'num_reviews': 195,
            },
            {
                'category': categories['Books & Stationery'],
                'name': 'Parker Sonnet Premium Black Lacquer Fountain Pen',
                'brand': 'Parker',
                'short_description': 'Handcrafted 18k solid gold nib with rhodium finish and luxury gift box.',
                'description': 'A classic expression of refined style, Sonnet is Parker’s symbol of elegance. Hand assembled and checked for flawless quality, with high precision and exceptional writing comfort.',
                'price': Decimal('14999.00'),
                'discount_price': Decimal('11499.00'),
                'stock': 8,
                'is_available': True,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.7'),
                'num_reviews': 18,
            },

            # Beauty & Personal Care
            {
                'category': categories['Beauty & Personal Care'],
                'name': 'Minimalist 10% Vitamin C Face Serum for Glowing Skin (30ml)',
                'brand': 'Minimalist',
                'short_description': 'Formulated with Centella water, fights pigmentation and early signs of aging.',
                'description': 'A glow-boosting serum formulated with a stable Vitamin C derivative (Ethyl Ascorbic Acid) that gives radiant and glowing skin without irritation.',
                'price': Decimal('699.00'),
                'discount_price': Decimal('629.00'),
                'stock': 70,
                'is_available': True,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.6'),
                'num_reviews': 140,
            },
            {
                'category': categories['Beauty & Personal Care'],
                'name': 'Dior Sauvage Eau De Parfum for Men (100ml)',
                'brand': 'Dior',
                'short_description': 'Radically fresh composition, raw and noble all at once with bergamot.',
                'description': 'A powerfully fresh fragrance composition. Raw and noble all at once, dictated by a name that has the ring of a manifesto.',
                'price': Decimal('14500.00'),
                'discount_price': Decimal('12999.00'),
                'stock': 10,
                'is_available': True,
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.9'),
                'num_reviews': 63,
            },

            # Sports & Fitness
            {
                'category': categories['Sports & Fitness'],
                'name': 'Boldfit Anti-Slip High Density Yoga Mat with Carrying Strap',
                'brand': 'Boldfit',
                'short_description': '6mm extra thick cushion, eco-friendly TPE material, tear resistant.',
                'description': 'Designed for yoga, pilates and daily floor workouts. Features double-sided non-slip surfaces to prevent injuries and maintain balance during advanced poses.',
                'price': Decimal('1999.00'),
                'discount_price': Decimal('1099.00'),
                'stock': 35,
                'is_available': True,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1592432678016-e910b452f9a2?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.5'),
                'num_reviews': 74,
            },
            {
                'category': categories['Sports & Fitness'],
                'name': 'Kore Heavy Duty Adjustable Dumbbell Set (20kg with Barbell Link)',
                'brand': 'Kore',
                'short_description': 'Convertible dumbbell to barbell combo for home gym workout.',
                'description': 'Includes vinyl weight plates, dumbbell handles, lock collars and connecting steel rod to switch between dumbbell and barbell exercises seamlessly.',
                'price': Decimal('3999.00'),
                'discount_price': Decimal('1999.00'),
                'stock': 4,  # low stock example
                'is_available': True,
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800&auto=format&fit=crop&q=80',
                'rating': Decimal('4.4'),
                'num_reviews': 49,
            },
        ]

        created_products = []
        for p_data in products_data:
            p, _ = Product.objects.update_or_create(
                name=p_data['name'],
                defaults=p_data
            )
            created_products.append(p)

        self.stdout.write(self.style.SUCCESS(f'Created/Updated {len(created_products)} products.'))

        # 5. Create Sample Reviews
        sample_reviews = [
            ("Excellent product quality! Exactly matches what is described. Noise cancellation is unbelievable.", 5),
            ("Very satisfied with the purchase. Fast delivery and safe packaging.", 5),
            ("Good value for money. Minor delays in shipping but product is top notch.", 4),
        ]
        for p in created_products[:4]:
            for comment, rating in sample_reviews:
                ProductReview.objects.get_or_create(
                    product=p,
                    user=customer,
                    defaults={'rating': rating, 'comment': comment}
                )

        # 6. Create Sample Orders for Customer
        if created_products and not Order.objects.filter(user=customer).exists():
            p1 = created_products[0]
            p2 = created_products[4]
            order1 = Order.objects.create(
                user=customer,
                full_name=address.full_name,
                email=customer.email,
                phone=address.phone,
                address_line_1=address.address_line_1,
                address_line_2=address.address_line_2,
                city=address.city,
                state=address.state,
                postal_code=address.postal_code,
                country=address.country,
                subtotal=p1.current_price + p2.current_price,
                shipping_fee=Decimal('0.00'),
                tax=round((p1.current_price + p2.current_price) * Decimal('0.05'), 2),
                discount=p1.savings + p2.savings,
                grand_total=(p1.current_price + p2.current_price) + round((p1.current_price + p2.current_price) * Decimal('0.05'), 2),
                payment_method='ONLINE',
                payment_status='Paid',
                payment_id='TXN-SIM94827164',
                status='Delivered',
                tracking_number='DELHIVERY8923419',
                estimated_delivery=(datetime.now() - timedelta(days=2)).date(),
            )
            OrderItem.objects.create(
                order=order1,
                product=p1,
                product_name=p1.name,
                product_image=p1.display_image,
                price=p1.current_price,
                quantity=1,
                total_price=p1.current_price
            )
            OrderItem.objects.create(
                order=order1,
                product=p2,
                product_name=p2.name,
                product_image=p2.display_image,
                price=p2.current_price,
                quantity=1,
                total_price=p2.current_price
            )

            # Order 2: In-Progress Order
            p3 = created_products[11]
            order2 = Order.objects.create(
                user=customer,
                full_name=address.full_name,
                email=customer.email,
                phone=address.phone,
                address_line_1=address.address_line_1,
                address_line_2=address.address_line_2,
                city=address.city,
                state=address.state,
                postal_code=address.postal_code,
                country=address.country,
                subtotal=p3.current_price,
                shipping_fee=Decimal('49.00'),
                tax=round(p3.current_price * Decimal('0.05'), 2),
                discount=p3.savings,
                grand_total=p3.current_price + Decimal('49.00') + round(p3.current_price * Decimal('0.05'), 2),
                payment_method='COD',
                payment_status='Pending',
                status='Processing',
                tracking_number='BLUEDART782163',
                estimated_delivery=(datetime.now() + timedelta(days=3)).date(),
            )
            OrderItem.objects.create(
                order=order2,
                product=p3,
                product_name=p3.name,
                product_image=p3.display_image,
                price=p3.current_price,
                quantity=1,
                total_price=p3.current_price
            )

            self.stdout.write(self.style.SUCCESS('Created 2 sample orders for customer testing.'))

        self.stdout.write(self.style.SUCCESS('=== DATABASE SEED COMPLETE ==='))
