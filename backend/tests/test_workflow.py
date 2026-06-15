"""Integration test - full business workflow for Campus Errand Platform."""

import requests

BASE = "http://localhost:8000"


def test_full_workflow():
    session = requests.Session()

    # 1. Register user A (publisher)
    print("=== 1. Register User A ===")
    r = session.post(f"{BASE}/auth/register", data={
        "username": "alice",
        "phone": "13800000001",
        "password": "pass123"
    }, allow_redirects=False)
    assert r.status_code in (200, 303), f"Register failed: {r.status_code}"
    print(f"  Status: {r.status_code}, Location: {r.headers.get('Location')}")
    # Follow redirect to set session cookie
    r = session.get(f"{BASE}/user/monitoring")
    print(f"  User monitoring: {r.status_code}")
    assert "alice" in r.text or r.status_code == 200

    # 2. Register user B (will be rider)
    print("\n=== 2. Register User B ===")
    session2 = requests.Session()
    r = session2.post(f"{BASE}/auth/register", data={
        "username": "bob",
        "phone": "13800000002",
        "password": "pass123"
    }, allow_redirects=False)
    assert r.status_code in (200, 303)
    r = session2.get(f"{BASE}/user/monitoring")
    print(f"  User monitoring: {r.status_code}")

    # 3. User B becomes rider
    print("\n=== 3. Become Rider ===")
    r = session2.post(f"{BASE}/user/become_rider", data={
        "service_area": "北校区"
    }, allow_redirects=False)
    assert r.status_code in (200, 303)
    print(f"  Become rider: {r.status_code}, Location: {r.headers.get('Location')}")

    # 4. User A creates an order
    print("\n=== 4. Create Order ===")
    r = session.post(f"{BASE}/user/place_order", data={
        "order_type": "takeout",
        "reward": 15.00,
        "delivery_addr": "北校区宿舍3号楼501",
        "item_desc": "一份黄焖鸡米饭",
        "pickup_addr": "三食堂二楼",
        "express_company": "",
        "express_no": "",
        "store_name": "",
        "item_name": "",
        "custom_desc": "",
        "item_weight": "",
        "deadline": "",
    }, allow_redirects=False)
    assert r.status_code in (200, 303), f"Create order failed: {r.status_code}"
    print(f"  Create order: {r.status_code}, Location: {r.headers.get('Location')}")

    # 5. Verify order appears in user monitoring
    print("\n=== 5. Verify Order ===")
    r = session.get(f"{BASE}/user/monitoring")
    assert r.status_code == 200
    assert "一份黄焖鸡米饭" in r.text or "黄焖鸡" in r.text or "takeout" in r.text, "Order not found on user page"
    print(f"  Order visible on user page: OK")

    # 6. Rider B views pending orders
    print("\n=== 6. Rider Views Pending Orders ===")
    r = session2.get(f"{BASE}/rider/monitoring")
    assert r.status_code == 200
    print(f"  Rider monitoring: {r.status_code}")
    # Extract order info from page
    has_order = "一份黄焖鸡米饭" in r.text or "takeout" in r.text or "15.00" in r.text
    print(f"  Pending order visible: {has_order}")

    # 7. Find order ID and accept it
    print("\n=== 7. Accept Order ===")
    import re
    # Find order_no in the page to extract order_id
    match = re.search(r'/rider/accept_order/(\d+)', r.text)
    if match:
        order_id = int(match.group(1))
        print(f"  Order ID: {order_id}")
        r = session2.post(f"{BASE}/rider/accept_order/{order_id}", allow_redirects=False)
        assert r.status_code in (200, 303), f"Accept failed: {r.status_code}"
        print(f"  Accept order: {r.status_code}, Location: {r.headers.get('Location')}")
    else:
        print("  Could not find order - check rider page manually")
        return False

    # 8. Rider updates status: delivering
    print("\n=== 8. Update to 'delivering' ===")
    r = session2.get(f"{BASE}/rider/update_status/{order_id}/delivering", allow_redirects=False)
    assert r.status_code in (200, 303), f"Update to delivering failed: {r.status_code}"
    print(f"  Status -> delivering: OK")

    # 9. Rider updates status: delivered
    print("\n=== 9. Update to 'delivered' ===")
    r = session2.get(f"{BASE}/rider/update_status/{order_id}/delivered", allow_redirects=False)
    assert r.status_code in (200, 303), f"Update to delivered failed: {r.status_code}"
    print(f"  Status -> delivered: OK")

    # 10. User A confirms delivery (settlement)
    print("\n=== 10. Confirm Delivery & Settlement ===")
    r = session.get(f"{BASE}/user/confirm_delivery/{order_id}", allow_redirects=False)
    assert r.status_code in (200, 303), f"Confirm delivery failed: {r.status_code}"
    print(f"  Confirm delivery: {r.status_code}")

    print("\n================================================")
    print("  ALL INTEGRATION TESTS PASSED!")
    print("================================================")
    return True


if __name__ == "__main__":
    result = test_full_workflow()
    print(f"\nFinal result: {'PASS' if result else 'FAIL'}")
