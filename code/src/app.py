import streamlit as st
import requests

API_BASE = "http://localhost:8001/api/v1"

BILLING_UNITS = ["per_visit", "per_hour", "per_tyre", "per_unit"]


# ── API helpers ────────────────────────────────────────────────────────────────

def _headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def api_get(path):
    return requests.get(f"{API_BASE}{path}", headers=_headers())


def api_post(path, payload):
    return requests.post(f"{API_BASE}{path}", json=payload, headers=_headers())


def api_patch(path, payload):
    return requests.patch(f"{API_BASE}{path}", json=payload, headers=_headers())


def show_api_error(r):
    try:
        detail = r.json().get("detail", f"Error {r.status_code}")
    except Exception:
        detail = f"Error {r.status_code}"
    st.error(detail)


# ── Auth ───────────────────────────────────────────────────────────────────────

def do_login(email, password):
    r = requests.post(f"{API_BASE}/auth/login", json={"email": email, "password": password})
    if r.status_code == 200:
        return r.json()["access_token"]
    return None


# ── Data fetchers ──────────────────────────────────────────────────────────────

def fetch_categories():
    r = api_get("/taxonomy/categories")
    return r.json() if r.status_code == 200 else []


def fetch_sub_categories(cat_id):
    r = api_get(f"/taxonomy/categories/{cat_id}/sub-categories")
    return r.json() if r.status_code == 200 else []


def fetch_service_types(sub_id):
    r = api_get(f"/taxonomy/sub-categories/{sub_id}/service-types")
    return r.json() if r.status_code == 200 else []


# ── Session init ───────────────────────────────────────────────────────────────

for _k, _v in {"token": None, "page": "categories", "sel_cat": None, "sel_sub": None}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


st.set_page_config(page_title="Ylopage Ops", layout="wide", page_icon="🛒")


# ── Login ──────────────────────────────────────────────────────────────────────

if not st.session_state.token:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("## Ylopage Operations")
        st.markdown("---")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True, type="primary"):
            token = do_login(email, password)
            if token:
                st.session_state.token = token
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.stop()


# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### Ylopage Ops")
    st.divider()
    if st.button("📂 Categories", use_container_width=True):
        st.session_state.page = "categories"
        st.session_state.sel_cat = None
        st.session_state.sel_sub = None
        st.rerun()
    st.divider()
    if st.button("Logout", use_container_width=True):
        st.session_state.token = None
        st.rerun()


# ── Helpers ────────────────────────────────────────────────────────────────────

def status_badge(is_active: bool) -> str:
    return ":green[● Active]" if is_active else ":red[● Inactive]"


def toggle_key(prefix, id_):
    return f"editing_{prefix}_{id_}"


# ── Categories page ────────────────────────────────────────────────────────────

def categories_page():
    st.title("📂 Categories")

    with st.expander("➕ Add New Category"):
        with st.form("add_cat_form", clear_on_submit=True):
            name = st.text_input("Name *")
            description = st.text_area("Description")
            icon = st.text_input("Icon URL")
            display_order = st.number_input("Display Order", min_value=0, value=0, step=1)
            if st.form_submit_button("Create Category", type="primary"):
                if len(name.strip()) < 2:
                    st.error("Name must be at least 2 characters.")
                else:
                    payload = {"name": name.strip(), "display_order": int(display_order)}
                    if description.strip():
                        payload["description"] = description.strip()
                    if icon.strip():
                        payload["icon"] = icon.strip()
                    r = api_post("/taxonomy/categories", payload)
                    if r.status_code == 201:
                        st.success(f"'{name}' created.")
                        st.rerun()
                    else:
                        show_api_error(r)

    st.divider()
    cats = fetch_categories()

    if not cats:
        st.info("No categories yet. Add one above.")
        return

    for cat in cats:
        ekey = toggle_key("cat", cat["id"])
        with st.container(border=True):
            c_icon, c_info, c_actions = st.columns([1, 5, 3])

            with c_icon:
                if cat.get("icon"):
                    st.image(cat["icon"], width=64)
                else:
                    st.markdown("## 🗂️")

            with c_info:
                st.markdown(f"### {cat['name']}  {status_badge(cat['is_active'])}")
                st.caption(f"Slug: `{cat['slug']}`  ·  Order: `{cat['display_order']}`")
                if cat.get("description"):
                    st.caption(cat["description"])

            with c_actions:
                a1, a2, a3 = st.columns(3)
                with a1:
                    if st.button("Sub-cats →", key=f"nav_{cat['id']}", use_container_width=True):
                        st.session_state.sel_cat = cat
                        st.session_state.page = "sub_categories"
                        st.rerun()
                with a2:
                    if st.button("Edit", key=f"edit_btn_{cat['id']}", use_container_width=True):
                        st.session_state[ekey] = not st.session_state.get(ekey, False)
                        st.rerun()
                with a3:
                    lbl = "Deactivate" if cat["is_active"] else "Activate"
                    if st.button(lbl, key=f"toggle_{cat['id']}", use_container_width=True):
                        r = api_patch(f"/taxonomy/categories/{cat['id']}", {"is_active": not cat["is_active"]})
                        if r.status_code == 200:
                            st.rerun()
                        else:
                            show_api_error(r)

            if st.session_state.get(ekey):
                st.markdown("---")
                with st.form(f"edit_cat_{cat['id']}"):
                    st.markdown("**Edit Category**")
                    e_name = st.text_input("Name", value=cat["name"])
                    e_desc = st.text_area("Description", value=cat.get("description") or "")
                    e_icon = st.text_input("Icon URL", value=cat.get("icon") or "")
                    e_order = st.number_input("Display Order", min_value=0, value=cat["display_order"], step=1)
                    s_col, c_col = st.columns(2)
                    with s_col:
                        save = st.form_submit_button("Save", type="primary", use_container_width=True)
                    with c_col:
                        cancel = st.form_submit_button("Cancel", use_container_width=True)
                    if save:
                        payload = {
                            "name": e_name.strip(),
                            "description": e_desc.strip() or None,
                            "icon": e_icon.strip() or None,
                            "display_order": int(e_order),
                        }
                        r = api_patch(f"/taxonomy/categories/{cat['id']}", payload)
                        if r.status_code == 200:
                            st.session_state.pop(ekey, None)
                            st.rerun()
                        else:
                            show_api_error(r)
                    if cancel:
                        st.session_state.pop(ekey, None)
                        st.rerun()


# ── Sub-categories page ────────────────────────────────────────────────────────

def sub_categories_page():
    cat = st.session_state.sel_cat

    bc1, bc2 = st.columns([1, 9])
    with bc1:
        if st.button("← Back"):
            st.session_state.page = "categories"
            st.session_state.sel_cat = None
            st.rerun()
    with bc2:
        st.title(f"📁 Sub-categories  ›  {cat['name']}")

    with st.expander("➕ Add New Sub-category"):
        with st.form("add_sub_form", clear_on_submit=True):
            name = st.text_input("Name *")
            description = st.text_area("Description")
            icon = st.text_input("Icon URL")
            display_order = st.number_input("Display Order", min_value=0, value=0, step=1)
            if st.form_submit_button("Create Sub-category", type="primary"):
                if len(name.strip()) < 2:
                    st.error("Name must be at least 2 characters.")
                else:
                    payload = {"name": name.strip(), "display_order": int(display_order)}
                    if description.strip():
                        payload["description"] = description.strip()
                    if icon.strip():
                        payload["icon"] = icon.strip()
                    r = api_post(f"/taxonomy/categories/{cat['id']}/sub-categories", payload)
                    if r.status_code == 201:
                        st.success(f"'{name}' created.")
                        st.rerun()
                    else:
                        show_api_error(r)

    st.divider()
    subs = fetch_sub_categories(cat["id"])

    if not subs:
        st.info("No sub-categories yet. Add one above.")
        return

    for sub in subs:
        ekey = toggle_key("sub", sub["id"])
        with st.container(border=True):
            c_icon, c_info, c_actions = st.columns([1, 5, 3])

            with c_icon:
                if sub.get("icon"):
                    st.image(sub["icon"], width=64)
                else:
                    st.markdown("## 📁")

            with c_info:
                st.markdown(f"### {sub['name']}  {status_badge(sub['is_active'])}")
                st.caption(f"Slug: `{sub['slug']}`  ·  Order: `{sub['display_order']}`")
                if sub.get("description"):
                    st.caption(sub["description"])

            with c_actions:
                a1, a2, a3 = st.columns(3)
                with a1:
                    if st.button("Types →", key=f"nav_{sub['id']}", use_container_width=True):
                        st.session_state.sel_sub = sub
                        st.session_state.page = "service_types"
                        st.rerun()
                with a2:
                    if st.button("Edit", key=f"edit_btn_{sub['id']}", use_container_width=True):
                        st.session_state[ekey] = not st.session_state.get(ekey, False)
                        st.rerun()
                with a3:
                    lbl = "Deactivate" if sub["is_active"] else "Activate"
                    if st.button(lbl, key=f"toggle_{sub['id']}", use_container_width=True):
                        r = api_patch(f"/taxonomy/sub-categories/{sub['id']}", {"is_active": not sub["is_active"]})
                        if r.status_code == 200:
                            st.rerun()
                        else:
                            show_api_error(r)

            if st.session_state.get(ekey):
                st.markdown("---")
                with st.form(f"edit_sub_{sub['id']}"):
                    st.markdown("**Edit Sub-category**")
                    e_name = st.text_input("Name", value=sub["name"])
                    e_desc = st.text_area("Description", value=sub.get("description") or "")
                    e_icon = st.text_input("Icon URL", value=sub.get("icon") or "")
                    e_order = st.number_input("Display Order", min_value=0, value=sub["display_order"], step=1)
                    s_col, c_col = st.columns(2)
                    with s_col:
                        save = st.form_submit_button("Save", type="primary", use_container_width=True)
                    with c_col:
                        cancel = st.form_submit_button("Cancel", use_container_width=True)
                    if save:
                        payload = {
                            "name": e_name.strip(),
                            "description": e_desc.strip() or None,
                            "icon": e_icon.strip() or None,
                            "display_order": int(e_order),
                        }
                        r = api_patch(f"/taxonomy/sub-categories/{sub['id']}", payload)
                        if r.status_code == 200:
                            st.session_state.pop(ekey, None)
                            st.rerun()
                        else:
                            show_api_error(r)
                    if cancel:
                        st.session_state.pop(ekey, None)
                        st.rerun()


# ── Service types page ─────────────────────────────────────────────────────────

def service_types_page():
    cat = st.session_state.sel_cat
    sub = st.session_state.sel_sub

    bc1, bc2 = st.columns([1, 9])
    with bc1:
        if st.button("← Back"):
            st.session_state.page = "sub_categories"
            st.session_state.sel_sub = None
            st.rerun()
    with bc2:
        st.title(f"🔧 Service Types  ›  {cat['name']}  ›  {sub['name']}")

    with st.expander("➕ Add New Service Type"):
        with st.form("add_svc_form", clear_on_submit=True):
            name = st.text_input("Name *")
            description = st.text_area("Description")
            p1, p2 = st.columns(2)
            with p1:
                price_min = st.number_input("Suggested Min Price (₹)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
            with p2:
                price_max = st.number_input("Suggested Max Price (₹)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
            d1, d2, d3 = st.columns(3)
            with d1:
                duration = st.number_input("Duration (minutes)", min_value=0, value=0, step=15)
            with d2:
                billing_unit = st.selectbox("Billing Unit", BILLING_UNITS, format_func=lambda x: x.replace("_", " ").title())
            with d3:
                display_order = st.number_input("Display Order", min_value=0, value=0, step=1)
            if st.form_submit_button("Create Service Type", type="primary"):
                if len(name.strip()) < 2:
                    st.error("Name must be at least 2 characters.")
                else:
                    payload = {
                        "name": name.strip(),
                        "billing_unit": billing_unit,
                        "display_order": int(display_order),
                    }
                    if description.strip():
                        payload["description"] = description.strip()
                    if price_min > 0:
                        payload["suggested_price_min"] = price_min
                    if price_max > 0:
                        payload["suggested_price_max"] = price_max
                    if duration > 0:
                        payload["suggested_duration_minutes"] = int(duration)
                    r = api_post(f"/taxonomy/sub-categories/{sub['id']}/service-types", payload)
                    if r.status_code == 201:
                        st.success(f"'{name}' created.")
                        st.rerun()
                    else:
                        show_api_error(r)

    st.divider()
    types = fetch_service_types(sub["id"])

    if not types:
        st.info("No service types yet. Add one above.")
        return

    for svc in types:
        ekey = toggle_key("svc", svc["id"])
        with st.container(border=True):
            c_info, c_pricing, c_actions = st.columns([4, 3, 3])

            with c_info:
                st.markdown(f"### {svc['name']}  {status_badge(svc['is_active'])}")
                st.caption(f"Slug: `{svc['slug']}`  ·  Order: `{svc['display_order']}`")
                if svc.get("description"):
                    st.caption(svc["description"])

            with c_pricing:
                billing_label = svc["billing_unit"].replace("_", " ").title()
                st.markdown(f"**{billing_label}**")
                p_min = svc.get("suggested_price_min")
                p_max = svc.get("suggested_price_max")
                if p_min or p_max:
                    st.caption(f"₹{p_min or '—'}  –  ₹{p_max or '—'}")
                if svc.get("suggested_duration_minutes"):
                    st.caption(f"⏱ {svc['suggested_duration_minutes']} min")

            with c_actions:
                a1, a2 = st.columns(2)
                with a1:
                    if st.button("Edit", key=f"edit_btn_{svc['id']}", use_container_width=True):
                        st.session_state[ekey] = not st.session_state.get(ekey, False)
                        st.rerun()
                with a2:
                    lbl = "Deactivate" if svc["is_active"] else "Activate"
                    if st.button(lbl, key=f"toggle_{svc['id']}", use_container_width=True):
                        r = api_patch(f"/taxonomy/service-types/{svc['id']}", {"is_active": not svc["is_active"]})
                        if r.status_code == 200:
                            st.rerun()
                        else:
                            show_api_error(r)

            if st.session_state.get(ekey):
                st.markdown("---")
                with st.form(f"edit_svc_{svc['id']}"):
                    st.markdown("**Edit Service Type**")
                    e_name = st.text_input("Name", value=svc["name"])
                    e_desc = st.text_area("Description", value=svc.get("description") or "")
                    ep1, ep2 = st.columns(2)
                    with ep1:
                        e_pmin = st.number_input(
                            "Min Price (₹)", min_value=0.0,
                            value=float(svc.get("suggested_price_min") or 0),
                            step=10.0, format="%.2f",
                        )
                    with ep2:
                        e_pmax = st.number_input(
                            "Max Price (₹)", min_value=0.0,
                            value=float(svc.get("suggested_price_max") or 0),
                            step=10.0, format="%.2f",
                        )
                    ed1, ed2, ed3 = st.columns(3)
                    with ed1:
                        e_dur = st.number_input(
                            "Duration (min)", min_value=0,
                            value=int(svc.get("suggested_duration_minutes") or 0),
                            step=15,
                        )
                    with ed2:
                        current_idx = BILLING_UNITS.index(svc["billing_unit"]) if svc["billing_unit"] in BILLING_UNITS else 0
                        e_billing = st.selectbox(
                            "Billing Unit", BILLING_UNITS,
                            index=current_idx,
                            format_func=lambda x: x.replace("_", " ").title(),
                        )
                    with ed3:
                        e_order = st.number_input("Display Order", min_value=0, value=svc["display_order"], step=1)
                    s_col, c_col = st.columns(2)
                    with s_col:
                        save = st.form_submit_button("Save", type="primary", use_container_width=True)
                    with c_col:
                        cancel = st.form_submit_button("Cancel", use_container_width=True)
                    if save:
                        payload = {
                            "name": e_name.strip(),
                            "description": e_desc.strip() or None,
                            "billing_unit": e_billing,
                            "display_order": int(e_order),
                            "suggested_price_min": e_pmin if e_pmin > 0 else None,
                            "suggested_price_max": e_pmax if e_pmax > 0 else None,
                            "suggested_duration_minutes": int(e_dur) if e_dur > 0 else None,
                        }
                        r = api_patch(f"/taxonomy/service-types/{svc['id']}", payload)
                        if r.status_code == 200:
                            st.session_state.pop(ekey, None)
                            st.rerun()
                        else:
                            show_api_error(r)
                    if cancel:
                        st.session_state.pop(ekey, None)
                        st.rerun()


# ── Router ─────────────────────────────────────────────────────────────────────

page = st.session_state.page
if page == "categories":
    categories_page()
elif page == "sub_categories":
    sub_categories_page()
elif page == "service_types":
    service_types_page()
