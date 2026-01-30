from slqalchemy import Session
from typing import List
from ..repositories.category_repository import CategoryRepository
from ..repositories.product_repository import ProductRepository
from ..schemas.product import ProductListResponse, ProductCreate, ProductResponse
from fastapi import HTTPException, status

class ProductService:
    def __init__(self, db: Session):
        self.product_repository = ProductRepository(db)
        self.category_repository = CategoryRepository(db)
    
    def get_all_products(self) -> ProductListResponse:
        products = self.product_repository.get_all()
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(products=products_response, total=len(products_response))

    def get_product_by_id(self, product_id: int) -> ProductResponse:
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        return ProductResponse.model_validate(product)

    def get_product_by_category(self, category_id) -> ProductListResponse:
        category = self.category_repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with ID {category_id} not found"
            )
        
        products = self.product_repository.get_by_category(category_id)
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(products=products_response, total=len(products_response))

