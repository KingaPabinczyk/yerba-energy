from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from .models import Product, User, db
from .forms import ProductForm, LoginForm, RegisterForm
import os
from werkzeug.utils import secure_filename
from flask import current_app


bp = Blueprint("main", __name__)

# Strona główna – tylko produkty
@bp.route("/")
def index():
    category = request.args.get("category", "all")  # domyślnie "all"

    if category == "all":
        products = Product.query.all()
    else:
        products = Product.query.filter_by(category=category).all()

    cart = session.get("cart", {})
    return render_template(
        "index.html",
        products=products,
        cart=cart,
        selected_category=category
    )




@bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)


# Dodawanie produktu – tylko admin

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



# Edycja produktu
@bp.route("/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if "user_id" not in session or session.get("role") != "admin":
        flash("Brak uprawnień!", "danger")
        return redirect(url_for("main.index"))

    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        # update pól tekstowych
        product.name = form.name.data
        product.price = form.price.data
        product.category = form.category.data
        product.description = form.description.data
        product.properties = form.properties.data
        product.preparation = form.preparation.data

        # obsługa zdjęcia (jeśli podano nowe)
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

# Usunięcie produktu
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


# Rejestracja
@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Użytkownik już istnieje!", "danger")
            return redirect(url_for("main.register"))

        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)

        # automatyczne ustawienie admina jeśli login to admin/admin
        if form.username.data == "admin" and form.password.data == "admin":
            new_user.role = "admin"

        db.session.add(new_user)
        db.session.commit()
        flash("Rejestracja udana! Możesz się zalogować.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)


# Logowanie
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


# Wylogowanie
@bp.route("/logout")
def logout():
    session.clear()
    flash("Wylogowano", "info")
    return redirect(url_for("main.index"))


# Dodanie produktu do koszyka
@bp.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    cart = session.get("cart", {})
    pid = str(product_id)  # zawsze string
    cart[pid] = cart.get(pid, 0) + 1
    session["cart"] = cart
    return redirect(request.referrer or url_for("main.index"))


# Zmiana ilości produktu w koszyku
@bp.route("/update_cart/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    action = request.form.get("action")
    cart = session.get("cart", {})
    pid = str(product_id)  # zawsze string
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

    # Pobieramy produkty z bazy
    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.query.filter(Product.id.in_(product_ids)).all()

    # Tworzymy listę produktów z ilością i sumą
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


# Usunięcie produktu z koszyka
@bp.route("/remove_from_cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        session["cart"] = cart
        flash("Produkt usunięty z koszyka.", "info")
    return redirect(request.referrer or url_for("main.cart"))


# Opróżnienie całego koszyka
@bp.route("/clear_cart", methods=["POST"])
def clear_cart():
    session["cart"] = {}
    flash("Koszyk został opróżniony.", "info")
    return redirect(url_for("main.cart"))
