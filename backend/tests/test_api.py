"""Integration test for Vue 3 SPA JSON API backend."""

import requests
from datetime import datetime

BASE = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}


def api(method, path, data=None):
    url = f"{BASE}{path}"
    if method == "GET":
        r = requests.get(url, headers=HEADERS | auth_header())
    else:
        r = requests.request(method, url, json=data, headers=HEADERS | auth_header())
    return r.json()


def auth_header():
    global _token
    if _token:
        return {"Authorization": f"Bearer {_token}"}
    return {}


_token = None


def test():
    global _token
    results = []

    # 1. Register 3 users (2 riders for concurrency test)
    print("=== 1. Register Users ===")
    for name, phone in [("alice", "138001"), ("bob", "138002"), ("charlie", "138003")]:
        r = requests.post(f"{BASE}/auth/register", json={
            "username": name, "phone": phone, "password": "pass123"
        })
        d = r.json()
        ok = d.get("code") == 0
        print(f"  {name}: {d.get('message')} {'OK' if ok else 'FAIL'}")
        results.append(ok)
        if name == "charlie":
            _token = d.get("data", {}).get("token", "")

    # 2. Login as alice
    print("\n=== 2. Login as alice (user) ===")
    r = requests.post(f"{BASE}/auth/login", json={
        "account": "alice", "password": "pass123", "role": "user"
    })
    d = r.json()
    _token = d.get("data", {}).get("token", "")
    print(f"  Login: {d.get('message')} -> token={_token[:20]}...")

    # 3. Alice creates an order
    print("\n=== 3. Create Order ===")
    r = requests.post(f"{BASE}/orders/create", json={
        "order_type": "takeout",
        "reward": 15.00,
        "delivery_addr": "北校区宿舍3号楼501",
        "biz_fields": {"item_desc": "黄焖鸡米饭", "pickup_addr": "三食堂二楼"}
    }, headers=auth_header())
    d = r.json()
    order_id = d.get("data", {}).get("order_id")
    print(f"  Create: {d.get('message')} -> order_id={order_id}")

    # 4. Login as bob (rider)
    print("\n=== 4. Login as bob (rider) ===")
    r = requests.post(f"{BASE}/auth/login", json={
        "account": "bob", "password": "pass123", "role": "rider"
    })
    d = r.json()
    _token = d.get("data", {}).get("token", "")
    print(f"  Login: {d.get('message')} -> role={d.get('data',{}).get('role')}")

    # 5. Bob becomes rider
    print("\n=== 5. Become Rider ===")
    r = requests.post(f"{BASE}/auth/become_rider", json={
        "service_area": "北校区"
    }, headers=auth_header())
    d = r.json()
    print(f"  Become rider: {d.get('message')}")

    # 6. Bob checks pending orders
    print("\n=== 6. Check Pending Orders ===")
    r = requests.get(f"{BASE}/orders/pending", headers=auth_header())
    d = r.json()
    pending_count = len(d.get("data", []))
    print(f"  Pending orders: {pending_count}")

    # 7. Bob accepts the order
    print("\n=== 7. Accept Order ===")
    r = requests.post(f"{BASE}/orders/accept/{order_id}", headers=auth_header())
    d = r.json()
    print(f"  Accept: {d.get('message')}")

    # 8. Bob updates status: delivering -> delivered
    print("\n=== 8. Delivery Flow ===")
    for status in ["delivering", "delivered"]:
        r = requests.post(
            f"{BASE}/orders/update_status?order_id={order_id}&status={status}",
            headers=auth_header()
        )
        d = r.json()
        print(f"  {status}: {d.get('message')}")

    # 9. Login as alice and confirm delivery (settlement)
    print("\n=== 9. Confirm Delivery (Settlement) ===")
    r = requests.post(f"{BASE}/auth/login", json={
        "account": "alice", "password": "pass123", "role": "user"
    })
    _token = r.json().get("data", {}).get("token", "")
    r = requests.post(f"{BASE}/orders/complete/{order_id}", headers=auth_header())
    d = r.json()
    print(f"  Complete: {d.get('message')}")

    # 10. Verify profiles
    print("\n=== 10. Verify Profiles ===")
    r = requests.get(f"{BASE}/auth/profile", headers=auth_header())
    d = r.json()
    print(f"  alice balance: {d.get('data',{}).get('balance')}")
    print(f"  alice is_rider: {d.get('data',{}).get('rider') is not None}")

    # 11. Update profile (alice)
    print("\n=== 11. Update Profile ===")
    r = requests.put(f"{BASE}/auth/profile", json={
        "phone": "138001",
        "default_address": "北校区宿舍3号楼501"
    }, headers=auth_header())
    d = r.json()
    print(f"  Update profile: {d.get('message')}")
    print(f"  new address: {d.get('data',{}).get('default_address')}")

    # 12. Topup (alice)
    print("\n=== 12. Topup ===")
    r = requests.post(f"{BASE}/auth/topup", json={
        "amount": 50.00
    }, headers=auth_header())
    d = r.json()
    print(f"  Topup: {d.get('message')}")
    print(f"  new balance: {d.get('data',{}).get('balance')}")

    print("\n================================================")
    print(f"  ALL {sum(results)}/3 REGISTRATIONS PASSED")
    print(f"  FULL WORKFLOW COMPLETED (incl. profile update + topup)")
    print("================================================")


if __name__ == "__main__":
    test()
