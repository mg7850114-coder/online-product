from flask import render_template, request, redirect, url_for, session, flash
from models import db, User, Product, Cart, Wishlist, Order, OrderItem, bcrypt
import random
import string

def generate_order_number():
    return 'ORD-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

def register_routes(app):
    
    @app.route('/')
    def index():
        featured = Product.query.filter_by(is_featured=True).limit(8).all()
        new_arrivals = Product.query.filter_by(is_new=True).limit(8).all()
        best_selling = Product.query.order_by(Product.reviews_count.desc()).limit(8).all()
        categories = db.session.query(Product.category).distinct().all()
        return render_template('index_new.html', featured=featured, new_arrivals=new_arrivals, 
                              best_selling=best_selling, categories=[c[0] for c in categories if c[0]])

    @app.route('/shop')
    def shop():
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        sort = request.args.get('sort', 'newest')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        query = Product.query
        if category:
            query = query.filter_by(category=category)
        if search:
            query = query.filter(Product.name.contains(search) | Product.brand.contains(search))
        if min_price:
            query = query.filter(Product.price >= min_price)
        if max_price:
            query = query.filter(Product.price <= max_price)
        
        if sort == 'price_asc':
            query = query.order_by(Product.price.asc())
        elif sort == 'price_desc':
            query = query.order_by(Product.price.desc())
        elif sort == 'rating':
            query = query.order_by(Product.rating.desc())
        else:
            query = query.order_by(Product.created_at.desc())
        
        products = query.all()
        categories = db.session.query(Product.category).distinct().all()
        return render_template('shop.html', products=products, categories=[c[0] for c in categories if c[0]],
                              category=category, search=search, sort=sort, min_price=min_price, max_price=max_price)

    @app.route('/product/<int:id>')
    def product_detail(id):
        product = Product.query.get_or_404(id)
        related = Product.query.filter_by(category=product.category).limit(4).all()
        in_wishlist = False
        wishlist_item = None
        if 'user_id' in session:
            wishlist_item = Wishlist.query.filter_by(user_id=session['user_id'], product_id=id).first()
            in_wishlist = wishlist_item is not None
        return render_template('product_detail_new.html', product=product, related=related, 
                             in_wishlist=in_wishlist, wishlist_item=wishlist_item)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            if User.query.filter_by(email=request.form['email']).first():
                flash('Email already registered!', 'danger')
                return redirect(url_for('register'))
            
            hashed = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            user = User(
                email=request.form['email'],
                username=request.form['username'],
                password=hashed
            )
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        return render_template('register_new.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            user = User.query.filter_by(email=request.form['email']).first()
            if user and bcrypt.check_password_hash(user.password, request.form['password']):
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                session['email'] = user.email
                flash(f'Welcome back, {user.username}!', 'success')
                return redirect(url_for('index'))
            flash('Invalid credentials!', 'danger')
        return render_template('login_new.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Logged out successfully!', 'info')
        return redirect(url_for('index'))

    @app.route('/add_to_cart/<int:id>')
    def add_to_cart(id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        cart_item = Cart.query.filter_by(user_id=session['user_id'], product_id=id).first()
        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = Cart(user_id=session['user_id'], product_id=id)
            db.session.add(cart_item)
        
        db.session.commit()
        flash('Product added to cart!', 'success')
        return redirect(request.referrer or url_for('shop'))

    @app.route('/cart')
    def cart():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        items = Cart.query.filter_by(user_id=session['user_id']).all()
        subtotal = sum(item.product.price * item.quantity for item in items)
        shipping = 0 if subtotal > 500 else 25
        tax = subtotal * 0.1
        total = subtotal + shipping + tax
        return render_template('cart_new.html', items=items, subtotal=subtotal, shipping=shipping, tax=tax, total=total)

    @app.route('/update_cart/<int:id>/<int:quantity>')
    def update_cart(id, quantity):
        cart_item = Cart.query.get(id)
        if cart_item and cart_item.user_id == session.get('user_id'):
            if quantity <= 0:
                db.session.delete(cart_item)
            else:
                cart_item.quantity = quantity
            db.session.commit()
        return redirect(url_for('cart'))

    @app.route('/remove_from_cart/<int:id>')
    def remove_from_cart(id):
        cart_item = Cart.query.get(id)
        if cart_item and cart_item.user_id == session.get('user_id'):
            db.session.delete(cart_item)
            db.session.commit()
            flash('Item removed from cart', 'info')
        return redirect(url_for('cart'))

    @app.route('/wishlist')
    def wishlist():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        items = Wishlist.query.filter_by(user_id=session['user_id']).all()
        return render_template('wishlist_new.html', items=items)

    @app.route('/add_to_wishlist/<int:id>')
    def add_to_wishlist(id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if not Wishlist.query.filter_by(user_id=session['user_id'], product_id=id).first():
            wish = Wishlist(user_id=session['user_id'], product_id=id)
            db.session.add(wish)
            db.session.commit()
            flash('Added to wishlist!', 'success')
        return redirect(request.referrer)

    @app.route('/remove_from_wishlist/<int:id>')
    def remove_from_wishlist(id):
        wish = Wishlist.query.get(id)
        if wish and wish.user_id == session.get('user_id'):
            db.session.delete(wish)
            db.session.commit()
            flash('Removed from wishlist', 'info')
        return redirect(url_for('wishlist'))

    @app.route('/checkout', methods=['GET', 'POST'])
    def checkout():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        items = Cart.query.filter_by(user_id=session['user_id']).all()
        if not items:
            return redirect(url_for('cart'))
        
        if request.method == 'POST':
            subtotal = sum(item.product.price * item.quantity for item in items)
            shipping = 0 if subtotal > 500 else 25
            tax = subtotal * 0.1
            total = subtotal + shipping + tax
            order_num = generate_order_number()
            
            order = Order(
                order_number=order_num,
                user_id=session['user_id'],
                total=total,
                payment_method=request.form.get('payment', 'Credit Card'),
                shipping_address=request.form.get('address', '123 Tech Street, CA'),
                shipping_cost=shipping
            )
            db.session.add(order)
            db.session.commit()
            
            for item in items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.product.price
                )
                db.session.add(order_item)
                db.session.delete(item)
            
            db.session.commit()
            flash(f'Order placed successfully! Order #{order_num}', 'success')
            return redirect(url_for('order_detail', id=order.id))
        
        subtotal = sum(item.product.price * item.quantity for item in items)
        shipping = 0 if subtotal > 500 else 25
        tax = subtotal * 0.1
        total = subtotal + shipping + tax
        return render_template('checkout_new.html', items=items, subtotal=subtotal, shipping=shipping, tax=tax, total=total)

    @app.route('/orders')
    def orders():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user_orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
        return render_template('orders_new.html', orders=user_orders)

    @app.route('/order/<int:id>')
    def order_detail(id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        order = Order.query.get_or_404(id)
        if order.user_id != session['user_id'] and session.get('role') != 'admin':
            flash('You do not have permission to view this order', 'danger')
            return redirect(url_for('orders'))
        
        return render_template('order_detail.html', order=order)

    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if request.method == 'POST':
            user.username = request.form['username']
            user.phone = request.form.get('phone', '')
            user.address = request.form.get('address', '')
            if request.form.get('password'):
                user.password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            db.session.commit()
            session['username'] = user.username
            flash('Profile updated successfully!', 'success')
        return render_template('profile_new.html', user=user)

    @app.route('/admin')
    def admin():
        if session.get('role') != 'admin':
            flash('Admin access required!', 'danger')
            return redirect(url_for('index'))
        
        products = Product.query.all()
        users = User.query.all()
        orders = Order.query.all()
        return render_template('admin_new.html', products=products, users=users, orders=orders)