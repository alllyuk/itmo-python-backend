from fastapi import FastAPI, HTTPException, status, Query
from typing import Dict, Any, List, Annotated
from pydantic import NonNegativeInt, PositiveInt, NonNegativeFloat
from .models import Item, Cart, CartItem, ItemPost

app = FastAPI(title="Shop API")

items_db: Dict[int, Item] = {}
carts_db: Dict[int, Cart] = {}


@app.post("/item", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemPost):
    new_item_id = len(items_db) + 1
    new_item = Item(id=new_item_id, name=item.name, price=item.price)
    items_db[new_item_id] = new_item
    return Item


@app.get("/item/{id}", status_code=status.HTTP_200_OK)
def get_item(id: int):
    item = items_db.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@app.get("/item")
def get_item_list(offset: Annotated[NonNegativeInt, Query()] = 0,
                  limit: Annotated[PositiveInt, Query()] = 10,
                  min_price: Annotated[NonNegativeFloat, Query()] = None,
                  max_price: Annotated[NonNegativeFloat, Query()] = None,
                  show_deleted: bool = False):

    filtered_items = [item for item in list(items_db.values())[offset:offset + limit]
                      if (show_deleted or not item.deleted) and
                      (min_price is None or item.price >= min_price) and
                      (max_price is None or item.price <= max_price)]
    return filtered_items


@app.put("/item/{id}")
def update_item(id: int, item: ItemPost):
    item_to_edit = items_db.get(id)
    if not item_to_edit or item_to_edit.deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    new_item = Item(id=id, name=item.name, price=item.price)
    items_db[id] = new_item
    return new_item


@app.patch("/item/{id}")
def patch_item(id: int, body: dict[str, Any]):
    item_to_patch = items_db.get(id)
    if not item_to_patch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item_to_patch.deleted:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Item is deleted")

    allowed_fields = {"name", "price"}
    for key, value in body.items():
        if key in allowed_fields:
            setattr(item_to_patch, key, value)
        elif key == 'deleted' and value:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Can't delete item")
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid field in request body")
    return item_to_patch


@app.delete("/item/{id}")
def delete_item(id: int):
    if id not in items_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    item_to_delete = items_db[id]
    item_to_delete.deleted = True
    return item_to_delete


@app.post("/cart", status_code=status.HTTP_201_CREATED)
def create_cart():
    cart_id = len(carts_db) + 1
    carts_db[cart_id] = Cart(id=cart_id)
    return cart_id


@app.get("/cart/{id}")
def get_cart(id: int):
    cart = carts_db.get(id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return cart


@app.get("/cart")
def get_cart_list(offset: Annotated[NonNegativeInt, Query()] = 0,
                  limit: Annotated[PositiveInt, Query()] = 10,
                  min_price: Annotated[NonNegativeFloat, Query()] = None,
                  max_price: Annotated[NonNegativeFloat, Query()] = None,
                  min_quantity: Annotated[NonNegativeInt, Query()] = None,
                  max_quantity: Annotated[NonNegativeInt, Query()] = None):

    filtered_carts = [cart for cart in list(carts_db.values())[offset:offset + limit]
                      if (min_price is None or cart.price >= min_price) and
                      (max_price is None or cart.price <= max_price) and
                      (min_quantity is None or sum(item.quantity for item in cart.items) >= min_quantity) and
                      (max_quantity is None or sum(item.quantity for item in cart.items) <= max_quantity)]
    return filtered_carts


@app.post("/cart/{cart_id}/add/{item_id}")
def add_to_cart(cart_id: int, item_id: int):
    if cart_id not in carts_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    if item_id not in items_db or items_db[item_id].deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found or deleted")

    cart = carts_db[cart_id]
    item = items_db[item_id]

    for cart_item in cart.items:
        if cart_item.id == item.id:
            cart_item.quantity += 1
            break
    else:
        cart.items.append(CartItem(id=item.id, name=item.name, quantity=1))
    cart.price += item.price

    return cart
