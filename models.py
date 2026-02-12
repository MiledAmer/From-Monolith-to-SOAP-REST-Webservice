import os
from dotenv import load_dotenv
from sqlalchemy import CheckConstraint, Column, Float, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

_engine = None
def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, echo=True)
    return _engine
SessionLocal = sessionmaker(bind=get_engine())
def test_connection():
    try:
        engine = get_engine()
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("Connection successful!")
    except SQLAlchemyError as error:
        print(f"Error connecting to database: {error}")

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    quantity_in_stock = Column(Integer, nullable=False)
    price_per_unit = Column(Float, nullable=False)

    __table_args__ = (
        CheckConstraint("quantity_in_stock >= 0", name="ck_products_quantity_nonneg"),
        CheckConstraint("price_per_unit >= 0", name="ck_products_price_nonneg"),
    )

def create_tables():
    Base.metadata.create_all(get_engine())
    print("Tables created successfully!")

def createProduct (name: str, quantity_in_stock: int, price_per_unit: float): 
    session = SessionLocal() 
    newProduct = Product(name=name, quantity_in_stock=quantity_in_stock, price_per_unit=price_per_unit) 
    session.add(newProduct) 
    session.commit()
    session.refresh(newProduct)
    print(f"the new product is created with id: {newProduct.id}")
    session.close()
    return newProduct

def readProduct (product_id: int): 
    session = SessionLocal() 
    product = session.query(Product).filter(Product.id == product_id).first()
    session.close() 
    return product

def listProducts():
    session = SessionLocal()
    products = session.query(Product).order_by(Product.id).all()
    session.close()
    return products

def updateProduct (product_id: int, name: str = None, quantity_in_stock: int = None, price_per_unit: float = None):
    session = SessionLocal() 
    product = session.query(Product).filter(Product.id == product_id).first()
    if not product:
        session.close()
        return None

    if product: 
        if name is not None: 
            product.name = name
        if quantity_in_stock is not None: 
            product.quantity_in_stock = quantity_in_stock
        if price_per_unit is not None: 
            product.price_per_unit = price_per_unit
        session.commit()
        session.refresh(product)
    session.close()
    return product

def deleteProduct (product_id: int):
    session = SessionLocal() 
    product = session.query(Product).filter(Product.id == product_id).first() 
    if product:
        session.delete(product)
        session.commit()
        session.close()
        return True
    session.close()
    return False

if __name__ == "__main__":
    test_connection()
    create_tables()
    createProduct(name="Product 2", quantity_in_stock=100, price_per_unit=9.99)
    product = readProduct(product_id=2)
    print(f"Product ID: {product.id}, Name: {product.name}, Quantity in Stock: {product.quantity_in_stock}, Price per Unit: {product.price_per_unit}")
    updateProduct(product_id=2, price_per_unit=22.99) 
    product = readProduct(product_id=2)
    print(f"Updated Product ID: {product.id}, Name: {product.name}, Quantity in Stock: {product.quantity_in_stock}, Price per Unit: {product.price_per_unit}")
    deleteProduct(product_id=2) 
    product = readProduct(product_id=2) 
    print(f"Deleted Product: {product}")

