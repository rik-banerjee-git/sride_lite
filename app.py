"""
🚖 RideWave v2 — Advanced Cab Booking / Ride Sharing System
Production-ready, mobile-first Streamlit app
Run: streamlit run app.py
"""

import streamlit as st
import json, hashlib, os, time
from datetime import datetime, date, timedelta

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="RideWave 🚖", page_icon="🚖", layout="wide",
                   initial_sidebar_state="expanded")

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
USERS_FILE    = "users.json"
BOOKINGS_FILE = "active_bookings.json"
HISTORY_FILE  = "history.json"
CONFIG_FILE   = "config.json"
ADMIN_SECRET  = "9090"

THEMES = {
    "Amber (Default)": {"primary":"#f7971e","secondary":"#ffd200","accent":"#ff6b35","dark":"#0f0c29"},
    "Violet":          {"primary":"#7c3aed","secondary":"#a78bfa","accent":"#c4b5fd","dark":"#0d0620"},
    "Emerald":         {"primary":"#059669","secondary":"#34d399","accent":"#6ee7b7","dark":"#022c22"},
    "Rose":            {"primary":"#e11d48","secondary":"#fb7185","accent":"#fda4af","dark":"#1c0010"},
    "Sky":             {"primary":"#0284c7","secondary":"#38bdf8","accent":"#7dd3fc","dark":"#0a1628"},
}

# ─────────────────────────────────────────────
# FILE UTILITIES
# ─────────────────────────────────────────────

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default

def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    os.replace(tmp, path)

def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.strip().encode()).hexdigest()

# ─────────────────────────────────────────────
# CONFIG / THEME
# ─────────────────────────────────────────────

def get_config() -> dict:
    return load_json(CONFIG_FILE, {"theme": "Amber (Default)"})

def save_config(cfg: dict):
    save_json(CONFIG_FILE, cfg)

def get_theme():
    cfg  = get_config()
    name = cfg.get("theme", "Amber (Default)")
    return THEMES.get(name, THEMES["Amber (Default)"]), name

def _hex_rgb(h: str) -> str:
    h = h.lstrip('#')
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"

def inject_css(theme: dict):
    p, s, ac, dk = theme["primary"], theme["secondary"], theme["accent"], theme["dark"]
    rgb_p = _hex_rgb(p)
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html,body,[class*="css"]{{font-family:'DM Sans',sans-serif;}}
.stApp{{background:linear-gradient(135deg,{dk} 0%,#1a1446 60%,#0d1b3e 100%);min-height:100vh;}}
#MainMenu,footer,header{{visibility:hidden;}}
[data-testid="stSidebar"]{{background:linear-gradient(180deg,#0a0a1a,#12123a);border-right:1px solid rgba(255,255,255,0.07);}}
[data-testid="stSidebar"] *{{color:#e2e8f0!important;}}
.sidebar-brand{{font-family:'Sora',sans-serif;font-size:1.55rem;font-weight:800;
  background:linear-gradient(90deg,{p},{s});-webkit-background-clip:text;-webkit-text-fill-color:transparent;
  text-align:center;padding:1rem 0 0.2rem;letter-spacing:-0.5px;}}
.sidebar-tagline{{text-align:center;font-size:0.68rem;color:rgba(255,255,255,0.3)!important;
  margin-bottom:1.3rem;letter-spacing:2px;text-transform:uppercase;}}
.ride-card{{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.09);
  border-radius:18px;padding:1.2rem 1.4rem;margin-bottom:1rem;backdrop-filter:blur(12px);
  transition:all 0.25s ease;position:relative;overflow:hidden;}}
.ride-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,{p},{s});border-radius:18px 18px 0 0;opacity:0;transition:opacity 0.25s;}}
.ride-card:hover::before{{opacity:1;}}
.ride-card:hover{{background:rgba(255,255,255,0.08);border-color:rgba({rgb_p},0.35);
  transform:translateY(-2px);box-shadow:0 8px 32px rgba(0,0,0,0.4);}}
.ride-card-mine{{border-color:rgba(99,102,241,0.4);background:rgba(99,102,241,0.07);}}
.ride-card-mine::before{{opacity:1;background:linear-gradient(90deg,#6366f1,#a78bfa);}}
.ride-card-booked{{border-color:rgba(16,185,129,0.35);background:rgba(16,185,129,0.06);}}
.ride-card-booked::before{{opacity:1;background:linear-gradient(90deg,#10b981,#34d399);}}
.ride-card-full{{opacity:0.6;}}
.route-text{{font-family:'Sora',sans-serif;font-size:1.12rem;font-weight:700;color:#f1f5f9;letter-spacing:-0.3px;}}
.meta-row{{color:rgba(255,255,255,0.5);font-size:0.8rem;margin-top:0.4rem;}}
.meta-row span{{margin-right:0.9rem;}}
.notes-text{{color:rgba(255,255,255,0.5);font-size:0.78rem;font-style:italic;margin-top:0.3rem;}}
.price-tag{{font-family:'Sora',sans-serif;font-size:1.25rem;font-weight:800;
  background:linear-gradient(90deg,{p},{s});-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.countdown{{display:inline-block;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);
  border-radius:8px;padding:2px 8px;font-size:0.7rem;color:{ac};font-weight:600;margin-top:0.3rem;}}
.badge{{display:inline-block;padding:3px 9px;border-radius:20px;font-size:0.67rem;font-weight:700;
  letter-spacing:0.5px;text-transform:uppercase;margin-right:4px;}}
.badge-available{{background:rgba(16,185,129,0.2);color:#34d399;border:1px solid rgba(16,185,129,0.3);}}
.badge-full{{background:rgba(239,68,68,0.2);color:#f87171;border:1px solid rgba(239,68,68,0.3);}}
.badge-soon{{background:rgba(245,158,11,0.2);color:#fbbf24;border:1px solid rgba(245,158,11,0.3);}}
.badge-mine{{background:rgba(99,102,241,0.2);color:#a78bfa;border:1px solid rgba(99,102,241,0.3);}}
.badge-booked{{background:rgba(16,185,129,0.2);color:#34d399;border:1px solid rgba(16,185,129,0.3);}}
.badge-admin{{background:rgba(245,158,11,0.2);color:#fbbf24;border:1px solid rgba(245,158,11,0.3);}}
.badge-history{{background:rgba(148,163,184,0.15);color:#94a3b8;border:1px solid rgba(148,163,184,0.2);}}
.badge-completed{{background:rgba(16,185,129,0.15);color:#6ee7b7;border:1px solid rgba(16,185,129,0.2);}}
.badge-paid{{background:rgba(16,185,129,0.2);color:#34d399;border:1px solid rgba(16,185,129,0.3);}}
.badge-unpaid{{background:rgba(239,68,68,0.2);color:#f87171;border:1px solid rgba(239,68,68,0.3);}}
.page-title{{font-family:'Sora',sans-serif;font-size:1.55rem;font-weight:800;color:#f1f5f9;margin-bottom:0.2rem;}}
.page-subtitle{{color:rgba(255,255,255,0.35);font-size:0.8rem;margin-bottom:1.4rem;}}
.stat-card{{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:0.9rem;text-align:center;}}
.stat-num{{font-family:'Sora',sans-serif;font-size:1.85rem;font-weight:800;
  background:linear-gradient(90deg,{p},{s});-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.stat-label{{color:rgba(255,255,255,0.35);font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;}}
.stButton>button{{background:linear-gradient(135deg,{p},{s})!important;color:#0a0a1a!important;
  border:none!important;border-radius:12px!important;font-weight:700!important;
  font-family:'Sora',sans-serif!important;transition:all 0.2s!important;}}
.stButton>button:hover{{transform:translateY(-1px)!important;box-shadow:0 4px 20px rgba({rgb_p},0.45)!important;}}
.stTextInput>div>div>input,.stNumberInput>div>div>input,.stDateInput>div>div>input,
.stTimeInput>div>div>input,.stTextArea textarea{{
  background:rgba(255,255,255,0.06)!important;border:1px solid rgba(255,255,255,0.12)!important;
  border-radius:12px!important;color:#f1f5f9!important;}}
.stSelectbox>div>div{{background:rgba(255,255,255,0.06)!important;border:1px solid rgba(255,255,255,0.12)!important;border-radius:12px!important;}}
.stTextInput label,.stNumberInput label,.stSelectbox label,.stDateInput label,
.stTimeInput label,.stTextArea label,.stRadio label{{color:rgba(255,255,255,0.55)!important;font-size:0.78rem!important;}}
.stSuccess{{background:rgba(16,185,129,0.15)!important;border:1px solid rgba(16,185,129,0.3)!important;border-radius:12px!important;color:#34d399!important;}}
.stError{{background:rgba(239,68,68,0.15)!important;border:1px solid rgba(239,68,68,0.3)!important;border-radius:12px!important;color:#f87171!important;}}
.stInfo{{background:rgba(99,102,241,0.15)!important;border:1px solid rgba(99,102,241,0.3)!important;border-radius:12px!important;}}
.stWarning{{background:rgba(245,158,11,0.15)!important;border:1px solid rgba(245,158,11,0.3)!important;border-radius:12px!important;}}
[data-testid="stExpander"]{{background:rgba(255,255,255,0.03)!important;border:1px solid rgba(255,255,255,0.08)!important;border-radius:12px!important;}}
[data-testid="stExpander"] summary{{color:rgba(255,255,255,0.6)!important;}}
.stTabs [data-baseweb="tab-list"]{{background:rgba(255,255,255,0.04);border-radius:12px;padding:4px;}}
.stTabs [data-baseweb="tab"]{{color:rgba(255,255,255,0.42)!important;border-radius:8px;}}
.stTabs [aria-selected="true"]{{background:rgba({rgb_p},0.18)!important;color:{s}!important;}}
.divider{{border:none;border-top:1px solid rgba(255,255,255,0.07);margin:1rem 0;}}
::-webkit-scrollbar{{width:4px;}}::-webkit-scrollbar-thumb{{background:rgba(255,255,255,0.1);border-radius:10px;}}
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────────

def get_users() -> list:
    return load_json(USERS_FILE, [])

def get_user(uid):
    return next((u for u in get_users() if u["user_id"] == uid), None)

def register_user(uid, pin, role, admin_secret=""):
    if not uid.strip():
        return False, "User ID cannot be empty."
    if not pin.isdigit() or len(pin) != 4:
        return False, "PIN must be exactly 4 digits."
    if role == "admin" and admin_secret != ADMIN_SECRET:
        return False, "Wrong Admin Secret PIN. Registration rejected."
    users = get_users()
    if any(u["user_id"] == uid for u in users):
        return False, "User ID already taken."
    users.append({"user_id": uid, "hashed_pin": hash_pin(pin), "role": role})
    save_json(USERS_FILE, users)
    return True, "Account created! Please log in."

def verify_login(uid, pin):
    u = get_user(uid)
    if not u:
        return False, "User not found."
    if u["hashed_pin"] != hash_pin(pin):
        return False, "Incorrect PIN."
    return True, u["role"]

# ─────────────────────────────────────────────
# RIDE HELPERS
# ─────────────────────────────────────────────

def get_rides() -> list:
    return load_json(BOOKINGS_FILE, [])

def save_rides(r):
    save_json(BOOKINGS_FILE, r)

def get_history() -> list:
    return load_json(HISTORY_FILE, [])

def save_history(h):
    save_json(HISTORY_FILE, h)

def gen_id() -> str:
    return f"ride_{int(time.time()*1000)}"

def parse_dt(ride):
    try:
        return datetime.fromisoformat(ride["datetime"])
    except Exception:
        return None

def countdown_str(ride) -> str:
    dt = parse_dt(ride)
    if not dt:
        return ""
    delta = dt - datetime.now()
    if delta.total_seconds() <= 0:
        return "⏳ Departed"
    total_min = int(delta.total_seconds() // 60)
    hrs, mins = divmod(total_min, 60)
    days = hrs // 24
    hrs %= 24
    if days > 0:
        return f"⏱ Starts in {days}d {hrs}h"
    if hrs > 0:
        return f"⏱ Starts in {hrs}h {mins}m"
    return f"⏱ Starts in {mins}m"

def archive_past_rides():
    rides = get_rides()
    hist = get_history()
    now = datetime.now()
    keep, arc = [], []
    for r in rides:
        dt = parse_dt(r)
        (arc if (dt and dt < now) else keep).append(r)
    if arc:
        hist.extend(arc)
        save_rides(keep)
        save_history(hist)

def is_duplicate_ride(creator, ride_date, ride_time, start, dest) -> bool:
    return any(
        r["creator"] == creator and r.get("date") == ride_date and
        r.get("time") == ride_time and
        r["start"].lower() == start.lower() and
        r["destination"].lower() == dest.lower()
        for r in get_rides()
    )

def create_ride(creator, ride_date, ride_time, start, dest, seats, price, notes):
    if not start.strip() or not dest.strip():
        return False, "Locations cannot be empty."
    if seats < 1:
        return False, "At least 1 seat required."
    if price < 0:
        return False, "Price cannot be negative."
    dt_str = f"{ride_date}T{ride_time}"
    try:
        dt = datetime.fromisoformat(dt_str)
    except Exception:
        return False, "Invalid date/time."
    if dt < datetime.now():
        return False, "Cannot create a ride in the past."
    if is_duplicate_ride(creator, ride_date, ride_time, start, dest):
        return False, "You already posted this exact ride (same route, date & time)."
    rides = get_rides()
    rides.append({
        "id": gen_id(), "creator": creator,
        "date": ride_date, "time": ride_time, "datetime": dt_str,
        "start": start.strip(), "destination": dest.strip(),
        "total_seats": seats, "available_seats": seats,
        "price": price, "notes": notes.strip(),
        "booked_users": [], "status": "active",
    })
    save_rides(rides)
    return True, "Ride posted! 🚖"

def book_ride(ride_id, user_id, paid, note):
    rides = get_rides()
    for r in rides:
        if r["id"] == ride_id:
            if r["available_seats"] <= 0:
                return False, "No seats available."
            if any(b["user_id"] == user_id for b in r["booked_users"]):
                return False, "Already booked."
            r["booked_users"].append({"user_id": user_id, "paid": paid, "note": note.strip()})
            r["available_seats"] -= 1
            save_rides(rides)
            return True, "Seat booked! ✅"
    return False, "Ride not found."

def cancel_booking(ride_id, user_id):
    rides = get_rides()
    for r in rides:
        if r["id"] == ride_id:
            before = len(r["booked_users"])
            r["booked_users"] = [b for b in r["booked_users"] if b["user_id"] != user_id]
            if len(r["booked_users"]) == before:
                return False, "Booking not found."
            r["available_seats"] += 1
            save_rides(rides)
            return True, "Booking cancelled."
    return False, "Ride not found."

def mark_payment_paid(ride_id, user_id):
    rides = get_rides()
    for r in rides:
        if r["id"] == ride_id:
            for b in r["booked_users"]:
                if b["user_id"] == user_id:
                    if b["paid"]:
                        return False, "Already marked as paid."
                    b["paid"] = True
                    save_rides(rides)
                    return True, "Payment marked as paid! ✅"
            return False, "Your booking was not found."
    return False, "Ride not found."

def delete_ride(ride_id):
    rides = get_rides()
    new = [r for r in rides if r["id"] != ride_id]
    if len(new) == len(rides):
        return False, "Ride not found."
    save_rides(new)
    return True, "Ride deleted."

def move_to_history(ride_id):
    rides = get_rides()
    hist = get_history()
    found = next((r for r in rides if r["id"] == ride_id), None)
    if not found:
        return False, "Ride not found."
    found["status"] = "completed"
    hist.append(found)
    save_rides([r for r in rides if r["id"] != ride_id])
    save_history(hist)
    return True, "Ride completed and archived."

def reschedule_ride(ride_id, new_date, new_time):
    dt_str = f"{new_date}T{new_time}"
    try:
        dt = datetime.fromisoformat(dt_str)
    except Exception:
        return False, "Invalid date/time."
    if dt < datetime.now():
        return False, "Cannot reschedule to the past."
    rides = get_rides()
    for r in rides:
        if r["id"] == ride_id:
            r["date"] = new_date
            r["time"] = new_time
            r["datetime"] = dt_str
            save_rides(rides)
            return True, "Ride rescheduled."
    return False, "Ride not found."

def update_ride(ride_id, **kwargs):
    rides = get_rides()
    for r in rides:
        if r["id"] == ride_id:
            for k, v in kwargs.items():
                r[k] = v
            save_rides(rides)
            return True, "Updated."
    return False, "Ride not found."

def remove_user_from_ride(ride_id, user_id):
    rides = get_rides()
    for r in rides:
        if r["id"] == ride_id:
            before = len(r["booked_users"])
            r["booked_users"] = [b for b in r["booked_users"] if b["user_id"] != user_id]
            if len(r["booked_users"]) == before:
                return False, "User not found in ride."
            r["available_seats"] += 1
            save_rides(rides)
            return True, f"Removed {user_id}."
    return False, "Ride not found."

# ─────────────────────────────────────────────
# SESSION INIT
# ─────────────────────────────────────────────
for k, v in [("logged_in", False), ("user_id", ""), ("role", "user"), ("page", "auth")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

def sidebar(theme_name):
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">🚖 RideWave</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-tagline">v2 · Ride Together · Save Together</div>', unsafe_allow_html=True)

        if st.session_state.logged_in:
            ri = "🛡️ Admin" if st.session_state.role == "admin" else "👤 User"
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05);border-radius:12px;padding:0.7rem 1rem;
                        margin-bottom:1rem;border:1px solid rgba(255,255,255,0.08);">
                <div style="font-size:0.7rem;color:rgba(255,255,255,0.36);">Signed in as</div>
                <div style="font-weight:700;color:#f1f5f9;">{st.session_state.user_id}</div>
                <div style="font-size:0.7rem;color:#fbbf24;margin-top:2px;">{ri}</div>
            </div>""", unsafe_allow_html=True)
            st.markdown(
                f'<div style="font-size:0.68rem;color:rgba(255,255,255,0.28);padding:0 0.3rem 0.5rem;">🎨 {theme_name}</div>',
                unsafe_allow_html=True
            )

            pages = {
                "🗺️  Dashboard": "dashboard",
                "➕  Post a Ride": "post_ride",
                "📜  History": "history"
            }
            if st.session_state.role == "admin":
                pages["🛡️  Admin Panel"] = "admin"
            for label, key in pages.items():
                if st.button(label, key=f"nav_{key}", use_container_width=True):
                    st.session_state.page = key
                    st.rerun()
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            if st.button("🚪  Logout", use_container_width=True, key="logout_btn"):
                st.session_state.logged_in = False
                st.session_state.user_id = ""
                st.session_state.role = "user"
                st.session_state.page = "auth"
                st.rerun()

# ─────────────────────────────────────────────
# AUTH PAGE
# ─────────────────────────────────────────────

def page_auth():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
        <div style="text-align:center;padding:1.5rem 0 1rem;">
            <div style="font-size:2.8rem;">🚖</div>
            <div style="font-family:'Sora',sans-serif;font-size:1.9rem;font-weight:800;
                background:linear-gradient(90deg,#f7971e,#ffd200);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">RideWave</div>
            <div style="color:rgba(255,255,255,0.3);font-size:0.76rem;letter-spacing:1.5px;margin-top:4px;">
                SHARE A RIDE · SAVE THE WORLD
            </div>
        </div>""", unsafe_allow_html=True)

        t1, t2 = st.tabs(["  🔑 Login  ", "  📝 Sign Up  "])
        with t1:
            uid = st.text_input("User ID", placeholder="your_username", key="l_uid")
            pin = st.text_input("4-Digit PIN", type="password", max_chars=4, key="l_pin")
            if st.button("Sign In →", use_container_width=True, key="do_login"):
                if not uid or not pin:
                    st.error("Fill in all fields.")
                else:
                    ok, result = verify_login(uid.strip(), pin.strip())
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.user_id = uid.strip()
                        st.session_state.role = result
                        st.session_state.page = "dashboard"
                        st.rerun()
                    else:
                        st.error(result)

        with t2:
            new_uid  = st.text_input("Choose User ID", key="r_uid")
            new_pin  = st.text_input("4-Digit PIN", type="password", max_chars=4, key="r_pin")
            new_pin2 = st.text_input("Confirm PIN",  type="password", max_chars=4, key="r_pin2")
            role_sel = st.selectbox("Role", ["User", "Admin"], key="r_role")
            sec_pin  = ""
            if role_sel == "Admin":
                sec_pin = st.text_input("Admin Secret PIN", type="password", max_chars=4, key="r_sec",
                                        help="Ask your system admin for this PIN.")
            if st.button("Create Account →", use_container_width=True, key="do_reg"):
                if new_pin != new_pin2:
                    st.error("PINs don't match.")
                else:
                    ok, msg = register_user(new_uid.strip(), new_pin.strip(), role_sel.lower(), sec_pin.strip())
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

# ─────────────────────────────────────────────
# RIDE CARD
# ─────────────────────────────────────────────

def render_card(r: dict, user_id: str, role: str, show_admin=False):
    is_mine   = r["creator"] == user_id
    is_booked = any(b["user_id"] == user_id for b in r["booked_users"])
    is_full   = r["available_seats"] <= 0
    dt        = parse_dt(r)
    now       = datetime.now()
    is_soon   = dt and timedelta(0) < (dt - now) < timedelta(hours=2)

    card_cls = "ride-card"
    if is_mine:
        card_cls += " ride-card-mine"
    elif is_booked:
        card_cls += " ride-card-booked"
    elif is_full:
        card_cls += " ride-card-full"

    # ── Build badges string safely (no nested f-strings) ──
    badges = ""
    if is_full:
        badges += '<span class="badge badge-full">🔴 Fully Booked</span>'
    elif is_soon:
        badges += '<span class="badge badge-soon">🟡 Starting Soon</span>'
    else:
        badges += '<span class="badge badge-available">🟢 Available</span>'
    if is_mine:
        badges += '<span class="badge badge-mine">⭐ Your Ride</span>'
    if is_booked:
        badges += '<span class="badge badge-booked">✅ Booked</span>'

    # ── Build optional HTML fragments before the main f-string ──
    notes_html  = ""
    if r.get("notes"):
        notes_html = '<div class="notes-text">📝 &ldquo;' + r["notes"] + '&rdquo;</div>'

    ctdown      = countdown_str(r)
    ctdown_html = ""
    if ctdown:
        ctdown_html = '<div class="countdown">' + ctdown + '</div>'

    price_str   = f"₹{r['price']:.0f}"
    seats_str   = f"{r['available_seats']}/{r['total_seats']}"

    # ── Single clean f-string — no nested quotes or expressions ──
    card_html = (
        '<div class="' + card_cls + '">'
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.5rem;">'
        '<div style="flex:1;">'
        '<div class="route-text">🚗 ' + r['start'] + ' → ' + r['destination'] + '</div>'
        '<div class="meta-row">'
        '<span>📅 ' + r.get('date', '?') + '</span>'
        '<span>⏰ ' + r.get('time', '') + '</span>'
        '<span>💺 ' + seats_str + '</span>'
        '<span>👤 ' + r['creator'] + '</span>'
        '</div>'
        + notes_html +
        '<div style="margin-top:0.5rem;">' + badges + '</div>'
        + ctdown_html +
        '</div>'
        '<div style="text-align:right;min-width:70px;">'
        '<div class="price-tag">' + price_str + '</div>'
        '<div style="color:rgba(255,255,255,0.28);font-size:0.68rem;margin-top:2px;">per seat</div>'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(card_html, unsafe_allow_html=True)

    # ── Actions ──
    cols = st.columns(6)
    ci = 0

    if not is_mine and not is_booked and not is_full:
        with cols[ci]:
            paid_sel = st.selectbox("Pay", ["Unpaid", "Paid"], key=f"paid_{r['id']}", label_visibility="collapsed")
        ci += 1
        with cols[ci]:
            bnote = st.text_input("Note", placeholder="Any note…", key=f"bn_{r['id']}", label_visibility="collapsed")
        ci += 1
        with cols[ci]:
            if st.button("Book Now", key=f"bk_{r['id']}", use_container_width=True):
                ok, msg = book_ride(r["id"], user_id, paid_sel == "Paid", bnote)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
                st.rerun()
        ci += 1

    if is_booked:
        # Find this user's booking to check payment status
        my_booking = next((b for b in r["booked_users"] if b["user_id"] == user_id), None)
        with cols[ci]:
            if st.button("❌ Cancel", key=f"can_{r['id']}", use_container_width=True):
                ok, msg = cancel_booking(r["id"], user_id)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
                st.rerun()
        ci += 1
        # Show "Mark as Paid" only if currently unpaid
        if my_booking and not my_booking["paid"]:
            with cols[ci]:
                if st.button("💳 Mark Paid", key=f"mkpaid_{r['id']}", use_container_width=True):
                    ok, msg = mark_payment_paid(r["id"], user_id)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
                    st.rerun()
            ci += 1

    if is_mine:
        with cols[ci]:
            if st.button("✅ Complete", key=f"comp_{r['id']}", use_container_width=True):
                ok, msg = move_to_history(r["id"])
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
                st.rerun()
        ci += 1

    if is_mine or show_admin:
        with cols[ci]:
            if st.button("🗑️ Delete", key=f"del_{r['id']}", use_container_width=True):
                ok, msg = delete_ride(r["id"])
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
                st.rerun()
        ci += 1

    # ── Reschedule / Edit (owner or admin) ──
    if is_mine or show_admin:
        with st.expander(f"🔄 Reschedule / Edit — {r['start']} → {r['destination']}"):
            rc1, rc2 = st.columns(2)
            with rc1:
                nd = st.date_input("New Date", value=date.fromisoformat(r["date"]), key=f"nd_{r['id']}")
            with rc2:
                import datetime as _dt
                try:
                    nt_default = _dt.time.fromisoformat(r.get("time", "08:00"))
                except Exception:
                    nt_default = _dt.time(8, 0)
                nt = st.time_input("New Time", value=nt_default, key=f"nt_{r['id']}")
            ra1, ra2 = st.columns(2)
            with ra1:
                if st.button("💾 Reschedule", key=f"rs_{r['id']}", use_container_width=True):
                    ok, msg = reschedule_ride(r["id"], str(nd), nt.strftime("%H:%M"))
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
                    st.rerun()
            if show_admin:
                with ra2:
                    new_price = st.number_input("Price ₹", value=float(r["price"]), min_value=0.0, key=f"ep_{r['id']}")
                re1, re2 = st.columns(2)
                with re1:
                    new_seats = st.number_input("Total Seats", value=r["total_seats"], min_value=1, key=f"es_{r['id']}")
                with re2:
                    if st.button("💾 Update", key=f"upd_{r['id']}", use_container_width=True):
                        diff = r["total_seats"] - r["available_seats"]
                        ok, msg = update_ride(
                            r["id"], price=new_price, total_seats=new_seats,
                            available_seats=max(0, new_seats - diff)
                        )
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
                        st.rerun()

    # ── Passengers ──
    if r["booked_users"] and (is_mine or role == "admin"):
        with st.expander(f"👥 Passengers ({len(r['booked_users'])})"):
            for b in r["booked_users"]:
                pc1, pc2, pc3, pc4 = st.columns([2, 1, 2, 1])

                pc1.markdown(
                    "<span style='color:#f1f5f9;font-weight:600;'>" + b['user_id'] + "</span>",
                    unsafe_allow_html=True
                )

                # FIX: build badge HTML without nested f-string expressions
                if b['paid']:
                    paid_badge = '<span class="badge badge-paid">✅ Paid</span>'
                else:
                    paid_badge = '<span class="badge badge-unpaid">⏳ Unpaid</span>'
                pc2.markdown(paid_badge, unsafe_allow_html=True)

                note_val = b.get('note') or '—'
                pc3.markdown(
                    "<span style='color:rgba(255,255,255,0.42);font-size:0.76rem;font-style:italic;'>" + note_val + "</span>",
                    unsafe_allow_html=True
                )

                if role == "admin":
                    with pc4:
                        if st.button("Remove", key=f"rm_{r['id']}_{b['user_id']}", use_container_width=True):
                            ok, msg = remove_user_from_ride(r["id"], b["user_id"])
                            if ok:
                                st.success(msg)
                            else:
                                st.error(msg)
                            st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

def page_dashboard():
    archive_past_rides()
    rides = get_rides()
    uid   = st.session_state.user_id
    role  = st.session_state.role
    today = date.today().isoformat()

    st.markdown('<div class="page-title">🗺️ Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">Hello, {uid}! Here are all active rides.</div>', unsafe_allow_html=True)

    sc1, sc2, sc3, sc4 = st.columns(4)
    for col, num, lbl in [
        (sc1, len(rides), "Total Rides"),
        (sc2, sum(1 for r in rides if r["available_seats"] > 0), "Available"),
        (sc3, sum(1 for r in rides if r["creator"] == uid), "My Rides"),
        (sc4, sum(1 for r in rides if any(b["user_id"] == uid for b in r["booked_users"])), "My Bookings"),
    ]:
        col.markdown(
            '<div class="stat-card"><div class="stat-num">' + str(num) + '</div>'
            '<div class="stat-label">' + lbl + '</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([2, 1, 1])
    with fc1:
        srch = st.text_input("🔍 Search location", placeholder="e.g. Kolkata…", key="srch")
    with fc2:
        ft = st.selectbox("When", ["All", "Today", "Upcoming"], key="ft")
    with fc3:
        fs = st.selectbox("Status", ["All", "Available", "My Rides", "Booked by Me"], key="fs")

    filtered = rides
    if srch.strip():
        q = srch.strip().lower()
        filtered = [r for r in filtered if q in r["start"].lower() or q in r["destination"].lower()]
    if ft == "Today":
        filtered = [r for r in filtered if r.get("date") == today]
    elif ft == "Upcoming":
        filtered = [r for r in filtered if r.get("date", "") > today]
    if fs == "Available":
        filtered = [r for r in filtered if r["available_seats"] > 0]
    elif fs == "My Rides":
        filtered = [r for r in filtered if r["creator"] == uid]
    elif fs == "Booked by Me":
        filtered = [r for r in filtered if any(b["user_id"] == uid for b in r["booked_users"])]

    filtered.sort(key=lambda r: r.get("datetime", ""))

    if not filtered:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:rgba(255,255,255,0.22);">
            <div style="font-size:2.5rem;margin-bottom:0.5rem;">🚗</div>
            <div>No rides found. Adjust filters or post a new ride!</div>
        </div>""", unsafe_allow_html=True)
    else:
        for r in filtered:
            render_card(r, uid, role, show_admin=(role == "admin"))

# ─────────────────────────────────────────────
# POST RIDE
# ─────────────────────────────────────────────

def page_post_ride():
    st.markdown('<div class="page-title">➕ Post a Ride</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Share your journey and earn while you travel.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        start     = st.text_input("📍 Start Location", placeholder="e.g. Kolkata")
        ride_date = st.date_input("📅 Date", min_value=date.today())
        seats     = st.number_input("💺 Available Seats", min_value=1, max_value=20, value=2)
    with c2:
        dest      = st.text_input("🏁 Destination", placeholder="e.g. Durgapur")
        ride_time = st.time_input("⏰ Departure Time")
        price     = st.number_input("💰 Price per Seat (₹)", min_value=0.0, value=100.0, step=10.0)

    notes = st.text_area(
        "📝 Notes (optional)",
        placeholder="e.g. Leaving sharp at departure time. AC car.",
        max_chars=200
    )

    if st.button("🚖 Post Ride", use_container_width=True):
        ok, msg = create_ride(
            st.session_state.user_id,
            str(ride_date), ride_time.strftime("%H:%M"),
            start, dest, seats, price, notes
        )
        # FIX: proper if/else, not ternary expression
        if ok:
            st.success(msg)
        else:
            st.error(msg)

# ─────────────────────────────────────────────
# HISTORY
# ─────────────────────────────────────────────

def page_history():
    archive_past_rides()
    history = get_history()
    uid  = st.session_state.user_id
    role = st.session_state.role

    st.markdown('<div class="page-title">📜 History</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">All completed and archived rides.</div>', unsafe_allow_html=True)

    if not history:
        st.info("No past rides yet.")
        return

    for r in sorted(history, key=lambda x: x.get("date", ""), reverse=True):
        bc = len(r.get("booked_users", []))
        notes_html = ""
        if r.get("notes"):
            notes_html = '<div class="notes-text">📝 &ldquo;' + r["notes"] + '&rdquo;</div>'

        hist_card = (
            '<div class="ride-card">'
            '<div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">'
            '<div>'
            '<div class="route-text">🚗 ' + r['start'] + ' → ' + r['destination'] + '</div>'
            '<div class="meta-row">'
            '<span>📅 ' + r.get('date', '?') + '</span>'
            '<span>⏰ ' + r.get('time', '') + '</span>'
            '<span>👤 ' + r['creator'] + '</span>'
            '<span>👥 ' + str(bc) + ' passengers</span>'
            '</div>'
            + notes_html +
            '<div style="margin-top:0.4rem;"><span class="badge badge-completed">✅ Completed</span></div>'
            '</div>'
            '<div style="text-align:right;">'
            '<div class="price-tag">₹' + f"{r['price']:.0f}" + '</div>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(hist_card, unsafe_allow_html=True)

        if r.get("booked_users") and (r["creator"] == uid or role == "admin"):
            with st.expander(f"👥 {bc} passengers"):
                for b in r["booked_users"]:
                    note_part = f" · _{b['note']}_" if b.get("note") else ""
                    paid_str = "✅ Paid" if b.get("paid") else "⏳ Unpaid"
                    st.markdown(f"- **{b['user_id']}** · {paid_str}{note_part}")

# ─────────────────────────────────────────────
# ADMIN PANEL
# ─────────────────────────────────────────────

def page_admin():
    if st.session_state.role != "admin":
        st.error("Access denied.")
        return

    st.markdown('<div class="page-title">🛡️ Admin Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Full control over rides, users, and app settings.</div>', unsafe_allow_html=True)

    rides   = get_rides()
    history = get_history()
    users   = get_users()

    t1, t2, t3, t4 = st.tabs(["🚖 Active Rides", "📜 History", "👤 Users", "🎨 Theme"])

    with t1:
        if not rides:
            st.info("No active rides.")
        else:
            for r in sorted(rides, key=lambda x: x.get("datetime", "")):
                render_card(r, st.session_state.user_id, "admin", show_admin=True)
                with st.expander(f"📦 Archive — {r['start']} → {r['destination']}"):
                    if st.button("Move to History", key=f"arch_{r['id']}", use_container_width=True):
                        ok, msg = move_to_history(r["id"])
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
                        st.rerun()

    with t2:
        if not history:
            st.info("No history yet.")
        else:
            for r in sorted(history, key=lambda x: x.get("date", ""), reverse=True):
                hist_admin = (
                    '<div class="ride-card">'
                    '<div class="route-text">🚗 ' + r['start'] + ' → ' + r['destination'] + '</div>'
                    '<div class="meta-row">'
                    '<span>📅 ' + r.get('date', '?') + '</span>'
                    '<span>⏰ ' + r.get('time', '') + '</span>'
                    '<span>👤 ' + r['creator'] + '</span>'
                    '<span>👥 ' + str(len(r.get('booked_users', []))) + ' passengers</span>'
                    '<span class="price-tag" style="font-size:1rem;">₹' + f"{r['price']:.0f}" + '</span>'
                    '</div>'
                    '</div>'
                )
                st.markdown(hist_admin, unsafe_allow_html=True)

    with t3:
        st.markdown(f"**Total registered users: {len(users)}**")
        for u in users:
            rb = "🛡️ Admin" if u["role"] == "admin" else "👤 User"
            bc = "badge-admin" if u["role"] == "admin" else "badge-history"
            user_html = (
                '<div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:0.6rem 1rem;'
                'margin-bottom:0.4rem;border:1px solid rgba(255,255,255,0.07);">'
                '<span style="color:#f1f5f9;font-weight:600;">' + u['user_id'] + '</span>'
                '&nbsp;<span class="badge ' + bc + '">' + rb + '</span>'
                '</div>'
            )
            st.markdown(user_html, unsafe_allow_html=True)

    with t4:
        st.markdown("**Select a color theme for the entire app:**")
        cfg     = get_config()
        current = cfg.get("theme", "Amber (Default)")
        choice  = st.selectbox(
            "Theme", list(THEMES.keys()),
            index=list(THEMES.keys()).index(current),
            key="theme_sel"
        )

        swatch_html = ""
        for name, colors in THEMES.items():
            p_c, s_c = colors["primary"], colors["secondary"]
            active_style = "border:2px solid white;" if name == choice else ""
            swatch_html += (
                '<span style="display:inline-block;margin:4px;padding:5px 14px;border-radius:20px;'
                + active_style +
                'background:linear-gradient(90deg,' + p_c + ',' + s_c + ');'
                'color:#000;font-size:0.76rem;font-weight:700;">' + name + '</span>'
            )
        st.markdown(swatch_html, unsafe_allow_html=True)

        if st.button("💾 Apply Theme", use_container_width=True, key="apply_theme"):
            cfg["theme"] = choice
            save_config(cfg)
            st.success(f"✅ Theme set to '{choice}'. Refresh the page to see the full effect!")
            st.rerun()

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    if not get_user("admin"):
        register_user("admin", "0000", "admin", ADMIN_SECRET)

    theme, theme_name = get_theme()
    inject_css(theme)
    sidebar(theme_name)

    if not st.session_state.logged_in:
        page_auth()
        return

    p = st.session_state.page
    if p == "dashboard":
        page_dashboard()
    elif p == "post_ride":
        page_post_ride()
    elif p == "history":
        page_history()
    elif p == "admin":
        page_admin()
    else:
        page_dashboard()

if __name__ == "__main__":
    main()
