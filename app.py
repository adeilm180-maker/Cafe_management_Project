
from flask import Flask, render_template, request, redirect, url_for, session, flash
from decimal import Decimal, ROUND_HALF_UP

app = Flask(__name__)
app.secret_key = "replace_with_a_random_secret_key"  # change for deployment

# 15 sample products (id, name, price, image filename, description)
PRODUCTS = [
    {"id": 1, "name": "Cold Coffee", "price": Decimal('3.00'), "image": "cold_coffee.jpg", "desc": "Chilled coffee."},
    {"id": 2, "name": "Cappuccino", "price": Decimal('5.00'), "image": "choclatecoffee.jpg", "desc": "Classic cappuccino."},
    {"id": 3, "name": "Chocolate Coffee", "price": Decimal('4.00'), "image": "chocolate_coffee.jpg", "desc": "Rich chocolate."},
    {"id": 4, "name": "Green Tea", "price": Decimal('2.00'), "image": "green_tea.jpg", "desc": "Healthy green tea."},
    {"id": 5, "name": "Mineral Water", "price": Decimal('0.50'), "image": "mineral_water.jpg", "desc": "Bottled water."},
    {"id": 6, "name": "Strawberry Cake", "price": Decimal('10.00'), "image": "strawberry_cake.jpg", "desc": "Fresh strawberry."},
    {"id": 7, "name": "Chocolate Cake", "price": Decimal('8.00'), "image": "chocolate_cake.jpg", "desc": "Decadent chocolate."},
    {"id": 8, "name": "Fruit Cake", "price": Decimal('12.00'), "image": "fruit_cake.jpg", "desc": "Mixed fruits."},
    {"id": 9, "name": "Rainbow Cake", "price": Decimal('15.00'), "image": "rainbow_cake.jpg", "desc": "Colorful treat."},
    {"id":10, "name": "Coca Cola", "price": Decimal('1.50'), "image": "coca_cola.jpg", "desc": "Cold cola."},
    {"id":11, "name": "Vegetarian Pizza", "price": Decimal('7.50'), "image": "veg_pizza.jpg", "desc": "Veg toppings."},
    {"id":12, "name": "Burger", "price": Decimal('2.50'), "image": "burger.jpg", "desc": "Juicy burger."},
    {"id":13, "name": "Noodles", "price": Decimal('5.50'), "image": "noodles.jpg", "desc": "Hot noodles."},
    {"id":14, "name": "7 UP", "price": Decimal('1.60'), "image": "7up.jpg", "desc": "Lemon-lime drink."},
    {"id":15, "name": "Orange Juice", "price": Decimal('3.00'), "image": "orange_juice.jpg", "desc": "Freshly squeezed."},
]

def get_product(pid):
    for p in PRODUCTS:
        if p['id'] == pid:
            return p
    
    return None

def to_two_decimals(d):
    return d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

@app.route('/')
def index():
    return render_template('index.html', products=PRODUCTS)

@app.route('/add', methods=['POST'])
def add_to_cart():
    pid = int(request.form.get('product_id'))
    qty = int(request.form.get('quantity', 0))
    if qty <= 0:
        flash("Quantity should be at least 1", "warning")
        return redirect(url_for('index'))

    product = get_product(pid)
    if not product:
        flash("Product not found", "danger")
        return redirect(url_for('index'))

    cart = session.get('cart', {})
    if str(pid) in cart:
        cart[str(pid)]['quantity'] += qty
    else:
        cart[str(pid)] = {
            'id': pid,
            'name': product['name'],
            'price': str(product['price']),
            'quantity': qty,
            'image': product['image']
        }
    session['cart'] = cart
    flash(f"Added {qty} × {product['name']} to cart", "success")
    return redirect(url_for('index'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    items = []
    subtotal = Decimal('0.00')

    for v in cart.values():
        price = Decimal(v['price'])
        qty = int(v['quantity'])
        item_total = price * qty
        items.append({
            **v,
            'price': to_two_decimals(price),
            'total': to_two_decimals(item_total)
        })
        subtotal += item_total

    total = to_two_decimals(subtotal)

    return render_template('cart.html', items=items,
                           subtotal=to_two_decimals(subtotal),
                           total=total)

@app.route('/update', methods=['POST'])
def update_cart():
    pid = request.form.get('product_id')
    action = request.form.get('action')
    cart = session.get('cart', {})
    if pid and pid in cart:
        if action == 'remove':
            cart.pop(pid, None)
        else:
            qty = int(request.form.get('quantity', 0))
            if qty <= 0:
                cart.pop(pid, None)
            else:
                cart[pid]['quantity'] = qty
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash("Cart is empty", "warning")
        return redirect(url_for('index'))

    items = []
    subtotal = Decimal('0.00')

    for v in cart.values():
        price = Decimal(v['price'])
        qty = int(v['quantity'])
        item_total = price * qty
        items.append({
            **v,
            'price': to_two_decimals(price),
            'total': to_two_decimals(item_total)
        })
        subtotal += item_total

    total = to_two_decimals(subtotal)

    session.pop('cart', None)

    return render_template('receipt.html', items=items,
                           subtotal=to_two_decimals(subtotal),
                           total=total)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
