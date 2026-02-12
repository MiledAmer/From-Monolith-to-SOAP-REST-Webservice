import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, PositiveFloat, PositiveInt
from typing import Optional, List
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from models import get_engine, Product as ProductModel, create_tables


class ProductBase(BaseModel):
    name: str
    quantity_in_stock: PositiveInt 
    price_per_unit: PositiveFloat    

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    quantity_in_stock: Optional[PositiveInt] = None
    price_per_unit: Optional[PositiveFloat] = None

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title="Inventory REST API",
    description="Lab 1 Part 3: RESTful Service with FastAPI",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    create_tables()

@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        new_product = ProductModel(
            name=product.name,
            quantity_in_stock=product.quantity_in_stock,
            price_per_unit=product.price_per_unit
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")

@app.get("/products", response_model=List[ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        products = db.query(ProductModel).offset(skip).limit(limit).all()
        return products
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error retrieving product list")

@app.get("/products/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    try:
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error fetching product")

@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    try:
        db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        update_data = product_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        
        db.commit()
        db.refresh(db_product)
        return db_product
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update product")

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    try:
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        db.delete(product)
        db.commit()
        return None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete product")
    
if __name__ == "__main__":
    uvicorn.run("rest:app", host="127.0.0.1", port=8000, reload=True)