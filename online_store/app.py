from flask import Flask
from config import Config
from models import db, bcrypt, User, Product, Cart, Wishlist, Order, OrderItem
from routes import register_routes
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)

def seed_database():
    if Product.query.count() > 0:
        print("✅ Database already has products, skipping seed.")
        return
    
    products_data = [
        # Smartphones (8)
        ("iPhone 15 Pro Max", 1299, 1499, "Smartphones", "Apple", "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400", 4.8, 89, True, True),
        ("Samsung Galaxy S24 Ultra", 1199, 1399, "Smartphones", "Samsung", "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400", 4.7, 78, True, True),
        ("Google Pixel 8 Pro", 999, 1099, "Smartphones", "Google", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400", 4.6, 56, False, False),
        ("OnePlus 12", 799, 899, "Smartphones", "OnePlus", "https://images.unsplash.com/photo-1616348436168-de43ad0db179?w=400", 4.5, 45, True, False),
        ("Xiaomi 14 Pro", 899, 999, "Smartphones", "Xiaomi", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400", 4.5, 55, False, True),
        ("Nothing Phone 2", 599, 699, "Smartphones", "Nothing", "https://images.unsplash.com/photo-1687633855041-3a7b4d7a6e2c?w=400", 4.4, 67, False, True),
        ("Sony Xperia 1 V", 1399, 1599, "Smartphones", "Sony", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400", 4.6, 23, False, False),
        ("Motorola Edge 40", 699, 799, "Smartphones", "Motorola", "https://images.unsplash.com/photo-1616348436168-de43ad0db179?w=400", 4.2, 45, False, False),
        
        # Laptops (7)
        ("MacBook Pro M3 Max", 2499, 2799, "Laptops", "Apple", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400", 4.9, 120, True, True),
        ("Dell XPS 16", 1899, 2199, "Laptops", "Dell", "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=400", 4.7, 67, True, False),
        ("HP Spectre x360", 1499, 1699, "Laptops", "HP", "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400", 4.6, 45, False, True),
        ("ASUS ROG Zephyrus", 1599, 1899, "Laptops", "ASUS", "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400", 4.8, 89, True, False),
        ("Lenovo ThinkPad X1", 1799, 2099, "Laptops", "Lenovo", "https://images.unsplash.com/photo-1629131726692-1accd0c53ce0?w=400", 4.7, 56, True, False),
        ("Microsoft Surface Laptop 5", 1299, 1499, "Laptops", "Microsoft", "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400", 4.5, 78, False, False),
        ("Acer Swift Edge", 1099, 1299, "Laptops", "Acer", "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400", 4.4, 34, False, True),
        
        # Audio Products (6)
        ("Sony WH-1000XM5", 399, 499, "Audio", "Sony", "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400", 4.9, 234, True, True),
        ("Apple AirPods Pro 2", 249, 299, "Audio", "Apple", "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400", 4.8, 189, True, False),
        ("Bose QuietComfort Ultra", 429, 499, "Audio", "Bose", "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400", 4.7, 89, False, True),
        ("Samsung Galaxy Buds2 Pro", 199, 249, "Audio", "Samsung", "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400", 4.6, 156, False, False),
        ("JBL Tour Pro 2", 249, 299, "Audio", "JBL", "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400", 4.5, 67, False, False),
        ("Sennheiser Momentum 4", 349, 399, "Audio", "Sennheiser", "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400", 4.7, 45, True, False),
        
        # Wearables (5)
        ("Apple Watch Ultra 2", 799, 899, "Wearables", "Apple", "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=400", 4.9, 89, True, True),
        ("Samsung Galaxy Watch 6", 349, 399, "Wearables", "Samsung", "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400", 4.6, 156, False, False),
        ("Garmin Fenix 7", 699, 799, "Wearables", "Garmin", "https://images.unsplash.com/photo-1626908013351-800ddd734b8a?w=400", 4.7, 78, True, False),
        ("Google Pixel Watch 2", 349, 399, "Wearables", "Google", "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400", 4.5, 89, False, True),
        ("Fitbit Sense 2", 299, 349, "Wearables", "Fitbit", "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400", 4.4, 67, False, False),
        
        # Accessories (4)
        ("Logitech MX Master 3S", 99, 129, "Accessories", "Logitech", "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400", 4.8, 234, True, False),
        ("Keychron Q1 Pro", 199, 249, "Accessories", "Keychron", "https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?w=400", 4.7, 89, False, True),
        ("Samsung T7 Shield 2TB", 159, 199, "Accessories", "Samsung", "https://images.unsplash.com/photo-1628890923662-2cb23c2e0cfe?w=400", 4.6, 145, False, False),
        ("Anker 737 Charger", 109, 129, "Accessories", "Anker", "https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=400", 4.5, 234, False, False),
    ]
    
    for name, price, orig_price, cat, brand, img, rating, reviews, featured, is_new in products_data:
        discount = int(((orig_price - price) / orig_price) * 100) if orig_price > price else 0
        product = Product(
            name=name, 
            price=price, 
            original_price=orig_price, 
            category=cat,
            brand=brand, 
            image=img, 
            rating=rating, 
            reviews_count=reviews,
            discount=discount, 
            is_featured=featured, 
            is_new=is_new, 
            stock=100,
            description=f"Experience the best of {brand} technology with the {name}. Premium quality with cutting-edge features."
        )
        db.session.add(product)
    
    db.session.commit()
    print("✅ 30 products with working Unsplash images added!")

def create_admin():
    if not User.query.filter_by(email='admin@techhub.com').first():
        hashed = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(email='admin@techhub.com', username='Administrator', password=hashed, role='admin')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created!")

with app.app_context():
    db.create_all()
    seed_database()
    create_admin()
    print("\n" + "="*60)
    print("🛍️  PREMIUM TECH HUB STORE")
    print("="*60)
    print("📍 Website: http://localhost:5000")
    print("👑 Admin: admin@techhub.com / admin123")
    print("📦 30 Products with Working Images!")
    print("="*60 + "\n")

register_routes(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)