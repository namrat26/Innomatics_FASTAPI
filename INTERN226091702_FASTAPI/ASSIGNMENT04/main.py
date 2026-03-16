from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

cart = []
orders = []


class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)


def find_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def calculate_total(product, quantity):
    return product["price"] * quantity


@app.get("/")
def home():
    return {"message": "FastAPI Cart System Running"}


@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):
    product = find_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = calculate_total(product, item["quantity"])
            return {"message": "Cart updated", "cart_item": item}

    cart_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": calculate_total(product, quantity)
    }

    cart.append(cart_item)
    return {"message": "Added to cart", "cart_item": cart_item}


@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed from cart"}

    raise HTTPException(status_code=404, detail="Product not found in cart")


@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty — add items first")

    placed_orders = []
    grand_total = 0

    for item in cart:
        order = {
            "order_id": len(orders) + 1,
            "customer_name": data.customer_name,
            "delivery_address": data.delivery_address,
            "product_id": item["product_id"],
            "product": item["product_name"],
            "quantity": item["quantity"],
            "unit_price": item["unit_price"],
            "total_price": item["subtotal"]
        }
        orders.append(order)
        placed_orders.append(order)
        grand_total += item["subtotal"]

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": placed_orders,
        "grand_total": grand_total
    }


@app.get("/orders")
def get_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }
