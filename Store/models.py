from flask_sqlalchemy import SQLAlchemy;

database = SQLAlchemy ( );


class Product (database.Model):

    __tablename__ = "products";

    id = database.Column (database.Integer, primary_key=True, autoincrement=True);
    name = database.Column (database.String (50), nullable=False);
    price = database.Column (database.Float, nullable=False);

    categories = database.relationship ("Category", secondary="product_categories", back_populates="products");
    orders = database.relationship ("Order", secondary="order_products", back_populates="products");

    #json serialization
    def to_json (self):
        return {
            "categories": [category.name for category in self.categories],
            "id": self.id,
            "name": self.name,
            "price": self.price
        };


class Category (database.Model):

    __tablename__ = "categories";

    id = database.Column (database.Integer, primary_key=True, autoincrement=True);
    name = database.Column (database.String (50), nullable=False);

    products = database.relationship ("Product", secondary="product_categories", back_populates="categories");

class ProductCategories (database.Model):

    __tablename__ = "product_categories";

    id = database.Column (database.Integer, primary_key=True, autoincrement=True);
    product_id = database.Column (database.Integer, database.ForeignKey ("products.id"), nullable=False);
    category_id = database.Column (database.Integer, database.ForeignKey ("categories.id"), nullable=False);


class Order (database.Model):
    
    __tablename__ = "orders";
    
    id = database.Column (database.Integer, primary_key=True, autoincrement=True);
    customer_email = database.Column (database.String (256), nullable=False);
    price = database.Column (database.Float, nullable=False);
    time = database.Column (database.DateTime, nullable=False);
    status = database.Column (database.String (256), nullable=False);

    products = database.relationship ("Product", secondary="order_products", back_populates="orders");
    

class OrderProducts (database.Model):
    __tablename__ = "order_products";

    id = database.Column (database.Integer, primary_key=True, autoincrement=True);
    order_id = database.Column (database.Integer, database.ForeignKey ("orders.id"), nullable=False);
    product_id = database.Column (database.Integer, database.ForeignKey ("products.id"), nullable=False);
    quantity = database.Column (database.Integer, nullable=False);
