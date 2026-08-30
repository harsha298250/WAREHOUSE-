from sqlalchemy import select, func
from sqlalchemy.orm import Session
from backend.models import (
    Inventory, InventoryMovement, InventoryReservation,
    WarehouseLocation, Order, Task, Item, Warehouse, FinancialTransaction
)

def run_database_reconciliation(db: Session) -> dict:
    """
    Perform a complete operational data reconciliation check:
    1. Negative inventory levels.
    2. Inventory vs Movement quantity mismatch.
    3. Movement record with invalid/negative quantity.
    4. Movement before/after quantity mismatch.
    5. Reservation mismatch (active reservations sum != inv.reserved).
    6. Invalid location reference.
    7. Movement referencing nonexistent order/task.
    8. Duplicate movements for the same operation.
    """
    discrepancies = []

    # 1. Check Negative Inventory
    neg_inventories = db.query(Inventory).filter(
        (Inventory.on_hand < 0) | (Inventory.reserved < 0) | (Inventory.available < 0)
    ).all()
    for inv in neg_inventories:
        discrepancies.append({
            "type": "NEGATIVE_INVENTORY",
            "details": f"Inventory row {inv.id} has negative values (on_hand={inv.on_hand}, reserved={inv.reserved}, available={inv.available})",
            "warehouse_id": inv.warehouse_id,
            "item_id": inv.item_id,
            "location_id": inv.location_id
        })

    # 2 & 3 & 4. Check Movements
    movements = db.query(InventoryMovement).all()
    seen_refs = {}

    for m in movements:
        # Check invalid quantity
        if m.quantity <= 0:
            discrepancies.append({
                "type": "IMPOSSIBLE_MOVEMENT_QUANTITY",
                "details": f"Movement {m.id} has invalid non-positive quantity: {m.quantity}",
                "movement_id": m.id
            })

        # Check before/after mismatch
        expected_after = m.quantity_after
        if m.movement_type in ("RECEIVING", "PUTAWAY", "RESERVE"):
            expected_after = m.quantity_before + m.quantity
        elif m.movement_type in ("PICK", "RESERVE_RELEASE"):
            expected_after = m.quantity_before - m.quantity
        elif m.movement_type == "ADJUSTMENT":
            # For manual adjustments, quantity can be positive or negative
            pass # Pydantic/logic validates before/after on save

        if expected_after != m.quantity_after and m.movement_type != "ADJUSTMENT":
            discrepancies.append({
                "type": "BEFORE_AFTER_MISMATCH",
                "details": f"Movement {m.id} before/after mismatch: {m.quantity_before} + {m.quantity} != {m.quantity_after} (type: {m.movement_type})",
                "movement_id": m.id
            })

        # Check duplicate references
        if m.reference_id and m.reference_type:
            ref_key = (m.reference_type, m.reference_id, m.movement_type)
            if ref_key in seen_refs:
                discrepancies.append({
                    "type": "DUPLICATE_MOVEMENT_REFERENCE",
                    "details": f"Duplicate movement reference found: {m.reference_type}='{m.reference_id}' (movement types: {m.id} and {seen_refs[ref_key]})",
                    "movement_id": m.id
                })
            seen_refs[ref_key] = m.id

        # Check nonexistent locations
        if m.source_location_id:
            loc_exists = db.query(WarehouseLocation).filter(WarehouseLocation.id == m.source_location_id).first()
            if not loc_exists:
                discrepancies.append({
                    "type": "INVALID_LOCATION_REFERENCE",
                    "details": f"Movement {m.id} references nonexistent source location: '{m.source_location_id}'",
                    "movement_id": m.id
                })
        if m.destination_location_id:
            loc_exists = db.query(WarehouseLocation).filter(WarehouseLocation.id == m.destination_location_id).first()
            if not loc_exists:
                discrepancies.append({
                    "type": "INVALID_LOCATION_REFERENCE",
                    "details": f"Movement {m.id} references nonexistent destination location: '{m.destination_location_id}'",
                    "movement_id": m.id
                })

        # Check nonexistent order/task
        if m.order_id:
            order_exists = db.query(Order).filter(Order.id == m.order_id).first()
            if not order_exists:
                discrepancies.append({
                    "type": "NONEXISTENT_ORDER_REFERENCE",
                    "details": f"Movement {m.id} references nonexistent order: '{m.order_id}'",
                    "movement_id": m.id
                })
        if m.task_id:
            task_exists = db.query(Task).filter(Task.id == m.task_id).first()
            if not task_exists:
                discrepancies.append({
                    "type": "NONEXISTENT_TASK_REFERENCE",
                    "details": f"Movement {m.id} references nonexistent task: {m.task_id}",
                    "movement_id": m.id
                })

    # 5. Check Reservation Mismatch
    # Group active reservations by warehouse, item, location
    active_res = db.query(
        InventoryReservation.item_id,
        InventoryReservation.location_id,
        func.sum(InventoryReservation.reserved_qty - InventoryReservation.released_qty).label("res_sum")
    ).group_by(
        InventoryReservation.item_id,
        InventoryReservation.location_id
    ).all()

    res_sum_map = {(r.item_id, r.location_id): r.res_sum for r in active_res}

    inventories = db.query(Inventory).all()
    for inv in inventories:
        expected_res = res_sum_map.get((inv.item_id, inv.location_id), 0)
        if inv.reserved != expected_res:
            discrepancies.append({
                "type": "RESERVATION_MISMATCH",
                "details": f"Inventory row {inv.id} has reserved={inv.reserved} but active reservation records sum={expected_res}",
                "warehouse_id": inv.warehouse_id,
                "item_id": inv.item_id,
                "location_id": inv.location_id
            })

    # 2 (cont). Validate Inventory vs Movement Quantity balance
    # Compute inflow and outflow for each physical inventory cell
    movement_balances = {}
    for m in movements:
        # Physical inflow (adds to destination location on-hand)
        if m.movement_type in ("RECEIVING", "PUTAWAY", "RETURN") and m.destination_location_id:
            key = (m.warehouse_id, m.item_id, m.destination_location_id)
            movement_balances[key] = movement_balances.get(key, 0) + m.quantity
        # Physical outflow (deducts from source location on-hand)
        elif m.movement_type in ("PICK", "DAMAGE") and m.source_location_id:
            key = (m.warehouse_id, m.item_id, m.source_location_id)
            movement_balances[key] = movement_balances.get(key, 0) - m.quantity
        elif m.movement_type == "ADJUSTMENT" and m.destination_location_id:
            key = (m.warehouse_id, m.item_id, m.destination_location_id)
            # Find adjustment sign
            movement_balances[key] = movement_balances.get(key, 0) + m.quantity

    for inv in inventories:
        key = (inv.warehouse_id, inv.item_id, inv.location_id)
        computed_qty = movement_balances.get(key, 0)
        # Note: If there are zero movements, computed_qty is 0. If current on_hand is not 0, it means untracked changes!
        if inv.on_hand != computed_qty:
            discrepancies.append({
                "type": "INVENTORY_LEDGER_MISMATCH",
                "details": f"Inventory row {inv.id} on_hand={inv.on_hand} does not match computed ledger quantity={computed_qty}",
                "warehouse_id": inv.warehouse_id,
                "item_id": inv.item_id,
                "location_id": inv.location_id
            })

    # 9. Financial Reconciliation Audits (Phase 5)
    financial_txns = db.query(FinancialTransaction).all()
    seen_sales = {}
    refunds_by_order = {}
    sales_by_order = {}

    for t in financial_txns:
        # Check invalid transaction amount
        if t.amount <= 0:
            discrepancies.append({
                "type": "INVALID_TRANSACTION_AMOUNT",
                "details": f"Financial Transaction {t.transaction_id} has invalid non-positive amount: {t.amount}",
                "transaction_id": t.transaction_id
            })

        # Check unsupported currency
        if t.currency not in ("INR", "USD", "EUR", "GBP"):
            discrepancies.append({
                "type": "UNSUPPORTED_CURRENCY",
                "details": f"Financial Transaction {t.transaction_id} has unsupported currency: '{t.currency}'",
                "transaction_id": t.transaction_id
            })

        # Check invalid status
        if t.status not in ("PENDING", "COMPLETED", "FAILED"):
            discrepancies.append({
                "type": "INVALID_TRANSACTION_STATUS",
                "details": f"Financial Transaction {t.transaction_id} has invalid status: '{t.status}'",
                "transaction_id": t.transaction_id
            })

        # Check nonexistent/orphan order reference
        order_exists = db.query(Order).filter(Order.id == t.order_id).first()
        if not order_exists:
            discrepancies.append({
                "type": "NONEXISTENT_ORDER_REFERENCE",
                "details": f"Financial Transaction {t.transaction_id} references nonexistent order: '{t.order_id}'",
                "transaction_id": t.transaction_id
            })

        # Track sales and refunds by order for limit validations
        if t.transaction_type == "SALE":
            sales_by_order[t.order_id] = sales_by_order.get(t.order_id, 0.0) + t.amount
            if t.order_id in seen_sales:
                discrepancies.append({
                    "type": "DUPLICATE_SALE_TRANSACTION",
                    "details": f"Order '{t.order_id}' has multiple SALE transactions: '{t.transaction_id}' and '{seen_sales[t.order_id]}'",
                    "transaction_id": t.transaction_id
                })
            else:
                seen_sales[t.order_id] = t.transaction_id
        elif t.transaction_type == "REFUND":
            refunds_by_order[t.order_id] = refunds_by_order.get(t.order_id, 0.0) + t.amount

    # Validate refunds against sales
    for order_id, refund_total in refunds_by_order.items():
        sale_total = sales_by_order.get(order_id, 0.0)
        if sale_total == 0.0:
            discrepancies.append({
                "type": "ORPHAN_REFUND_TRANSACTION",
                "details": f"Order '{order_id}' has REFUND transactions totaling {refund_total} but has no SALE transactions",
                "order_id": order_id
            })
        elif refund_total > sale_total:
            discrepancies.append({
                "type": "REFUND_EXCEEDING_ELIGIBLE_AMOUNT",
                "details": f"Order '{order_id}' has refunds totaling {refund_total} which exceeds the gross SALE transaction total {sale_total}",
                "order_id": order_id
            })

    return {
        "status": "success" if not discrepancies else "failed",
        "inconsistencies_count": len(discrepancies),
        "inconsistencies": discrepancies
    }
