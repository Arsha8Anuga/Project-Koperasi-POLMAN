# app/services/hpp.py
def moving_average(old_stock: int, old_cost: int, qty: int, price: int) -> int:
    total_qty = old_stock + qty
    if total_qty == 0:
        return price
    num = old_stock * old_cost + qty * price
    return (2 * num + total_qty) // (2 * total_qty)   # pembulatan half-up, hasil tetap integer