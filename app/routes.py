from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from .models import Product, User, db, Order, OrderItem
from .forms import ProductForm, LoginForm, RegisterForm, GuestCheckoutForm
import os
from werkzeug.utils import secure_filename
from flask import current_app

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    category = request.args.get("category", "all") 
    
    if category == "all":
        products = Product.query.all()
    else:
        products = Product.query.filter_by(category=category).all()

    cart = session.get("cart", {})
    return render_template(
        "index.html",
        products = products,
        cart = cart,
        selected_category = category
    )

@bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)



@bp.route("/add", methods=["GET", "POST"])
def add_product():
    if session.get("role") != "admin":
        flash("Nie masz uprawnień do dodawania produktów!", "danger")
        return redirect(url_for("main.index"))

    form = ProductForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            images_dir = os.path.join(current_app.root_path, "static", "images")
            os.makedirs(images_dir, exist_ok=True)
            upload_path = os.path.join(images_dir, filename)
            form.image.data.save(upload_path)
            image_url = f"/static/images/{filename}"
        else:
            image_url = None


        new_product = Product(
            name=form.name.data,
            price=form.price.data,
            image_url=image_url,
            category=form.category.data,
            description=form.description.data,
            properties=form.properties.data,
            preparation=form.preparation.data,
        )

        db.session.add(new_product)
        db.session.commit()
        flash("Produkt dodany!", "success")
        return redirect(url_for("main.index"))

    return render_template("add_product.html", form=form)


@bp.route("/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if "user_id" not in session or session.get("role") != "admin":
        flash("Brak uprawnień!", "danger")
        return redirect(url_for("main.index"))

    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.category = form.category.data
        product.description = form.description.data
        product.properties = form.properties.data
        product.preparation = form.preparation.data

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            images_dir = os.path.join(current_app.root_path, "static", "images")
            os.makedirs(images_dir, exist_ok=True)
            upload_path = os.path.join(images_dir, filename)
            form.image.data.save(upload_path)
            product.image_url = f"/static/images/{filename}"

        db.session.commit()
        flash("Produkt zaktualizowany!", "success")
        return redirect(url_for("main.product_detail", product_id=product.id))

    return render_template("add_product.html", form=form, edit=True)

@bp.route("/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    if "user_id" not in session or session.get("role") != "admin":
        flash("Brak uprawnień!", "danger")
        return redirect(url_for("main.index"))

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Produkt usunięty!", "info")
    return redirect(url_for("main.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Użytkownik o takim loginie już istnieje!", "danger")
            return redirect(url_for("main.register"))

        if User.query.filter_by(email=form.email.data).first():
            flash("Adres e-mail jest już używany!", "danger")
            return redirect(url_for("main.register"))

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            street=form.street.data,
            house_number=form.house_number.data,
            postal_code=form.postal_code.data,
            city=form.city.data,
        )
        new_user.set_password(form.password.data)

        if form.username.data == "admin" and form.password.data == "admin":
            new_user.role = "admin"

        db.session.add(new_user)
        db.session.commit()
        flash("Rejestracja udana! Możesz się zalogować.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            flash(f"Zalogowano jako {user.username}", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Błędny login lub hasło", "danger")
    return render_template("login.html", form=form)


@bp.route("/logout")
def logout():
    session.clear()
    flash("Wylogowano", "info")
    return redirect(url_for("main.index"))


@bp.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    cart = session.get("cart", {})
    pid = str(product_id)  
    cart[pid] = cart.get(pid, 0) + 1
    session["cart"] = cart
    return redirect(request.referrer or url_for("main.index"))


@bp.route("/update_cart/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    action = request.form.get("action")
    cart = session.get("cart", {})
    pid = str(product_id) 
    if pid in cart:
        if action == "increase":
            cart[pid] += 1
        elif action == "decrease":
            cart[pid] -= 1
            if cart[pid] <= 0:
                del cart[pid]
    session["cart"] = cart
    return redirect(request.referrer or url_for("main.index"))


@bp.route("/cart")
def cart():
    cart = session.get("cart", {})
    if not cart:
        flash("Koszyk jest pusty.", "info")
        return render_template("cart.html", products=[], total=0)

    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.query.filter(Product.id.in_(product_ids)).all()

    items = []
    total = 0
    for product in products:
        qty = cart.get(str(product.id), 0)
        subtotal = qty * product.price
        total += subtotal
        items.append({
            "product": product,
            "qty": qty,
            "subtotal": subtotal
        })

    return render_template("cart.html", products=items, total=total)


@bp.route("/remove_from_cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        session["cart"] = cart
        flash("Produkt usunięty z koszyka.", "info")
    return redirect(request.referrer or url_for("main.cart"))


@bp.route("/clear_cart", methods=["POST"])
def clear_cart():
    session["cart"] = {}
    flash("Koszyk został opróżniony.", "info")
    return redirect(url_for("main.cart"))

@bp.route("/place_order", methods=["POST"])
def place_order():
    if "user_id" not in session:
        flash("Musisz być zalogowany, aby złożyć zamówienie.", "danger")
        return redirect(url_for("main.login"))

    cart = session.get("cart", {})
    if not cart:
        flash("Koszyk jest pusty.", "warning")
        return redirect(url_for("main.cart"))

    user_id = session["user_id"]

    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.query.filter(Product.id.in_(product_ids)).all()

    total = 0
    order = Order(user_id=user_id, total=0)
    db.session.add(order)
    db.session.flush()  

    for product in products:
        qty = cart[str(product.id)]
        subtotal = qty * product.price
        total += subtotal
        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=qty,
            price=product.price
        )
        db.session.add(item)

    order.total = total
    db.session.commit()

    session["cart"] = {}

    flash("Zamówienie zostało złożone!", "success")
    return redirect(url_for("main.my_orders"))

@bp.route("/orders")
def orders():
    if "user_id" not in session:
        flash("Zaloguj się, aby zobaczyć zamówienia.", "danger")
        return redirect(url_for("main.login"))

    if session.get("role") == "admin":
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(user_id=session["user_id"]).order_by(Order.created_at.desc()).all()

    return render_template("orders.html", orders=orders)

@bp.route("/users")
def users():
    if "user_id" not in session:
        flash("Zaloguj się, aby zobaczyć użytkowników.", "danger")
        return redirect(url_for("main.login"))

    if session.get("role") != "admin":
        flash("Nie masz uprawnień do podglądu użytkowników.", "danger")
        return redirect(url_for("main.index"))

    users = User.query.order_by(User.id.asc()).all()
    return render_template("users.html", users=users)

@bp.route("/users/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if "user_id" not in session or session.get("role") != "admin":
        flash("Brak uprawnień!", "danger")
        return redirect(url_for("main.index"))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Użytkownik został usunięty.", "info")
    return redirect(url_for("main.users"))


@bp.route("/checkout/delivery", methods=["GET", "POST"])
def checkout_delivery():
    
    guest_form = GuestCheckoutForm()

    if not session.get("user_id"):
        if guest_form.validate_on_submit():
            
            address = {k: v for k, v in guest_form.data.items() if k not in ("csrf_token", "submit")}
            session["checkout_address"] = address
            session["checkout_delivery"] = request.form.get("delivery_method")
            session["checkout_payment"] = request.form.get("payment_method")
            return redirect(url_for("main.checkout_summary"))

    else:
        if request.method == "POST":
            session["checkout_delivery"] = request.form.get("delivery_method")
            session["checkout_payment"] = request.form.get("payment_method")
            user = User.query.get(session["user_id"])
            session["checkout_address"] = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "street": user.street,
                "house_number": user.house_number,
                "postal_code": user.postal_code,
                "city": user.city,
                "email": user.email
            }
            return redirect(url_for("main.checkout_summary"))

    return render_template("checkout/delivery.html", guest_form=guest_form)


@bp.route("/checkout/summary", methods=["GET", "POST"])
def checkout_summary():
    cart = session.get("cart", {})
    if not cart:
        flash("Koszyk jest pusty.", "warning")
        return redirect(url_for("main.cart"))

    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.query.filter(Product.id.in_(product_ids)).all()

    items = []
    total = 0
    for p in products:
        qty = cart[str(p.id)]
        subtotal = qty * p.price
        items.append({"product": p, "qty": qty, "subtotal": subtotal})
        total += subtotal

    if session.get("checkout_delivery") == "kurier":
        total += 14

    if request.method == "POST":
        blik_code = request.form.get("blik_code")
        order = Order(
            user_id=session.get("user_id"),
            total=total,
            delivery_method=session.get("checkout_delivery"),
            payment_method=session.get("checkout_payment"),
            status="Zapłacone - w realizacji" if blik_code else (
                "w realizacji" if session.get("checkout_payment") == "odbior" else "oczekuje na płatność"
            ),
        )

        address = session.get("checkout_address", {})
        order.first_name = address.get("first_name")
        order.last_name = address.get("last_name")
        order.email = address.get("email")
        order.street = address.get("street")
        order.house_number = address.get("house_number")
        order.postal_code = address.get("postal_code")
        order.city = address.get("city")

        db.session.add(order)
        db.session.flush()

        for item in items:
            db.session.add(OrderItem(
                order_id=order.id,
                product_id=item["product"].id,
                quantity=item["qty"],
                price=item["product"].price
            ))

        db.session.commit()
        session["cart"] = {}
        session.pop("checkout_address", None)
        session.pop("checkout_delivery", None)
        session.pop("checkout_payment", None)

        return redirect(url_for("main.order_detail", order_id=order.id))

    return render_template("checkout/summary.html", items=items, total=total)


@bp.route("/order/<int:order_id>")
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("checkout/confirm.html", order=order)
