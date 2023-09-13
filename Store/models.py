from flask_sqlalchemy import SQLAlchemy;

database = SQLAlchemy ( );


class Product (database.Model):

    __tablename__ = "products";

    id = database.Column (database.Integer, primary_key=True, autoincrement=True);
    name = database.Column (database.String (50), nullable=False);
    price = database.Column (database.Float, nullable=False);

    categories = database.relationship ("Category", secondary="product_categories", back_populates="products");

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