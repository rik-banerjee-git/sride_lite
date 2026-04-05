"""
🚖 RideWave v2 — Mobile-First Cab Booking / Ride Sharing System
Run: streamlit run app.py
"""

import streamlit as st
import json, hashlib, os, time
from datetime import datetime, date, timedelta

# ─────────────────────────────────────────────
# PAGE CONFIG — sidebar collapsed by default
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RideWave 🚖",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    -webkit-tap-highlight-color: transparent;
}}
.stApp {{
    background: linear-gradient(135deg, {dk} 0%, #1a1446 60%, #0d1b3e 100%);
    min-height: 100vh;
}}

/* Hide all Streamlit chrome including sidebar toggle */
#MainMenu, footer, header,
[data-testid="collapsedControl"],
[data-testid="stSidebarNav"],
section[data-testid="stSidebar"] {{
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
}}

/* Full-width content, padded bottom for nav bar */
.main .block-container {{
    max-width: 680px !important;
    margin: 0 auto !important;
    padding: 0 0.8rem 5.5rem 0.8rem !important;
}}

/* ── TOP APP BAR ── */
.top-bar {{
    background: linear-gradient(90deg,{dk}f0,#12123af0);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding: 0.65rem 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0 -0.8rem 1rem -0.8rem;
    position: sticky;
    top: 0;
    z-index: 999;
}}
.top-bar-brand {{
    font-family: 'Sora', sans-serif;
    font-size: 1.2rem;
    font-weight: 800;
    background: linear-gradient(90deg,{p},{s});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.top-bar-user {{
    text-align: right;
    line-height: 1.3;
}}
.top-bar-user .uid {{
    color: #f1f5f9;
    font-weight: 700;
    font-size: 0.82rem;
    display: block;
}}
.top-bar-user .role {{
    color: {s};
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}}

/* ── STAT CARDS — always 4 in a row ── */
.stats-row {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.45rem;
    margin-bottom: 1rem;
}}
.stat-card {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 0.6rem 0.25rem;
    text-align: center;
}}
.stat-num {{
    font-family: 'Sora', sans-serif;
    font-size: 1.45rem;
    font-weight: 800;
    background: linear-gradient(90deg,{p},{s});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}}
.stat-label {{
    color: rgba(255,255,255,0.3);
    font-size: 0.56rem;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-top: 2px;
}}

/* ── RIDE CARDS ── */
.ride-card {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 0.95rem 1rem;
    margin-bottom: 0.8rem;
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
}}
.ride-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg,{p},{s});
    border-radius: 16px 16px 0 0;
    opacity: 0;
}}
.ride-card-mine   {{ border-color: rgba(99,102,241,0.4); background: rgba(99,102,241,0.07); }}
.ride-card-mine::before   {{ opacity: 1; background: linear-gradient(90deg,#6366f1,#a78bfa); }}
.ride-card-booked {{ border-color: rgba(16,185,129,0.35); background: rgba(16,185,129,0.06); }}
.ride-card-booked::before {{ opacity: 1; background: linear-gradient(90deg,#10b981,#34d399); }}
.ride-card-full   {{ opacity: 0.6; }}

.route-text {{
    font-family: 'Sora', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #f1f5f9;
}}
.meta-row {{
    color: rgba(255,255,255,0.45);
    font-size: 0.74rem;
    margin-top: 0.3rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem 0.7rem;
}}
.notes-text {{
    color: rgba(255,255,255,0.42);
    font-size: 0.73rem;
    font-style: italic;
    margin-top: 0.25rem;
}}
.price-tag {{
    font-family: 'Sora', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    background: linear-gradient(90deg,{p},{s});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.countdown {{
    display: inline-block;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    padding: 1px 7px;
    font-size: 0.67rem;
    color: {ac};
    font-weight: 600;
    margin-top: 0.2rem;
}}

/* ── BADGES ── */
.badge {{
    display: inline-block;
    padding: 2px 7px;
    border-radius: 20px;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    margin-right: 3px;
}}
.badge-available {{ background:rgba(16,185,129,0.2);  color:#34d399; border:1px solid rgba(16,185,129,0.3); }}
.badge-full      {{ background:rgba(239,68,68,0.2);   color:#f87171; border:1px solid rgba(239,68,68,0.3); }}
.badge-soon      {{ background:rgba(245,158,11,0.2);  color:#fbbf24; border:1px solid rgba(245,158,11,0.3); }}
.badge-mine      {{ background:rgba(99,102,241,0.2);  color:#a78bfa; border:1px solid rgba(99,102,241,0.3); }}
.badge-booked    {{ background:rgba(16,185,129,0.2);  color:#34d399; border:1px solid rgba(16,185,129,0.3); }}
.badge-admin     {{ background:rgba(245,158,11,0.2);  color:#fbbf24; border:1px solid rgba(245,158,11,0.3); }}
.badge-history   {{ background:rgba(148,163,184,0.15);color:#94a3b8; border:1px solid rgba(148,163,184,0.2); }}
.badge-completed {{ background:rgba(16,185,129,0.15); color:#6ee7b7; border:1px solid rgba(16,185,129,0.2); }}
.badge-paid      {{ background:rgba(16,185,129,0.2);  color:#34d399; border:1px solid rgba(16,185,129,0.3); }}
.badge-unpaid    {{ background:rgba(239,68,68,0.2);   color:#f87171; border:1px solid rgba(239,68,68,0.3); }}

/* ── PAGE HEADERS ── */
.page-title {{
    font-family: 'Sora', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    color: #f1f5f9;
    margin-bottom: 0.1rem;
}}
.page-subtitle {{
    color: rgba(255,255,255,0.3);
    font-size: 0.74rem;
    margin-bottom: 0.9rem;
}}

/* ── BUTTONS ── */
.stButton > button {{
    background: linear-gradient(135deg,{p},{s}) !important;
    color: #0a0a1a !important;
    border: none !important;
    border-radius: 11px !important;
    font-weight: 700 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.8rem !important;
    padding: 0.42rem 0.5rem !important;
    min-height: 2.3rem !important;
    transition: all 0.18s !important;
}}
.stButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba({rgb_p},0.4) !important;
}}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stTimeInput > div > div > input,
.stTextArea textarea {{
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 11px !important;
    color: #f1f5f9 !important;
    font-size: 0.88rem !important;
}}
.stSelectbox > div > div {{
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 11px !important;
}}
.stTextInput label,.stNumberInput label,.stSelectbox label,
.stDateInput label,.stTimeInput label,.stTextArea label,.stRadio label {{
    color: rgba(255,255,255,0.48) !important;
    font-size: 0.73rem !important;
}}

/* ── ALERTS ── */
.stSuccess {{ background:rgba(16,185,129,0.15)!important; border:1px solid rgba(16,185,129,0.3)!important; border-radius:11px!important; color:#34d399!important; }}
.stError   {{ background:rgba(239,68,68,0.15)!important;  border:1px solid rgba(239,68,68,0.3)!important;  border-radius:11px!important; color:#f87171!important; }}
.stInfo    {{ background:rgba(99,102,241,0.15)!important; border:1px solid rgba(99,102,241,0.3)!important; border-radius:11px!important; }}
.stWarning {{ background:rgba(245,158,11,0.15)!important; border:1px solid rgba(245,158,11,0.3)!important; border-radius:11px!important; }}

/* ── EXPANDERS & TABS ── */
[data-testid="stExpander"] {{
    background: rgba(255,255,255,0.03)!important;
    border: 1px solid rgba(255,255,255,0.08)!important;
    border-radius: 11px!important;
}}
[data-testid="stExpander"] summary {{ color: rgba(255,255,255,0.55)!important; }}
.stTabs [data-baseweb="tab-list"] {{ background:rgba(255,255,255,0.04); border-radius:11px; padding:3px; }}
.stTabs [data-baseweb="tab"] {{ color:rgba(255,255,255,0.42)!important; border-radius:8px; }}
.stTabs [aria-selected="true"] {{ background:rgba({rgb_p},0.18)!important; color:{s}!important; }}

/* ── DIVIDER ── */
.divider {{ border:none; border-top:1px solid rgba(255,255,255,0.07); margin:0.7rem 0; }}
::-webkit-scrollbar {{ width:3px; }}
::-webkit-scrollbar-thumb {{ background:rgba(255,255,255,0.1); border-radius:10px; }}

/* ── AUTH ── */
.auth-wrap {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 18px;
    padding: 1.4rem 1.1rem 1.1rem;
    margin-top: 0.4rem;
}}

/* ── BOTTOM NAV — the fixed bar ── */
.bnav-wrap {{
    position: fixed;
    bottom: 0; left: 0; right: 0;
    z-index: 1000;
    background: #080818;
    border-top: 1px solid rgba(255,255,255,0.1);
    display: flex;
    padding: 0;
}}
.bnav-item {{
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0.45rem 0 0.55rem;
    cursor: pointer;
    color: rgba(255,255,255,0.32);
    font-size: 0.58rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    gap: 2px;
    border: none;
    background: transparent;
    transition: color 0.15s;
}}
.bnav-item .ni {{ font-size: 1.25rem; line-height: 1; }}
.bnav-item.active {{ color: {p}; }}
.bnav-item.active .ni {{
    filter: drop-shadow(0 0 5px {p}99);
    transform: translateY(-2px);
}}
/* Hide the Streamlit buttons used as triggers */
.bnav-stbtn .stButton > button {{
    opacity: 0 !important;
    position: absolute !important;
    width: 100% !important;
    height: 100% !important;
    top: 0 !important; left: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    min-height: 0 !important;
    border-radius: 0 !important;
    cursor: pointer !important;
    z-index: 10 !important;
}}
.bnav-stbtn {{ position: relative; flex: 1; }}
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
        return False, "Wrong Admin Secret PIN."
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
    days = hrs // 24; hrs %= 24
    if days > 0:  return f"⏱ {days}d {hrs}h left"
    if hrs > 0:   return f"⏱ {hrs}h {mins}m left"
    return f"⏱ {mins}m left"

def archive_past_rides():
    rides = get_rides(); hist = get_history(); now = datetime.now()
    keep, arc = [], []
    for r in rides:
        dt = parse_dt(r)
        (arc if (dt and dt < now) else keep).append(r)
    if arc:
        hist.extend(arc); save_rides(keep); save_history(hist)

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
        return False, "You already posted this exact ride."
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
            return False, "Booking not found."
    return False, "Ride not found."

def delete_ride(ride_id):
    rides = get_rides()
    new = [r for r in rides if r["id"] != ride_id]
    if len(new) == len(rides):
        return False, "Ride not found."
    save_rides(new)
    return True, "Ride deleted."

def move_to_history(ride_id):
    rides = get_rides(); hist = get_history()
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
            r["date"] = new_date; r["time"] = new_time; r["datetime"] = dt_str
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
# TOP BAR
# ─────────────────────────────────────────────

def render_top_bar():
    role_icon = "🛡️" if st.session_state.role == "admin" else "👤"
    role_lbl  = st.session_state.role.capitalize()
    st.markdown(
        '<div class="top-bar">'
        '<div class="top-bar-brand">🚖 RideWave</div>'
        '<div class="top-bar-user">'
        '<span class="uid">' + st.session_state.user_id + '</span>'
        '<span class="role">' + role_icon + ' ' + role_lbl + '</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
# BOTTOM NAV BAR
# ─────────────────────────────────────────────

def render_bottom_nav():
    current  = st.session_state.page
    is_admin = st.session_state.role == "admin"

    nav_items = [
        ("dashboard", "🗺️", "Home"),
        ("post_ride", "➕", "Post"),
        ("history",   "📜", "History"),
    ]
    if is_admin:
        nav_items.append(("admin", "🛡️", "Admin"))
    nav_items.append(("logout", "🚪", "Logout"))

    # Build the visual HTML bar
    bar_html = '<div class="bnav-wrap">'
    for page_key, icon, label in nav_items:
        active = "active" if current == page_key else ""
        bar_html += (
            '<div class="bnav-item ' + active + '">'
            '<span class="ni">' + icon + '</span>'
            '<span>' + label + '</span>'
            '</div>'
        )
    bar_html += '</div>'
    st.markdown(bar_html, unsafe_allow_html=True)

    # Invisible Streamlit buttons overlaid on each nav slot
    cols = st.columns(len(nav_items))
    for i, (page_key, icon, label) in enumerate(nav_items):
        with cols[i]:
            st.markdown('<div class="bnav-stbtn">', unsafe_allow_html=True)
            if st.button(label, key=f"bnav_{page_key}"):
                if page_key == "logout":
                    st.session_state.logged_in = False
                    st.session_state.user_id   = ""
                    st.session_state.role      = "user"
                    st.session_state.page      = "auth"
                else:
                    st.session_state.page = page_key
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# AUTH PAGE
# ─────────────────────────────────────────────

def page_auth():
    st.markdown("""
    <div style="text-align:center;padding:2.2rem 0 1.5rem;">
        <div style="font-size:3.2rem;">🚖</div>
        <div style="font-family:'Sora',sans-serif;font-size:2rem;font-weight:800;
            background:linear-gradient(90deg,#f7971e,#ffd200);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-top:0.2rem;">
            RideWave
        </div>
        <div style="color:rgba(255,255,255,0.25);font-size:0.68rem;letter-spacing:2px;margin-top:6px;">
            SHARE A RIDE · SAVE THE WORLD
        </div>
    </div>""", unsafe_allow_html=True)

    t1, t2 = st.tabs(["  🔑 Login  ", "  📝 Sign Up  "])

    with t1:
        st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)
        uid = st.text_input("User ID", placeholder="your_username", key="l_uid")
        pin = st.text_input("4-Digit PIN", type="password", max_chars=4, key="l_pin")
        if st.button("Sign In →", use_container_width=True, key="do_login"):
            if not uid or not pin:
                st.error("Fill in all fields.")
            else:
                ok, result = verify_login(uid.strip(), pin.strip())
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.user_id   = uid.strip()
                    st.session_state.role      = result
                    st.session_state.page      = "dashboard"
                    st.rerun()
                else:
                    st.error(result)
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

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
    if is_mine:       card_cls += " ride-card-mine"
    elif is_booked:   card_cls += " ride-card-booked"
    elif is_full:     card_cls += " ride-card-full"

    badges = ""
    if is_full:       badges += '<span class="badge badge-full">🔴 Full</span>'
    elif is_soon:     badges += '<span class="badge badge-soon">🟡 Soon</span>'
    else:             badges += '<span class="badge badge-available">🟢 Open</span>'
    if is_mine:       badges += '<span class="badge badge-mine">⭐ Mine</span>'
    if is_booked:     badges += '<span class="badge badge-booked">✅ Booked</span>'

    notes_html  = '<div class="notes-text">📝 ' + r["notes"] + '</div>' if r.get("notes") else ""
    ctdown      = countdown_str(r)
    ctdown_html = '<div class="countdown">' + ctdown + '</div>' if ctdown else ""
    price_str   = "₹" + f"{r['price']:.0f}"
    seats_str   = str(r['available_seats']) + "/" + str(r['total_seats']) + " seats"

    card_html = (
        '<div class="' + card_cls + '">'
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;">'
        '<div style="flex:1;min-width:0;">'
        '<div class="route-text">🚗 ' + r['start'] + ' → ' + r['destination'] + '</div>'
        '<div class="meta-row">'
        '<span>📅 ' + r.get('date','?') + '</span>'
        '<span>⏰ ' + r.get('time','') + '</span>'
        '<span>💺 ' + seats_str + '</span>'
        '<span>👤 ' + r['creator'] + '</span>'
        '</div>'
        + notes_html
        + '<div style="margin-top:0.35rem;">' + badges + '</div>'
        + ctdown_html
        + '</div>'
        '<div style="text-align:right;flex-shrink:0;">'
        '<div class="price-tag">' + price_str + '</div>'
        '<div style="color:rgba(255,255,255,0.22);font-size:0.6rem;margin-top:1px;">/seat</div>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    # ── Booking inputs ──
    paid_sel = "Unpaid"
    bnote    = ""
    if not is_mine and not is_booked and not is_full:
        bi1, bi2 = st.columns([1, 2])
        with bi1:
            paid_sel = st.selectbox("Pay?", ["Unpaid", "Paid"],
                                    key=f"paid_{r['id']}", label_visibility="collapsed")
        with bi2:
            bnote = st.text_input("Note", placeholder="Any note…",
                                  key=f"bn_{r['id']}", label_visibility="collapsed")

    # ── Determine which buttons to show ──
    btns = []
    if not is_mine and not is_booked and not is_full:
        btns.append("book")
    if is_booked:
        btns.append("cancel")
        my_bk = next((b for b in r["booked_users"] if b["user_id"] == user_id), None)
        if my_bk and not my_bk["paid"]:
            btns.append("markpaid")
    if is_mine:
        btns.append("complete")
    if is_mine or show_admin:
        btns.append("delete")

    if btns:
        bcols = st.columns(len(btns))
        for i, btype in enumerate(btns):
            with bcols[i]:
                if btype == "book":
                    if st.button("🚖 Book", key=f"bk_{r['id']}", use_container_width=True):
                        ok, msg = book_ride(r["id"], user_id, paid_sel == "Paid", bnote)
                        if ok: st.success(msg)
                        else:  st.error(msg)
                        st.rerun()
                elif btype == "cancel":
                    if st.button("❌ Cancel", key=f"can_{r['id']}", use_container_width=True):
                        ok, msg = cancel_booking(r["id"], user_id)
                        if ok: st.success(msg)
                        else:  st.error(msg)
                        st.rerun()
                elif btype == "markpaid":
                    if st.button("💳 Paid", key=f"mkp_{r['id']}", use_container_width=True):
                        ok, msg = mark_payment_paid(r["id"], user_id)
                        if ok: st.success(msg)
                        else:  st.error(msg)
                        st.rerun()
                elif btype == "complete":
                    if st.button("✅ Done", key=f"comp_{r['id']}", use_container_width=True):
                        ok, msg = move_to_history(r["id"])
                        if ok: st.success(msg)
                        else:  st.error(msg)
                        st.rerun()
                elif btype == "delete":
                    if st.button("🗑️ Del", key=f"del_{r['id']}", use_container_width=True):
                        ok, msg = delete_ride(r["id"])
                        if ok: st.success(msg)
                        else:  st.error(msg)
                        st.rerun()

    # ── My Booking Status (for booker) ──
    if is_booked:
        my_bk = next((b for b in r["booked_users"] if b["user_id"] == user_id), None)
        if my_bk:
            paid_txt = "✅ Paid" if my_bk["paid"] else "⏳ Unpaid — tap 💳 Paid above"
            note_txt = my_bk.get("note") or "—"
            st.markdown(
                '<div style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);'
                'border-radius:11px;padding:0.55rem 0.85rem;margin-top:0.4rem;">'
                '<div style="font-size:0.62rem;color:rgba(255,255,255,0.32);text-transform:uppercase;'
                'letter-spacing:1px;margin-bottom:0.25rem;">My Booking</div>'
                '<div style="display:flex;gap:1.2rem;flex-wrap:wrap;">'
                '<div><span style="color:rgba(255,255,255,0.35);font-size:0.7rem;">Payment</span><br>'
                '<span style="color:#f1f5f9;font-size:0.8rem;font-weight:600;">' + paid_txt + '</span></div>'
                '<div><span style="color:rgba(255,255,255,0.35);font-size:0.7rem;">Note</span><br>'
                '<span style="color:#f1f5f9;font-size:0.8rem;font-style:italic;">' + note_txt + '</span></div>'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )

    # ── Reschedule / Edit ──
    if is_mine or show_admin:
        with st.expander("🔄 Reschedule / Edit"):
            rc1, rc2 = st.columns(2)
            with rc1:
                nd = st.date_input("New Date", value=date.fromisoformat(r["date"]), key=f"nd_{r['id']}")
            with rc2:
                import datetime as _dt
                try:    nt_def = _dt.time.fromisoformat(r.get("time","08:00"))
                except: nt_def = _dt.time(8, 0)
                nt = st.time_input("New Time", value=nt_def, key=f"nt_{r['id']}")
            if st.button("💾 Reschedule", key=f"rs_{r['id']}", use_container_width=True):
                ok, msg = reschedule_ride(r["id"], str(nd), nt.strftime("%H:%M"))
                if ok: st.success(msg)
                else:  st.error(msg)
                st.rerun()
            if show_admin:
                ea1, ea2 = st.columns(2)
                with ea1:
                    new_price = st.number_input("Price ₹", value=float(r["price"]), min_value=0.0, key=f"ep_{r['id']}")
                with ea2:
                    new_seats = st.number_input("Seats", value=r["total_seats"], min_value=1, key=f"es_{r['id']}")
                if st.button("💾 Update", key=f"upd_{r['id']}", use_container_width=True):
                    diff = r["total_seats"] - r["available_seats"]
                    ok, msg = update_ride(r["id"], price=new_price, total_seats=new_seats,
                                          available_seats=max(0, new_seats - diff))
                    if ok: st.success(msg)
                    else:  st.error(msg)
                    st.rerun()

    # ── Passenger Panel (creator & admin) ──
    if r["booked_users"] and (is_mine or role == "admin"):
        bc    = len(r["booked_users"])
        paid_c   = sum(1 for b in r["booked_users"] if b["paid"])
        unpaid_c = bc - paid_c
        st.markdown(
            '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
            'border-radius:13px;padding:0.65rem 0.85rem;margin-top:0.45rem;">'
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.45rem;">'
            '<span style="font-family:\'Sora\',sans-serif;font-weight:700;color:#f1f5f9;font-size:0.82rem;">'
            '👥 ' + str(bc) + ' Passenger' + ('s' if bc != 1 else '') + '</span>'
            '<div>'
            '<span style="background:rgba(16,185,129,0.15);color:#34d399;border:1px solid rgba(16,185,129,0.2);'
            'border-radius:20px;padding:1px 7px;font-size:0.6rem;font-weight:700;margin-right:3px;">'
            '✅ ' + str(paid_c) + '</span>'
            '<span style="background:rgba(239,68,68,0.15);color:#f87171;border:1px solid rgba(239,68,68,0.2);'
            'border-radius:20px;padding:1px 7px;font-size:0.6rem;font-weight:700;">'
            '⏳ ' + str(unpaid_c) + '</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        for b in r["booked_users"]:
            if b["paid"]:
                pb  = '<span class="badge badge-paid">✅ Paid</span>'
                bg  = "rgba(16,185,129,0.06)"
                bdr = "rgba(16,185,129,0.18)"
            else:
                pb  = '<span class="badge badge-unpaid">⏳ Unpaid</span>'
                bg  = "rgba(239,68,68,0.05)"
                bdr = "rgba(239,68,68,0.14)"
            nv = b.get("note") or "—"
            st.markdown(
                '<div style="background:' + bg + ';border:1px solid ' + bdr + ';'
                'border-radius:9px;padding:0.4rem 0.7rem;margin-bottom:0.28rem;'
                'display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.3rem;">'
                '<div style="display:flex;align-items:center;gap:0.4rem;">'
                '<span style="color:#f1f5f9;font-weight:700;font-size:0.8rem;">👤 ' + b['user_id'] + '</span>'
                + pb + '</div>'
                '<span style="color:rgba(255,255,255,0.38);font-size:0.7rem;font-style:italic;">📝 ' + nv + '</span>'
                '</div>',
                unsafe_allow_html=True
            )
            if role == "admin":
                _, rc2 = st.columns([4, 1])
                with rc2:
                    if st.button("Remove", key=f"rm_{r['id']}_{b['user_id']}", use_container_width=True):
                        ok, msg = remove_user_from_ride(r["id"], b["user_id"])
                        if ok: st.success(msg)
                        else:  st.error(msg)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

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
    st.markdown('<div class="page-subtitle">Hello, ' + uid + '! All active rides below.</div>', unsafe_allow_html=True)

    total  = len(rides)
    avail  = sum(1 for r in rides if r["available_seats"] > 0)
    mine   = sum(1 for r in rides if r["creator"] == uid)
    mybk   = sum(1 for r in rides if any(b["user_id"] == uid for b in r["booked_users"]))

    st.markdown(
        '<div class="stats-row">'
        '<div class="stat-card"><div class="stat-num">' + str(total) + '</div><div class="stat-label">Rides</div></div>'
        '<div class="stat-card"><div class="stat-num">' + str(avail) + '</div><div class="stat-label">Open</div></div>'
        '<div class="stat-card"><div class="stat-num">' + str(mine)  + '</div><div class="stat-label">Mine</div></div>'
        '<div class="stat-card"><div class="stat-num">' + str(mybk)  + '</div><div class="stat-label">Booked</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

    srch = st.text_input("🔍 Search location", placeholder="e.g. Kolkata…", key="srch")
    fc1, fc2 = st.columns(2)
    with fc1: ft = st.selectbox("When",   ["All","Today","Upcoming"], key="ft")
    with fc2: fs = st.selectbox("Status", ["All","Available","My Rides","Booked by Me"], key="fs")

    filtered = rides
    if srch.strip():
        q = srch.strip().lower()
        filtered = [r for r in filtered if q in r["start"].lower() or q in r["destination"].lower()]
    if ft == "Today":    filtered = [r for r in filtered if r.get("date") == today]
    elif ft == "Upcoming": filtered = [r for r in filtered if r.get("date","") > today]
    if fs == "Available":      filtered = [r for r in filtered if r["available_seats"] > 0]
    elif fs == "My Rides":     filtered = [r for r in filtered if r["creator"] == uid]
    elif fs == "Booked by Me": filtered = [r for r in filtered if any(b["user_id"]==uid for b in r["booked_users"])]
    filtered.sort(key=lambda r: r.get("datetime",""))

    if not filtered:
        st.markdown(
            '<div style="text-align:center;padding:3rem 1rem;color:rgba(255,255,255,0.2);">'
            '<div style="font-size:2.5rem;margin-bottom:0.5rem;">🚗</div>'
            '<div style="font-size:0.88rem;">No rides found. Post one!</div>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        for r in filtered:
            render_card(r, uid, role, show_admin=(role=="admin"))

# ─────────────────────────────────────────────
# POST RIDE
# ─────────────────────────────────────────────

def page_post_ride():
    st.markdown('<div class="page-title">➕ Post a Ride</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Share your journey and earn while you travel.</div>', unsafe_allow_html=True)

    start = st.text_input("📍 Start Location", placeholder="e.g. Kolkata")
    dest  = st.text_input("🏁 Destination",    placeholder="e.g. Durgapur")
    c1, c2 = st.columns(2)
    with c1: ride_date = st.date_input("📅 Date", min_value=date.today())
    with c2: ride_time = st.time_input("⏰ Time")
    c3, c4 = st.columns(2)
    with c3: seats = st.number_input("💺 Seats", min_value=1, max_value=20, value=2)
    with c4: price = st.number_input("💰 ₹/Seat", min_value=0.0, value=100.0, step=10.0)
    notes = st.text_area("📝 Notes (optional)", placeholder="AC car, leaving sharp on time…", max_chars=200)

    if st.button("🚖 Post Ride", use_container_width=True):
        ok, msg = create_ride(
            st.session_state.user_id,
            str(ride_date), ride_time.strftime("%H:%M"),
            start, dest, seats, price, notes
        )
        if ok: st.success(msg)
        else:  st.error(msg)

# ─────────────────────────────────────────────
# HISTORY
# ─────────────────────────────────────────────

def page_history():
    archive_past_rides()
    history = get_history()
    uid  = st.session_state.user_id
    role = st.session_state.role

    st.markdown('<div class="page-title">📜 History</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Completed and archived rides.</div>', unsafe_allow_html=True)

    if not history:
        st.info("No past rides yet.")
        return

    for r in sorted(history, key=lambda x: x.get("date",""), reverse=True):
        bc = len(r.get("booked_users",[]))
        nh = '<div class="notes-text">📝 ' + r["notes"] + '</div>' if r.get("notes") else ""
        st.markdown(
            '<div class="ride-card">'
            '<div style="display:flex;justify-content:space-between;gap:0.5rem;">'
            '<div style="flex:1;min-width:0;">'
            '<div class="route-text">🚗 ' + r['start'] + ' → ' + r['destination'] + '</div>'
            '<div class="meta-row">'
            '<span>📅 ' + r.get('date','?') + '</span>'
            '<span>⏰ ' + r.get('time','') + '</span>'
            '<span>👤 ' + r['creator'] + '</span>'
            '<span>👥 ' + str(bc) + '</span>'
            '</div>'
            + nh
            + '<div style="margin-top:0.3rem;"><span class="badge badge-completed">✅ Done</span></div>'
            '</div>'
            '<div style="text-align:right;flex-shrink:0;">'
            '<div class="price-tag">₹' + f"{r['price']:.0f}" + '</div>'
            '</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        if r.get("booked_users") and (r["creator"] == uid or role == "admin"):
            with st.expander(f"👥 {bc} passengers"):
                for b in r["booked_users"]:
                    ps = "✅ Paid" if b.get("paid") else "⏳ Unpaid"
                    np = " · _" + b['note'] + "_" if b.get("note") else ""
                    st.markdown(f"- **{b['user_id']}** · {ps}{np}")

# ─────────────────────────────────────────────
# ADMIN PANEL
# ─────────────────────────────────────────────

def page_admin():
    if st.session_state.role != "admin":
        st.error("Access denied.")
        return

    st.markdown('<div class="page-title">🛡️ Admin Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Full control over rides, users, and settings.</div>', unsafe_allow_html=True)

    rides   = get_rides()
    history = get_history()
    users   = get_users()

    t1, t2, t3, t4 = st.tabs(["🚖 Rides", "📜 History", "👤 Users", "🎨 Theme"])

    with t1:
        if not rides:
            st.info("No active rides.")
        else:
            for r in sorted(rides, key=lambda x: x.get("datetime","")):
                render_card(r, st.session_state.user_id, "admin", show_admin=True)
                with st.expander("📦 Archive this ride"):
                    if st.button("Move to History", key=f"arch_{r['id']}", use_container_width=True):
                        ok, msg = move_to_history(r["id"])
                        if ok: st.success(msg)
                        else:  st.error(msg)
                        st.rerun()

    with t2:
        if not history:
            st.info("No history yet.")
        else:
            for r in sorted(history, key=lambda x: x.get("date",""), reverse=True):
                st.markdown(
                    '<div class="ride-card">'
                    '<div class="route-text">🚗 ' + r['start'] + ' → ' + r['destination'] + '</div>'
                    '<div class="meta-row">'
                    '<span>📅 ' + r.get('date','?') + '</span>'
                    '<span>⏰ ' + r.get('time','') + '</span>'
                    '<span>👤 ' + r['creator'] + '</span>'
                    '<span>👥 ' + str(len(r.get('booked_users',[]))) + '</span>'
                    '<span class="price-tag" style="font-size:0.9rem;">₹' + f"{r['price']:.0f}" + '</span>'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

    with t3:
        st.markdown(f"**{len(users)} registered users**")
        for u in users:
            rb = "🛡️ Admin" if u["role"] == "admin" else "👤 User"
            bc = "badge-admin" if u["role"] == "admin" else "badge-history"
            st.markdown(
                '<div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:0.5rem 0.85rem;'
                'margin-bottom:0.3rem;border:1px solid rgba(255,255,255,0.07);">'
                '<span style="color:#f1f5f9;font-weight:600;">' + u['user_id'] + '</span>'
                ' <span class="badge ' + bc + '">' + rb + '</span>'
                '</div>',
                unsafe_allow_html=True
            )

    with t4:
        st.markdown("**Color theme:**")
        cfg     = get_config()
        current = cfg.get("theme","Amber (Default)")
        choice  = st.selectbox("Theme", list(THEMES.keys()),
                               index=list(THEMES.keys()).index(current), key="theme_sel")
        sw = ""
        for name, colors in THEMES.items():
            pc, sc = colors["primary"], colors["secondary"]
            ast = "border:2px solid white;" if name == choice else ""
            sw += ('<span style="display:inline-block;margin:3px;padding:4px 11px;border-radius:20px;'
                   + ast + 'background:linear-gradient(90deg,' + pc + ',' + sc + ');'
                   'color:#000;font-size:0.7rem;font-weight:700;">' + name + '</span>')
        st.markdown(sw, unsafe_allow_html=True)
        if st.button("💾 Apply Theme", use_container_width=True, key="apply_theme"):
            cfg["theme"] = choice
            save_config(cfg)
            st.success(f"✅ Theme '{choice}' applied — refresh to see changes!")
            st.rerun()

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    if not get_user("admin"):
        register_user("admin", "0000", "admin", ADMIN_SECRET)

    theme, _ = get_theme()
    inject_css(theme)

    if not st.session_state.logged_in:
        page_auth()
        return

    render_top_bar()

    p = st.session_state.page
    if p == "dashboard":   page_dashboard()
    elif p == "post_ride": page_post_ride()
    elif p == "history":   page_history()
    elif p == "admin":     page_admin()
    else:                  page_dashboard()

    render_bottom_nav()

if __name__ == "__main__":
    main()
