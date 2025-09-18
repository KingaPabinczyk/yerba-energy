from . import db
from werkzeug.security import generate_password_hash, check_password_hash

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)  
    category = db.Column(db.String(80), nullable=True)
    description = db.Column(db.Text, nullable=True)
    properties = db.Column(db.Text, nullable=True)      
    preparation = db.Column(db.Text, nullable=True)     


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="user")  

    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    street = db.Column(db.String(120), nullable=True)
    house_number = db.Column(db.String(20), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)  
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="nowe")
    created_at = db.Column(db.DateTime, default=db.func.now())

    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    street = db.Column(db.String(120))
    house_number = db.Column(db.String(20))
    postal_code = db.Column(db.String(20))
    city = db.Column(db.String(80))
    email = db.Column(db.String(120))

    delivery_method = db.Column(db.String(20))   
    payment_method = db.Column(db.String(20))   

    user = db.relationship("User", backref="orders")


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False) 

    order = db.relationship("Order", backref="items")
    product = db.relationship("Product")
