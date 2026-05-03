"""
Seed script — Ylopage Marketplace taxonomy
Run: python seed.py
"""

import getpass
import sys
import requests

API_BASE = "http://localhost:8001/api/v1"
EMAIL = "kiranpesarlanka9@gmail.com"

# ── Taxonomy data ──────────────────────────────────────────────────────────────

TAXONOMY = [
    {
        "name": "Home Services",
        "description": "Professional home maintenance and repair services",
        "display_order": 1,
        "sub_categories": [
            {
                "name": "Cleaning",
                "description": "Deep cleaning for homes, kitchens, and bathrooms",
                "display_order": 1,
                "service_types": [
                    {"name": "Home Deep Clean", "description": "Full home deep cleaning service", "billing_unit": "per_visit", "suggested_price_min": 1200, "suggested_price_max": 3000, "suggested_duration_minutes": 180, "display_order": 1},
                    {"name": "Kitchen Cleaning", "description": "Thorough kitchen and chimney cleaning", "billing_unit": "per_visit", "suggested_price_min": 600, "suggested_price_max": 1500, "suggested_duration_minutes": 90, "display_order": 2},
                    {"name": "Bathroom Cleaning", "description": "Deep scrub and sanitisation of bathrooms", "billing_unit": "per_visit", "suggested_price_min": 400, "suggested_price_max": 800, "suggested_duration_minutes": 60, "display_order": 3},
                ],
            },
            {
                "name": "Plumbing",
                "description": "Pipe, tap, drain, and water heater repairs",
                "display_order": 2,
                "service_types": [
                    {"name": "Pipe Leak Fix", "description": "Diagnosis and repair of pipe leaks", "billing_unit": "per_visit", "suggested_price_min": 300, "suggested_price_max": 1000, "suggested_duration_minutes": 60, "display_order": 1},
                    {"name": "Tap / Faucet Repair", "description": "Repair or replacement of taps and faucets", "billing_unit": "per_visit", "suggested_price_min": 200, "suggested_price_max": 600, "suggested_duration_minutes": 30, "display_order": 2},
                    {"name": "Drain Unblocking", "description": "Clearing blocked drains and floor traps", "billing_unit": "per_visit", "suggested_price_min": 300, "suggested_price_max": 800, "suggested_duration_minutes": 45, "display_order": 3},
                ],
            },
            {
                "name": "Electrical",
                "description": "Wiring, switches, fans, and fixture installation",
                "display_order": 3,
                "service_types": [
                    {"name": "Switch / Socket Repair", "description": "Repair or replacement of switches and sockets", "billing_unit": "per_visit", "suggested_price_min": 150, "suggested_price_max": 500, "suggested_duration_minutes": 30, "display_order": 1},
                    {"name": "Fan Installation", "description": "Ceiling or exhaust fan fitting and wiring", "billing_unit": "per_visit", "suggested_price_min": 300, "suggested_price_max": 700, "suggested_duration_minutes": 45, "display_order": 2},
                    {"name": "Electrical Wiring Repair", "description": "Fault tracing and wiring repair", "billing_unit": "per_hour", "suggested_price_min": 400, "suggested_price_max": 800, "suggested_duration_minutes": 60, "display_order": 3},
                ],
            },
            {
                "name": "Carpentry",
                "description": "Furniture repair, assembly, and custom woodwork",
                "display_order": 4,
                "service_types": [
                    {"name": "Furniture Assembly", "description": "Assembly of flat-pack or modular furniture", "billing_unit": "per_visit", "suggested_price_min": 300, "suggested_price_max": 1200, "suggested_duration_minutes": 90, "display_order": 1},
                    {"name": "Door / Window Repair", "description": "Fixing hinges, locks, and frames", "billing_unit": "per_visit", "suggested_price_min": 200, "suggested_price_max": 800, "suggested_duration_minutes": 60, "display_order": 2},
                ],
            },
        ],
    },
    {
        "name": "Beauty & Wellness",
        "description": "At-home beauty, hair, and spa services",
        "display_order": 2,
        "sub_categories": [
            {
                "name": "Hair Care",
                "description": "Haircuts, colouring, and treatments at home",
                "display_order": 1,
                "service_types": [
                    {"name": "Haircut – Men", "description": "Professional men's haircut at home", "billing_unit": "per_visit", "suggested_price_min": 200, "suggested_price_max": 500, "suggested_duration_minutes": 30, "display_order": 1},
                    {"name": "Haircut – Women", "description": "Women's haircut and styling at home", "billing_unit": "per_visit", "suggested_price_min": 400, "suggested_price_max": 1000, "suggested_duration_minutes": 60, "display_order": 2},
                    {"name": "Hair Colour", "description": "Full hair colouring with professional products", "billing_unit": "per_visit", "suggested_price_min": 800, "suggested_price_max": 2500, "suggested_duration_minutes": 120, "display_order": 3},
                ],
            },
            {
                "name": "Skin Care",
                "description": "Facials, cleanups, and skin treatments",
                "display_order": 2,
                "service_types": [
                    {"name": "Facial", "description": "Deep cleansing and nourishing facial", "billing_unit": "per_visit", "suggested_price_min": 500, "suggested_price_max": 2000, "suggested_duration_minutes": 60, "display_order": 1},
                    {"name": "Cleanup", "description": "Basic skin cleanup and moisturising", "billing_unit": "per_visit", "suggested_price_min": 300, "suggested_price_max": 800, "suggested_duration_minutes": 45, "display_order": 2},
                ],
            },
            {
                "name": "Massage & Spa",
                "description": "Relaxation and therapeutic massage at home",
                "display_order": 3,
                "service_types": [
                    {"name": "Full Body Massage", "description": "60-min relaxation massage by a certified therapist", "billing_unit": "per_hour", "suggested_price_min": 800, "suggested_price_max": 2000, "suggested_duration_minutes": 60, "display_order": 1},
                    {"name": "Head & Shoulder Massage", "description": "30-min stress-relief head and shoulder massage", "billing_unit": "per_visit", "suggested_price_min": 400, "suggested_price_max": 800, "suggested_duration_minutes": 30, "display_order": 2},
                ],
            },
        ],
    },
    {
        "name": "Auto Services",
        "description": "Car and two-wheeler services at your doorstep",
        "display_order": 3,
        "sub_categories": [
            {
                "name": "Car Wash",
                "description": "Exterior, interior, and full-detail car wash",
                "display_order": 1,
                "service_types": [
                    {"name": "Exterior Wash", "description": "Hand wash and dry of car exterior", "billing_unit": "per_visit", "suggested_price_min": 300, "suggested_price_max": 600, "suggested_duration_minutes": 30, "display_order": 1},
                    {"name": "Full Detail Wash", "description": "Exterior wash + interior vacuum and wipe-down", "billing_unit": "per_visit", "suggested_price_min": 700, "suggested_price_max": 1500, "suggested_duration_minutes": 90, "display_order": 2},
                ],
            },
            {
                "name": "Tyre Services",
                "description": "Puncture repairs, rotation, and tyre replacement",
                "display_order": 2,
                "service_types": [
                    {"name": "Puncture Repair", "description": "On-site tubeless or tube tyre puncture fix", "billing_unit": "per_tyre", "suggested_price_min": 150, "suggested_price_max": 400, "suggested_duration_minutes": 20, "display_order": 1},
                    {"name": "Tyre Rotation", "description": "Rotate all four tyres for even wear", "billing_unit": "per_visit", "suggested_price_min": 300, "suggested_price_max": 600, "suggested_duration_minutes": 30, "display_order": 2},
                ],
            },
            {
                "name": "Oil & Fluids",
                "description": "Engine oil, coolant, and brake fluid top-up and change",
                "display_order": 3,
                "service_types": [
                    {"name": "Engine Oil Change", "description": "Drain and refill with fresh engine oil", "billing_unit": "per_visit", "suggested_price_min": 500, "suggested_price_max": 1500, "suggested_duration_minutes": 45, "display_order": 1},
                    {"name": "Coolant Top-up", "description": "Check and top-up engine coolant level", "billing_unit": "per_visit", "suggested_price_min": 200, "suggested_price_max": 500, "suggested_duration_minutes": 20, "display_order": 2},
                ],
            },
        ],
    },
    {
        "name": "Appliance Repair",
        "description": "Repair and servicing of home appliances",
        "display_order": 4,
        "sub_categories": [
            {
                "name": "Air Conditioning",
                "description": "AC service, gas refill, and installation",
                "display_order": 1,
                "service_types": [
                    {"name": "AC Service & Clean", "description": "Filter clean, coil wash, and general service", "billing_unit": "per_unit", "suggested_price_min": 500, "suggested_price_max": 1200, "suggested_duration_minutes": 60, "display_order": 1},
                    {"name": "AC Gas Refill", "description": "Refrigerant top-up for cooling efficiency", "billing_unit": "per_unit", "suggested_price_min": 1500, "suggested_price_max": 3000, "suggested_duration_minutes": 45, "display_order": 2},
                    {"name": "AC Installation", "description": "Full installation of split or window AC unit", "billing_unit": "per_unit", "suggested_price_min": 1000, "suggested_price_max": 2000, "suggested_duration_minutes": 120, "display_order": 3},
                ],
            },
            {
                "name": "Washing Machine",
                "description": "Washing machine servicing and repairs",
                "display_order": 2,
                "service_types": [
                    {"name": "Washing Machine Service", "description": "Routine service and drum clean", "billing_unit": "per_unit", "suggested_price_min": 400, "suggested_price_max": 800, "suggested_duration_minutes": 60, "display_order": 1},
                    {"name": "Washing Machine Repair", "description": "Fault diagnosis and repair", "billing_unit": "per_unit", "suggested_price_min": 500, "suggested_price_max": 2000, "suggested_duration_minutes": 90, "display_order": 2},
                ],
            },
            {
                "name": "Refrigerator",
                "description": "Fridge servicing, gas refill, and repairs",
                "display_order": 3,
                "service_types": [
                    {"name": "Refrigerator Service", "description": "Coil clean and general maintenance", "billing_unit": "per_unit", "suggested_price_min": 400, "suggested_price_max": 900, "suggested_duration_minutes": 60, "display_order": 1},
                    {"name": "Refrigerator Gas Refill", "description": "Refrigerant refill for cooling issues", "billing_unit": "per_unit", "suggested_price_min": 1200, "suggested_price_max": 2500, "suggested_duration_minutes": 60, "display_order": 2},
                ],
            },
        ],
    },
]


# ── Runner ─────────────────────────────────────────────────────────────────────

def log(msg): print(msg, flush=True)
def ok(msg):  print(f"  ✓ {msg}", flush=True)
def err(msg): print(f"  ✗ {msg}", flush=True)


def login(password: str) -> str:
    r = requests.post(f"{API_BASE}/auth/login", json={"email": EMAIL, "password": password})
    if r.status_code == 200:
        return r.json()["access_token"]
    err(f"Login failed: {r.status_code} {r.text}")
    sys.exit(1)


def post(token: str, path: str, payload: dict) -> dict | None:
    r = requests.post(
        f"{API_BASE}{path}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    if r.status_code == 201:
        return r.json()
    err(f"POST {path} → {r.status_code}: {r.text}")
    return None


def seed(token: str):
    total_cats = total_subs = total_types = 0

    for cat_data in TAXONOMY:
        sub_categories = cat_data.pop("sub_categories")
        log(f"\n📂 Category: {cat_data['name']}")

        cat = post(token, "/taxonomy/categories", cat_data)
        if not cat:
            continue
        ok(f"Created category '{cat['name']}' ({cat['id']})")
        total_cats += 1

        for sub_data in sub_categories:
            service_types = sub_data.pop("service_types")
            log(f"  📁 Sub-category: {sub_data['name']}")

            sub = post(token, f"/taxonomy/categories/{cat['id']}/sub-categories", sub_data)
            if not sub:
                continue
            ok(f"Created sub-category '{sub['name']}' ({sub['id']})")
            total_subs += 1

            for svc_data in service_types:
                svc = post(token, f"/taxonomy/sub-categories/{sub['id']}/service-types", svc_data)
                if not svc:
                    continue
                ok(f"  Created service type '{svc['name']}'")
                total_types += 1

    print(f"\n{'─'*50}")
    print(f"Done — {total_cats} categories, {total_subs} sub-categories, {total_types} service types created.")


if __name__ == "__main__":
    print(f"Ylopage Seed — logging in as {EMAIL}")
    password = getpass.getpass("Password: ")
    token = login(password)
    print("Login successful.\n")
    seed(token)
