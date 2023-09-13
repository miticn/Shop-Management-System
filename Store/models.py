from flask_sqlalchemy import SQLAlchemy;

database = SQLAlchemy ( );


class Product (database.Model):

    __tablename__ = "products";

    id = database.Column (database.Integer, primary_key=True, autoincrement=True);
    name = database.Column (database.String (50), nullable=False);
    price = database.Column (database.Float, nullable=False);


class Category (database.Model):

    __tablename__ = "categories";

    id = database.Column (database.Integer, primary_key=True, autoincrement=True);
    name = database.Column (database.String (50), nullable=False);

class ProductCategories (database.Model):

    __tablename__ = "product_categories";

    id = database.Column (database.Integer, primary_key=True, autoincrement=True);
    product_id = database.Column (database.Integer, database.ForeignKey ("products.id"), nullable=False);
    category_id = database.Column (database.Integer, database.ForeignKey ("categories.id"), nullable=False);