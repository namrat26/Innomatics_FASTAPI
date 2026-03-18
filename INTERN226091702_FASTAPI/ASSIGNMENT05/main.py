from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from math import ceil

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

orders = []


class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


def find_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


@app.get("/")
def home():
    return {"message": "FastAPI Day 6 Running"}


@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


# Q1 already built today
@app.get("/products/search")
def search_products(keyword: str):
    results = [p for p in products if keyword.lower() in p["name"].lower()]

    if not results:
        return {"message": f"No products found for: {keyword}"}

    return {
        "keyword": keyword,
        "total_found": len(results),
        "products": results
    }


# Q2 already built today
@app.get("/products/sort")
def sort_products(
    sort_by: str = "price",
    order: str = "asc"
):
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    reverse = True if order == "desc" else False
    sorted_products = sorted(products, key=lambda p: p[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }


# Q3 already built today
@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit
    paginated = products[start:end]
    total_pages = ceil(len(products) / limit)

    return {
        "page": page,
        "limit": limit,
        "total_products": len(products),
        "total_pages": total_pages,
        "products": paginated
    }


# used for Q4 + bonus
@app.post("/orders")
def place_order(order: OrderRequest):
    product = find_product(order.product_id)

    if not product:
        return {"error": "Product not found"}

    total_price = product["price"] * order.quantity

    new_order = {
        "order_id": len(orders) + 1,
        "customer_name": order.customer_name,
        "product_id": order.product_id,
        "product": product["name"],
        "quantity": order.quantity,
        "unit_price": product["price"],
        "total_price": total_price
    }

    orders.append(new_order)
    return {"message": "Order placed successfully", "order": new_order}


@app.get("/orders")
def get_orders():
    return {"orders": orders, "total_orders": len(orders)}


# Q4
@app.get("/orders/search")
def search_orders(customer_name: str):
    results = [
        order for order in orders
        if customer_name.lower() in order["customer_name"].lower()
    ]

    if not results:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results
    }


# Q5 - place above /products/{product_id}
@app.get("/products/sort-by-category")
def sort_by_category():
    sorted_products = sorted(products, key=lambda p: (p["category"], p["price"]))

    return {
        "message": "Products sorted by category, then price",
        "products": sorted_products
    }


# Q6 - place above /products/{product_id}
@app.get("/products/browse")
def browse_products(
    keyword: str = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    result = products

    # filter
    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    # sort
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda p: p[sort_by], reverse=reverse)

    # paginate
    total_found = len(result)
    total_pages = ceil(total_found / limit) if limit > 0 else 1
    start = (page - 1) * limit
    end = start + limit
    paginated = result[start:end]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total_found,
        "total_pages": total_pages,
        "products": paginated
    }


# Bonus
@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit
    paginated = orders[start:end]
    total_pages = ceil(len(orders) / limit) if limit > 0 else 1

    return {
        "page": page,
        "limit": limit,
        "total_orders": len(orders),
        "total_pages": total_pages,
        "orders": paginated
    }


@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = find_product(product_id)

    if not product:
        return {"error": "Product not found"}

    return product
