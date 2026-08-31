import hashlib
import json
import sqlite3
from pathlib import Path

import streamlit as st
from PIL import Image

from database import get_connection, init_database


# ============================================================
# PAGE CONFIGURATION
# ============================================================

ASSETS_DIR = Path(__file__).parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"

_logo_icon = Image.open(LOGO_PATH) if LOGO_PATH.exists() else "🏠"

st.set_page_config(
    page_title="Pakistan Estate Hub",
    page_icon=_logo_icon,
    layout="wide"
)

init_database()


# ============================================================
# BRAND THEME (matches logo: black / gold / deep green)
# ============================================================

GOLD = "#D4AF37"
GOLD_LIGHT = "#E8C766"
DEEP_GREEN = "#123524"
DEEP_GREEN_LIGHT = "#1B4D33"
NEAR_BLACK = "#0B0B0B"
PANEL = "#12201A"
CREAM = "#F1E9D2"

st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Lato:wght@300;400;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Lato', sans-serif;
}}

/* App background */
.stApp {{
    background: radial-gradient(circle at top, {DEEP_GREEN} 0%, {NEAR_BLACK} 55%);
    color: {CREAM};
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {NEAR_BLACK} 0%, {DEEP_GREEN} 140%);
    border-right: 1px solid {GOLD};
}}
section[data-testid="stSidebar"] * {{
    color: {CREAM} !important;
}}

/* Headings */
h1, h2, h3 {{
    font-family: 'Cormorant Garamond', serif !important;
    color: {GOLD} !important;
    letter-spacing: 0.5px;
}}

/* Captions / dividers */
hr {{
    border-color: {GOLD} !important;
    opacity: 0.4;
}}

/* Buttons */
.stButton > button, .stDownloadButton > button {{
    background: linear-gradient(180deg, {GOLD_LIGHT} 0%, {GOLD} 100%);
    color: {NEAR_BLACK} !important;
    border: 1px solid {GOLD};
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s ease-in-out;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    background: linear-gradient(180deg, {GOLD} 0%, {DEEP_GREEN_LIGHT} 100%);
    color: {CREAM} !important;
    border: 1px solid {GOLD_LIGHT};
    transform: translateY(-1px);
}}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stNumberInput input,
.stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] {{
    background-color: {PANEL} !important;
    color: {CREAM} !important;
    border: 1px solid {GOLD} !important;
    border-radius: 6px !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab"] {{
    color: {CREAM};
}}
.stTabs [aria-selected="true"] {{
    color: {GOLD} !important;
    border-bottom-color: {GOLD} !important;
}}

/* Metric / cards / containers */
div[data-testid="stMetric"], div[data-testid="stExpander"] {{
    background-color: {PANEL};
    border: 1px solid {GOLD};
    border-radius: 10px;
    padding: 6px;
}}

/* Alerts */
div[data-testid="stAlert"] {{
    border-left: 4px solid {GOLD};
}}

/* Sidebar logo container */
.brand-logo-wrap {{
    display: flex;
    justify-content: center;
    padding: 6px 0 2px 0;
}}
.brand-tagline {{
    text-align: center;
    color: {GOLD};
    font-family: 'Cormorant Garamond', serif;
    letter-spacing: 2px;
    font-size: 0.85rem;
    margin-top: -8px;
    margin-bottom: 8px;
    opacity: 0.9;
}}

</style>
""", unsafe_allow_html=True)


# ============================================================
# APP DATA
# ============================================================

PROVINCES = [
    "Punjab",
    "Sindh",
    "Khyber Pakhtunkhwa",
    "Balochistan",
    "Islamabad Capital Territory",
    "Azad Jammu & Kashmir",
    "Gilgit-Baltistan"
]

CITIES = {
    "Punjab": [
        "Lahore",
        "Rawalpindi",
        "Faisalabad",
        "Multan",
        "Gujranwala",
        "Sialkot",
        "Bahawalpur",
        "Sargodha",
        "Sheikhupura",
        "Gujrat",
        "Jhelum",
        "Kasur",
        "Okara",
        "Sahiwal",
        "Rahim Yar Khan",
        "Dera Ghazi Khan"
    ],
    "Sindh": [
        "Karachi",
        "Hyderabad",
        "Sukkur",
        "Larkana",
        "Mirpur Khas",
        "Nawabshah"
    ],
    "Khyber Pakhtunkhwa": [
        "Peshawar",
        "Abbottabad",
        "Mardan",
        "Swat",
        "Kohat",
        "Bannu"
    ],
    "Balochistan": [
        "Quetta",
        "Gwadar",
        "Turbat",
        "Khuzdar",
        "Chaman"
    ],
    "Islamabad Capital Territory": [
        "Islamabad"
    ],
    "Azad Jammu & Kashmir": [
        "Muzaffarabad",
        "Mirpur",
        "Rawalakot"
    ],
    "Gilgit-Baltistan": [
        "Gilgit",
        "Skardu",
        "Hunza"
    ]
}

PROPERTY_TYPES = [
    "House",
    "Apartment / Flat",
    "Villa",
    "Portion",
    "Penthouse",
    "Residential Plot",
    "Shop",
    "Office",
    "Plaza",
    "Commercial Building",
    "Commercial Plot",
    "Warehouse",
    "Factory",
    "Industrial Building",
    "Industrial Land",
    "Farmhouse",
    "Agricultural Land",
    "Farm",
    "Orchard",
    "Open Land",
    "Development Land",
    "Mixed-Use Property",
    "Other"
]

AREA_UNITS = [
    "Marla",
    "Kanal",
    "Acre",
    "Murabba",
    "Square Feet",
    "Square Yard",
    "Square Meter"
]

FURNISHED = [
    "Not Applicable",
    "Furnished",
    "Unfurnished",
    "Semi-Furnished"
]

CONDITIONS = [
    "New",
    "Good",
    "Needs Maintenance"
]

USER_TYPES = [
    "Buyer",
    "Seller",
    "Both",
    "Landlord",
    "Tenant",
    "Agent"
]

IMAGE_FOLDER = Path(__file__).parent / "property_images"
IMAGE_FOLDER.mkdir(parents=True, exist_ok=True)


# ============================================================
# TRANSLATIONS
# ============================================================

T = {
    "English": {
        "home": "Home",
        "buy": "Buy Property",
        "rent": "Rent Property",
        "sell": "Sell / List Property",
        "wanted": "Wanted Property",
        "login": "Login",
        "register": "Register",
        "my_listings": "My Listings",
        "favourites": "Favourites",
        "profile": "My Profile",
        "logout": "Logout",
        "language": "Language / زبان",
        "title": "Pakistan Estate Hub",
        "tagline": "Buy • Sell • Rent • Find Property Across Pakistan",
        "search": "Search",
        "save": "Save",
        "property_type": "Property Type",
        "province": "Province / Region",
        "city": "City / District",
        "price": "Price / Rent (PKR)",
        "area": "Property Area",
        "area_unit": "Area Unit",
        "area_locality": "Area / Locality",
        "bedrooms": "Bedrooms",
        "bathrooms": "Bathrooms",
        "furnished": "Furnished Status",
        "condition": "Property Condition",
        "amenities": "Amenities",
        "description": "Property Description",
        "property_title": "Property Title",
        "contact_name": "Contact Name",
        "contact_mobile": "Contact Mobile",
        "purpose": "Purpose",
        "no_properties": "No properties found.",
        "found": "properties found.",
        "required": "Please complete all required fields.",
        "login_first": "Please login first.",
        "success": "Saved successfully.",
        "message": "Message",
        "send": "Send Message",
        "contact": "Contact Seller",
        "compare": "Compare",
        "add_favourite": "♡ Add Favourite",
        "remove_favourite": "❤️ Remove Favourite",
        "notifications": "Notifications",
        "messages": "Messages",
        "saved_searches": "Saved Searches",
        "reviews": "Reviews & Ratings",
        "admin": "Admin Dashboard",
        "report": "Report Listing",
        "smart": "Smart Match",
        "listing_saved": "Property listed successfully.",
        "wanted_saved": "Requirement posted successfully.",
        "update": "Update Profile",
        "delete": "Delete",
        "edit": "Edit",
        "status": "Status"
    },

    "Urdu": {
        "home": "ہوم",
        "buy": "پراپرٹی خریدیں",
        "rent": "پراپرٹی کرائے پر",
        "sell": "پراپرٹی فروخت / لسٹ کریں",
        "wanted": "مطلوبہ پراپرٹی",
        "login": "لاگ اِن",
        "register": "رجسٹریشن",
        "my_listings": "میری لسٹنگز",
        "favourites": "پسندیدہ پراپرٹیز",
        "profile": "میرا پروفائل",
        "logout": "لاگ آؤٹ",
        "language": "Language / زبان",
        "title": "پاکستان اسٹیٹ ہب",
        "tagline": "پورے پاکستان میں پراپرٹی خریدیں • فروخت کریں • کرائے پر لیں",
        "search": "تلاش کریں",
        "save": "محفوظ کریں",
        "property_type": "پراپرٹی کی قسم",
        "province": "صوبہ / علاقہ",
        "city": "شہر / ضلع",
        "price": "قیمت / کرایہ (PKR)",
        "area": "پراپرٹی کا رقبہ",
        "area_unit": "رقبے کی یونٹ",
        "area_locality": "علاقہ / لوکلٹی",
        "bedrooms": "بیڈ رومز",
        "bathrooms": "باتھ رومز",
        "furnished": "فرنشڈ اسٹیٹس",
        "condition": "پراپرٹی کی حالت",
        "amenities": "سہولیات",
        "description": "پراپرٹی کی تفصیل",
        "property_title": "پراپرٹی کا عنوان",
        "contact_name": "رابطے کا نام",
        "contact_mobile": "رابطے کا موبائل",
        "purpose": "مقصد",
        "no_properties": "کوئی پراپرٹی نہیں ملی۔",
        "found": "پراپرٹیز ملیں۔",
        "required": "براہِ کرم تمام ضروری معلومات مکمل کریں۔",
        "login_first": "براہِ کرم پہلے لاگ اِن کریں۔",
        "success": "کامیابی سے محفوظ ہوگیا۔",
        "message": "پیغام",
        "send": "پیغام بھیجیں",
        "contact": "فروخت کنندہ سے رابطہ",
        "compare": "موازنہ",
        "add_favourite": "♡ پسندیدہ میں شامل کریں",
        "remove_favourite": "❤️ پسندیدہ سے ہٹائیں",
        "notifications": "اطلاعات",
        "messages": "پیغامات",
        "saved_searches": "محفوظ سرچز",
        "reviews": "ریٹنگز اور جائزے",
        "admin": "ایڈمن ڈیش بورڈ",
        "report": "لسٹنگ رپورٹ کریں",
        "smart": "اسمارٹ میچ",
        "listing_saved": "پراپرٹی کامیابی سے لسٹ ہوگئی۔",
        "wanted_saved": "ضرورت کامیابی سے پوسٹ ہوگئی۔",
        "update": "پروفائل اپ ڈیٹ",
        "delete": "حذف کریں",
        "edit": "ترمیم",
        "status": "اسٹیٹس"
    }
}


# ============================================================
# SESSION STATE
# ============================================================

if "language" not in st.session_state:
    st.session_state.language = "English"

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "compare_ids" not in st.session_state:
    st.session_state.compare_ids = []

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "message_property_id" not in st.session_state:
    st.session_state.message_property_id = None

if "report_property_id" not in st.session_state:
    st.session_state.report_property_id = None

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def tr(key):
    return T[st.session_state.language].get(key, key)


def rows(sql, params=()):
    conn = get_connection()
    try:
        return [
            dict(r)
            for r in conn.execute(sql, params).fetchall()
        ]
    finally:
        conn.close()


def one(sql, params=()):
    conn = get_connection()
    try:
        r = conn.execute(sql, params).fetchone()
        return dict(r) if r else None
    finally:
        conn.close()


def execute(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def password_hash(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def password_matches(stored, password):
    return (
        stored == password
        or stored == password_hash(password)
    )


def notify(user_id, title, message):
    if user_id:
        execute(
            """
            INSERT INTO notifications(user_id,title,message)
            VALUES(?,?,?)
            """,
            (user_id, title, message)
        )


def login_user(mobile, password):
    user = one(
        """
        SELECT *
        FROM users
        WHERE mobile=?
        AND is_active=1
        """,
        (mobile.strip(),)
    )

    if user and password_matches(
        user["password"],
        password
    ):
        return user

    return None


def register_user(
    name,
    mobile,
    email,
    password,
    user_type,
    province,
    city
):
    try:
        uid = execute(
            """
            INSERT INTO users(
                full_name,
                mobile,
                email,
                password,
                user_type,
                province,
                city
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                name.strip(),
                mobile.strip(),
                email.strip() or None,
                password_hash(password),
                user_type,
                province,
                city
            )
        )

        return uid, None

    except sqlite3.IntegrityError:
        return None, "Mobile number or email already exists."


def save_property(data):
    return execute(
        """
        INSERT INTO properties(
            user_id,
            title,
            description,
            purpose,
            property_type,
            province,
            city,
            area_name,
            area_value,
            area_unit,
            price,
            price_period,
            bedrooms,
            bathrooms,
            furnished,
            condition,
            amenities,
            contact_name,
            contact_mobile,
            verification_status,
            listing_status,
            image_paths
        )
        VALUES(
            ?,?,?,?,?,?,?,?,?,?,
            ?,?,?,?,?,?,?,?,?,?,
            ?,?
        )
        """,
        data
    )


def search_properties(
    purpose,
    ptype,
    province,
    city,
    min_price,
    max_price,
    bedrooms=None
):
    q = """
        SELECT
            p.*,
            u.full_name AS owner_name
        FROM properties p
        LEFT JOIN users u
            ON p.user_id=u.id
        WHERE p.listing_status='Active'
        AND p.verification_status IN
            ('Pending','Verified','Unverified')
    """

    params = []

    if purpose != "All":
        q += " AND p.purpose=?"
        params.append(purpose)

    if ptype != "All":
        q += " AND p.property_type=?"
        params.append(ptype)

    if province != "All":
        q += " AND p.province=?"
        params.append(province)

    if city != "All":
        q += " AND p.city=?"
        params.append(city)

    if min_price > 0:
        q += " AND p.price>=?"
        params.append(min_price)

    if max_price > 0:
        q += " AND p.price<=?"
        params.append(max_price)

    if bedrooms is not None and bedrooms > 0:
        q += " AND p.bedrooms>=?"
        params.append(bedrooms)

    q += " ORDER BY p.created_at DESC"

    return rows(q, tuple(params))


def is_favourite(pid):
    if not st.session_state.logged_in:
        return False

    return (
        one(
            """
            SELECT id
            FROM favourites
            WHERE user_id=?
            AND property_id=?
            """,
            (
                st.session_state.user_id,
                pid
            )
        )
        is not None
    )


def toggle_favourite(pid):
    if not st.session_state.logged_in:
        return

    if is_favourite(pid):

        execute(
            """
            DELETE FROM favourites
            WHERE user_id=?
            AND property_id=?
            """,
            (
                st.session_state.user_id,
                pid
            )
        )

    else:

        execute(
            """
            INSERT OR IGNORE INTO favourites(
                user_id,
                property_id
            )
            VALUES(?,?)
            """,
            (
                st.session_state.user_id,
                pid
            )
        )

        owner = one(
            """
            SELECT user_id,title
            FROM properties
            WHERE id=?
            """,
            (pid,)
        )

        if (
            owner
            and owner["user_id"]
            != st.session_state.user_id
        ):
            notify(
                owner["user_id"],
                "New Favourite",
                f"Your property '{owner['title']}' was added to favourites."
            )


def smart_score(prop, desired):
    score = 0
    total = 0

    for field in [
        "province",
        "city",
        "property_type",
        "purpose"
    ]:

        wanted = desired.get(field)

        if wanted and wanted != "All":
            total += 25

            if prop.get(field) == wanted:
                score += 25

    if desired.get("max_price", 0) > 0:
        total += 25

        if (
            prop.get("price") or 0
        ) <= desired["max_price"]:
            score += 25

    if total == 0:
        return 0

    return round(
        score / total * 100,
        1
    )


# ============================================================
# IMAGE FUNCTIONS
# ============================================================

def save_uploaded_images(uploaded_files):
    saved_paths = []

    if not uploaded_files:
        return saved_paths

    for uploaded_file in uploaded_files:

        if uploaded_file is None:
            continue

        suffix = Path(
            uploaded_file.name
        ).suffix.lower()

        if suffix not in [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        ]:
            continue

        unique_name = (
            f"{st.session_state.user_id}_"
            f"{__import__('time').time_ns()}"
            f"{suffix}"
        )

        file_path = IMAGE_FOLDER / unique_name

        with open(file_path, "wb") as f:
            f.write(
                uploaded_file.getbuffer()
            )

        saved_paths.append(
            str(file_path)
        )

    return saved_paths


def get_property_images(p):
    raw = p.get("image_paths")

    if not raw:
        return []

    try:
        paths = json.loads(raw)

        if isinstance(paths, list):
            return [
                path
                for path in paths
                if Path(path).exists()
            ]

    except Exception:
        pass

    return []


def show_property_images(p):

    images = get_property_images(p)

    if not images:
        st.info("📷 No property pictures uploaded.")
        return

    st.markdown("### 📷 Property Pictures")

    if len(images) == 1:
        st.image(
            images[0],
            use_container_width=True
        )
        return

    cols = st.columns(
        min(len(images), 3)
    )

    for index, image_path in enumerate(images):

        with cols[index % 3]:
            st.image(
                image_path,
                use_container_width=True
            )


# ============================================================
# PROPERTY CARD
# ============================================================

def show_property_card(p):

    with st.container(border=True):

        st.subheader(
            f"🏠 {p.get('title', 'Property')}"
        )

        images = get_property_images(p)

        if images:
            st.image(
                images[0],
                use_container_width=True
            )

            if len(images) > 1:
                st.caption(
                    f"📷 {len(images)} property pictures"
                )

        st.write(
            f"**{p.get('property_type','')}** "
            f"• {p.get('purpose','')}"
        )

        st.write(
            f"📍 {p.get('city','')}, "
            f"{p.get('province','')}"
        )

        if p.get("area_value"):
            st.write(
                f"📐 {p['area_value']:g} "
                f"{p.get('area_unit','')}"
            )

        if p.get("price") is not None:
            st.write(
                f"💰 PKR {p['price']:,.0f} "
                f"• {p.get('price_period','')}"
            )

        if p.get("area_name"):
            st.write(
                f"📌 {p['area_name']}"
            )

        if (
            p.get("bedrooms", 0)
            or p.get("bathrooms", 0)
        ):
            st.write(
                f"🛏️ {p.get('bedrooms',0)} Bedrooms "
                f"• 🛁 {p.get('bathrooms',0)} Bathrooms"
            )

        if p.get("furnished"):
            st.write(
                f"🛋️ {p['furnished']}"
            )

        if p.get("condition"):
            st.write(
                f"🏗️ Condition: {p['condition']}"
            )

        if p.get("amenities"):
            st.write(
                f"✨ {p['amenities']}"
            )

        if p.get("description"):
            st.write(
                p["description"]
            )

        if p.get("owner_name"):
            st.write(
                f"👤 Listed by: {p['owner_name']}"
            )

        st.caption(
            f"Verification: "
            f"{p.get('verification_status','Pending')} "
            f"• Listing: "
            f"{p.get('listing_status','Active')}"
        )

        c1, c2, c3, c4 = st.columns(4)

        if st.session_state.logged_in:

            with c1:

                if st.button(
                    tr("remove_favourite")
                    if is_favourite(p["id"])
                    else tr("add_favourite"),
                    key=f"fav_{p['id']}",
                    use_container_width=True
                ):
                    toggle_favourite(
                        p["id"]
                    )
                    st.rerun()

            with c2:

                if st.button(
                    tr("contact"),
                    key=f"contact_{p['id']}",
                    use_container_width=True
                ):
                    st.session_state.message_property_id = p["id"]
                    st.session_state.page = "Messages"
                    st.rerun()

            with c3:

                selected = (
                    p["id"]
                    in st.session_state.compare_ids
                )

                if st.button(
                    (
                        "✓ "
                        if selected
                        else ""
                    )
                    + tr("compare"),
                    key=f"cmp_{p['id']}",
                    use_container_width=True
                ):

                    if selected:

                        st.session_state.compare_ids.remove(
                            p["id"]
                        )

                    elif (
                        len(
                            st.session_state.compare_ids
                        ) < 3
                    ):

                        st.session_state.compare_ids.append(
                            p["id"]
                        )

                    else:
                        st.warning(
                            "Compare limit is 3 properties."
                        )

                    st.rerun()

            with c4:

                if st.button(
                    "🚩 " + tr("report"),
                    key=f"report_{p['id']}",
                    use_container_width=True
                ):

                    st.session_state.report_property_id = p["id"]
                    st.session_state.page = "Report"
                    st.rerun()

        if st.button(
            "🖼️ View All Pictures",
            key=f"images_{p['id']}",
            use_container_width=True
        ):
            show_property_images(p)


# ============================================================
# SEARCH PAGE
# ============================================================

def property_search_page(mode):

    st.header(
        "🏠 "
        + (
            tr("buy")
            if mode == "Buy"
            else tr("rent")
        )
    )

    ptype = st.selectbox(
        tr("property_type"),
        ["All"] + PROPERTY_TYPES,
        key=f"{mode}_type"
    )

    province = st.selectbox(
        tr("province"),
        ["All"] + PROVINCES,
        key=f"{mode}_province"
    )

    if province == "All":

        city_options = [
            "All"
        ] + sum(
            CITIES.values(),
            []
        )

    else:

        city_options = [
            "All"
        ] + CITIES.get(
            province,
            []
        )

    city = st.selectbox(
        tr("city"),
        city_options,
        key=f"{mode}_city"
    )

    c1, c2 = st.columns(2)

    with c1:

        min_price = st.number_input(
            "Minimum Price/Budget (PKR)",
            min_value=0.0,
            step=100000.0,
            key=f"{mode}_min"
        )

    with c2:

        max_price = st.number_input(
            "Maximum Price/Budget (PKR)",
            min_value=0.0,
            step=100000.0,
            key=f"{mode}_max"
        )

    beds = st.number_input(
        tr("bedrooms"),
        min_value=0,
        max_value=20,
        step=1,
        key=f"{mode}_beds"
    )

    if st.button(
        "🔎 " + tr("search"),
        use_container_width=True,
        key=f"search_{mode}"
    ):

        results = search_properties(
            "For Sale"
            if mode == "Buy"
            else "For Rent",
            ptype,
            province,
            city,
            min_price,
            max_price,
            beds
        )

        st.session_state.search_results = results

    results = st.session_state.get(
        "search_results",
        []
    )

    if results:

        st.success(
            f"{len(results)} "
            f"{tr('found')}"
        )

        for p in results:
            show_property_card(p)

    else:

        st.info(
            tr("no_properties")
        )


# ============================================================
# SIDEBAR
# ============================================================

if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), use_container_width=True)
else:
    st.sidebar.title("🏠 " + tr("title"))

st.sidebar.markdown(
    f"<div class='brand-tagline'>BUY · RENT · SELL · INVEST</div>",
    unsafe_allow_html=True
)

lang = st.sidebar.selectbox(
    tr("language"),
    ["English", "Urdu"],
    index=(
        0
        if st.session_state.language
        == "English"
        else 1
    )
)

if lang != st.session_state.language:
    st.session_state.language = lang
    st.rerun()

st.sidebar.divider()

navigation = [
    (
        tr("home"),
        "Home",
        "🏠"
    ),
    (
        tr("buy"),
        "Buy",
        "🏡"
    ),
    (
        tr("rent"),
        "Rent",
        "🏢"
    ),
    (
        tr("sell"),
        "Sell",
        "💰"
    ),
    (
        tr("wanted"),
        "Wanted",
        "🔎"
    )
]

for label, page_name, icon in navigation:

    if st.sidebar.button(
        f"{icon} {label}",
        use_container_width=True,
        key=f"nav_{page_name}"
    ):
        st.session_state.page = page_name


if st.session_state.logged_in:

    st.sidebar.divider()

    st.sidebar.write(
        f"👤 {st.session_state.user_name}"
    )

    user_navigation = [
        (
            tr("my_listings"),
            "My Listings",
            "📋"
        ),
        (
            tr("favourites"),
            "Favourites",
            "❤️"
        ),
        (
            tr("messages"),
            "Messages",
            "💬"
        ),
        (
            tr("notifications"),
            "Notifications",
            "🔔"
        ),
        (
            tr("saved_searches"),
            "Saved Searches",
            "🔎"
        ),
        (
            tr("reviews"),
            "Reviews",
            "⭐"
        ),
        (
            tr("profile"),
            "Profile",
            "👤"
        ),
        (
            tr("compare"),
            "Compare",
            "⚖️"
        )
    ]

    for label, page_name, icon in user_navigation:

        if st.sidebar.button(
            f"{icon} {label}",
            use_container_width=True,
            key=f"user_{page_name}"
        ):
            st.session_state.page = page_name

    if st.sidebar.button(
        "🚩 Reports",
        use_container_width=True
    ):
        st.session_state.page = "Report"

    if st.sidebar.button(
        "🛡️ " + tr("admin"),
        use_container_width=True
    ):
        st.session_state.page = "Admin"

    if st.sidebar.button(
        "🚪 " + tr("logout"),
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = ""
        st.session_state.page = "Home"
        st.session_state.compare_ids = []
        st.rerun()

else:

    st.sidebar.divider()

    if st.sidebar.button(
        "🔐 " + tr("login"),
        use_container_width=True
    ):
        st.session_state.page = "Login"

    if st.sidebar.button(
        "📝 " + tr("register"),
        use_container_width=True
    ):
        st.session_state.page = "Register"


# ============================================================
# MAIN HEADER
# ============================================================

header_left, header_right = st.columns([1, 6])

with header_left:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=90)

with header_right:
    st.title(tr("title"))
    st.caption(tr("tagline"))

st.divider()


# ============================================================
# PAGE ROUTING
# ============================================================

page = st.session_state.page


# ============================================================
# LOGIN
# ============================================================

if page == "Login":

    st.header(
        "🔐 " + tr("login")
    )

    with st.form("login_form"):

        mobile = st.text_input(
            "Mobile Number"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button(
            tr("login"),
            use_container_width=True
        )

        if submitted:

            if not mobile or not password:

                st.error(
                    tr("required")
                )

            else:

                u = login_user(
                    mobile,
                    password
                )

                if u:

                    st.session_state.logged_in = True
                    st.session_state.user_id = u["id"]
                    st.session_state.user_name = u["full_name"]
                    st.session_state.page = "Home"

                    st.success(
                        "Login successful."
                    )

                    st.rerun()

                else:

                    st.error(
                        "Invalid mobile number or password."
                    )


# ============================================================
# REGISTER
# ============================================================

elif page == "Register":

    st.header(
        "📝 " + tr("register")
    )

    with st.form("register_form"):

        name = st.text_input(
            "Full Name"
        )

        mobile = st.text_input(
            "Mobile Number"
        )

        email = st.text_input(
            "Email (Optional)"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        confirm = st.text_input(
            "Confirm Password",
            type="password"
        )

        user_type = st.selectbox(
            "Account Type",
            USER_TYPES
        )

        province = st.selectbox(
            tr("province"),
            PROVINCES
        )

        city = st.selectbox(
            tr("city"),
            CITIES[province]
        )

        submitted = st.form_submit_button(
            tr("register"),
            use_container_width=True
        )

        if submitted:

            if (
                not name
                or not mobile
                or not password
                or not confirm
                or not city
            ):

                st.error(
                    tr("required")
                )

            elif password != confirm:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 6:

                st.error(
                    "Password must be at least 6 characters."
                )

            else:

                uid, error = register_user(
                    name,
                    mobile,
                    email,
                    password,
                    user_type,
                    province,
                    city
                )

                if error:

                    st.error(error)

                else:

                    st.success(
                        "Registration successful. Please login."
                    )


# ============================================================
# HOME
# ============================================================

elif page == "Home":

    st.header(
        "🔎 Find Your Property 🏡"
    )

    st.write(
        "Search residential, commercial, agricultural "
        "and other properties across Pakistan."
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(
            "🏡 " + tr("buy"),
            use_container_width=True
        ):

            st.session_state.page = "Buy"
            st.rerun()

    with c2:

        if st.button(
            "🏠 " + tr("rent"),
            use_container_width=True
        ):

            st.session_state.page = "Rent"
            st.rerun()

    with c3:

        if st.button(
            "💰 " + tr("sell"),
            use_container_width=True
        ):

            st.session_state.page = "Sell"
            st.rerun()

    st.subheader(
        "Quick Search"
    )

    ptype = st.selectbox(
        tr("property_type"),
        ["All"] + PROPERTY_TYPES,
        key="home_type"
    )

    province = st.selectbox(
        tr("province"),
        ["All"] + PROVINCES,
        key="home_province"
    )

    if province == "All":

        city_options = [
            "All"
        ] + sum(
            CITIES.values(),
            []
        )

    else:

        city_options = [
            "All"
        ] + CITIES.get(
            province,
            []
        )

    city = st.selectbox(
        tr("city"),
        city_options,
        key="home_city"
    )

    purpose = st.selectbox(
        tr("purpose"),
        [
            "All",
            "For Sale",
            "For Rent"
        ],
        key="home_purpose"
    )

    if st.button(
        "🔎 " + tr("search"),
        use_container_width=True,
        key="home_search"
    ):

        st.session_state.search_results = search_properties(
            purpose,
            ptype,
            province,
            city,
            0,
            0
        )

    for p in st.session_state.get(
        "search_results",
        []
    ):
        show_property_card(p)


# ============================================================
# BUY / RENT
# ============================================================

elif page in (
    "Buy",
    "Rent"
):

    property_search_page(
        page
    )


# ============================================================
# SELL / LIST PROPERTY
# ============================================================

elif page == "Sell":

    st.header(
        "💰 " + tr("sell")
    )

    if not st.session_state.logged_in:

        st.warning(
            tr("login_first")
        )

    else:

        with st.form("sell_form"):

            title = st.text_input(
                tr("property_title")
            )

            description = st.text_area(
                tr("description")
            )

            purpose = st.selectbox(
                tr("purpose"),
                [
                    "For Sale",
                    "For Rent"
                ]
            )

            ptype = st.selectbox(
                tr("property_type"),
                PROPERTY_TYPES
            )

            province = st.selectbox(
                tr("province"),
                PROVINCES,
                key="sell_province"
            )

            city = st.selectbox(
                tr("city"),
                CITIES[province],
                key="sell_city"
            )

            area_name = st.text_input(
                tr("area_locality")
            )

            area_value = st.number_input(
                tr("area"),
                min_value=0.0,
                step=0.5
            )

            area_unit = st.selectbox(
                tr("area_unit"),
                AREA_UNITS
            )

            price = st.number_input(
                tr("price"),
                min_value=0.0,
                step=100000.0
            )

            price_period = st.selectbox(
                "Price Period",
                [
                    "Total Price",
                    "Per Month",
                    "Per Year"
                ]
            )

            bedrooms = st.number_input(
                tr("bedrooms"),
                min_value=0,
                max_value=50,
                step=1
            )

            bathrooms = st.number_input(
                tr("bathrooms"),
                min_value=0,
                max_value=50,
                step=1
            )

            furnished = st.selectbox(
                tr("furnished"),
                FURNISHED
            )

            condition = st.selectbox(
                tr("condition"),
                CONDITIONS
            )

            amenities = st.text_area(
                tr("amenities"),
                placeholder=(
                    "Parking, Electricity, Gas, "
                    "Water, Security, Garden..."
                )
            )

            contact_name = st.text_input(
                tr("contact_name"),
                value=st.session_state.user_name
            )

            contact_mobile = st.text_input(
                tr("contact_mobile")
            )

            uploaded_images = st.file_uploader(
                "📷 Upload Property Pictures",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                ],
                accept_multiple_files=True,
                help="You can upload multiple property pictures."
            )

            st.caption(
                "You can upload multiple pictures of the property."
            )

            submitted = st.form_submit_button(
                "💾 " + tr("save"),
                use_container_width=True
            )

            if submitted:

                if (
                    not title
                    or not description
                    or not city
                    or area_value <= 0
                    or price <= 0
                    or not contact_mobile
                ):

                    st.error(
                        tr("required")
                    )

                else:

                    image_paths = save_uploaded_images(
                        uploaded_images
                    )

                    image_json = json.dumps(
                        image_paths
                    )

                    pid = save_property(
                        (
                            st.session_state.user_id,
                            title.strip(),
                            description.strip(),
                            purpose,
                            ptype,
                            province,
                            city,
                            area_name.strip(),
                            area_value,
                            area_unit,
                            price,
                            price_period,
                            bedrooms,
                            bathrooms,
                            furnished,
                            condition,
                            amenities.strip(),
                            contact_name.strip(),
                            contact_mobile.strip(),
                            "Pending",
                            "Active",
                            image_json
                        )
                    )

                    notify(
                        st.session_state.user_id,
                        "Listing Submitted",
                        f"Your property listing '{title.strip()}' "
                        "has been submitted for verification."
                    )

                    st.success(
                        f"{tr('listing_saved')} ID: {pid}"
                    )

                    if image_paths:

                        st.info(
                            f"📷 {len(image_paths)} "
                            "picture(s) uploaded successfully."
                        )


# ============================================================
# WANTED PROPERTY
# ============================================================

elif page == "Wanted":

    st.header(
        "🔎 " + tr("wanted")
    )

    if not st.session_state.logged_in:

        st.warning(
            tr("login_first")
        )

    else:

        with st.form("wanted_form"):

            ptype = st.selectbox(
                tr("property_type"),
                PROPERTY_TYPES,
                key="wanted_type"
            )

            purpose = st.selectbox(
                tr("purpose"),
                [
                    "Wanted to Buy",
                    "Wanted to Rent"
                ]
            )

            province = st.selectbox(
                tr("province"),
                PROVINCES,
                key="wanted_province"
            )

            city = st.selectbox(
                tr("city"),
                CITIES[province],
                key="wanted_city"
            )

            area = st.number_input(
                tr("area"),
                min_value=0.0,
                step=0.5,
                key="wanted_area"
            )

            unit = st.selectbox(
                tr("area_unit"),
                AREA_UNITS,
                key="wanted_unit"
            )

            budget = st.number_input(
                "Maximum Budget (PKR)",
                min_value=0.0,
                step=100000.0
            )

            req = st.text_area(
                "Additional Requirements"
            )

            submitted = st.form_submit_button(
                "📌 Post Requirement",
                use_container_width=True
            )

            if submitted:

                if (
                    not city
                    or budget <= 0
                ):

                    st.error(
                        tr("required")
                    )

                else:

                    title = (
                        f"Wanted {ptype} in {city}"
                    )

                    desc = (
                        f"{purpose}. "
                        f"Required Area: "
                        f"{area:g} {unit}. "
                        f"Maximum Budget: "
                        f"PKR {budget:,.0f}. "
                        f"{req}"
                    )

                    pid = save_property(
                        (
                            st.session_state.user_id,
                            title,
                            desc,
                            purpose,
                            ptype,
                            province,
                            city,
                            "",
                            area,
                            unit,
                            budget,
                            "Total Price",
                            0,
                            0,
                            "Not Applicable",
                            "New",
                            "",
                            st.session_state.user_name,
                            "",
                            "Pending",
                            "Active",
                            "[]"
                        )
                    )

                    st.success(
                        f"{tr('wanted_saved')} ID: {pid}"
                    )


# ============================================================
# MY LISTINGS
# ============================================================

elif page == "My Listings":

    st.header(
        "📋 " + tr("my_listings")
    )

    if not st.session_state.logged_in:

        st.warning(
            tr("login_first")
        )

    else:

        listings = rows(
            """
            SELECT *
            FROM properties
            WHERE user_id=?
            ORDER BY created_at DESC
            """,
            (
                st.session_state.user_id,
            )
        )

        if not listings:

            st.info(
                "You have not posted any properties yet."
            )

        for p in listings:

            show_property_card(p)

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "🟢 Mark Active / Available",
                    key=f"active_{p['id']}",
                    use_container_width=True
                ):

                    execute(
                        """
                        UPDATE properties
                        SET listing_status='Active',
                            updated_at=CURRENT_TIMESTAMP
                        WHERE id=?
                        AND user_id=?
                        """,
                        (
                            p["id"],
                            st.session_state.user_id
                        )
                    )

                    st.rerun()

            with c2:

                if st.button(
                    "🗑️ " + tr("delete"),
                    key=f"del_{p['id']}",
                    use_container_width=True
                ):

                    execute(
                        """
                        UPDATE properties
                        SET listing_status='Inactive',
                            updated_at=CURRENT_TIMESTAMP
                        WHERE id=?
                        AND user_id=?
                        """,
                        (
                            p["id"],
                            st.session_state.user_id
                        )
                    )

                    st.rerun()


# ============================================================
# FAVOURITES
# ============================================================

elif page == "Favourites":

    st.header(
        "❤️ " + tr("favourites")
    )

    if not st.session_state.logged_in:

        st.warning(
            tr("login_first")
        )

    else:

        favs = rows(
            """
            SELECT p.*
            FROM properties p
            JOIN favourites f
                ON p.id=f.property_id
            WHERE f.user_id=?
            ORDER BY f.created_at DESC
            """,
            (
                st.session_state.user_id,
            )
        )

        if not favs:

            st.info(
                "No favourite properties yet."
            )

        for p in favs:

            show_property_card(p)


# ============================================================
# MESSAGES
# ============================================================

elif page == "Messages":

    st.header(
        "💬 " + tr("messages")
    )

    if not st.session_state.logged_in:

        st.warning(
            tr("login_first")
        )

    else:

        uid = st.session_state.user_id

        partners = rows(
            """
            SELECT DISTINCT
                u.id,
                u.full_name
            FROM users u
            JOIN messages m
                ON (
                    u.id=m.sender_id
                    OR u.id=m.receiver_id
                )
            WHERE u.id!=?
            AND (
                m.sender_id=?
                OR m.receiver_id=?
            )
            ORDER BY u.full_name
            """,
            (
                uid,
                uid,
                uid
            )
        )

        if partners:

            partner = st.selectbox(
                "Conversation",
                partners,
                format_func=lambda x:
                    x["full_name"]
            )

            conversation = rows(
                """
                SELECT
                    m.*,
                    u.full_name AS sender_name
                FROM messages m
                JOIN users u
                    ON u.id=m.sender_id
                WHERE (
                    (
                        sender_id=?
                        AND receiver_id=?
                    )
                    OR
                    (
                        sender_id=?
                        AND receiver_id=?
                    )
                )
                ORDER BY m.created_at
                """,
                (
                    uid,
                    partner["id"],
                    partner["id"],
                    uid
                )
            )

            for m in conversation:

                st.write(
                    f"**{m['sender_name']}**: "
                    f"{m['message']}"
                )

                st.caption(
                    m["created_at"]
                )

        else:

            st.info(
                "No conversations yet. "
                "Use Contact Seller on a property."
            )

        st.divider()

        with st.form("message_form"):

            recipient_options = rows(
                """
                SELECT id,full_name
                FROM users
                WHERE id!=?
                AND is_active=1
                ORDER BY full_name
                """,
                (uid,)
            )

            if recipient_options:

                recipient = st.selectbox(
                    "Send To",
                    recipient_options,
                    format_func=lambda x:
                        x["full_name"]
                )

            else:

                recipient = None

            msg = st.text_area(
                tr("message")
            )

            submitted = st.form_submit_button(
                tr("send")
            )

            if submitted and recipient:

                if msg.strip():

                    execute(
                        """
                        INSERT INTO messages(
                            sender_id,
                            receiver_id,
                            property_id,
                            message
                        )
                        VALUES(?,?,?,?)
                        """,
                        (
                            uid,
                            recipient["id"],
                            st.session_state.get(
                                "message_property_id"
                            ),
                            msg.strip()
                        )
                    )

                    notify(
                        recipient["id"],
                        "New Message",
                        f"New message from "
                        f"{st.session_state.user_name}."
                    )

                    st.success(
                        "Message sent."
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Please enter a message."
                    )


# ============================================================
# NOTIFICATIONS
# ============================================================

elif page == "Notifications":

    st.header(
        "🔔 " + tr("notifications")
    )

    if not st.session_state.logged_in:

        st.warning(
            tr("login_first")
        )

    else:

        notes = rows(
            """
            SELECT *
            FROM notifications
            WHERE user_id=?
            ORDER BY created_at DESC
            """,
            (
                st.session_state.user_id,
            )
        )

        if not notes:

            st.info(
                "No notifications yet."
            )

        for n in notes:

            st.write(
                f"**{n['title']}** — "
                f"{n['message']}"
            )

            st.caption(
                n["created_at"]
            )

        execute(
            """
            UPDATE notifications
            SET is_read=1
            WHERE user_id=?
            """,
            (
                st.session_state.user_id,
            )
        )


# ============================================================
# SAVED SEARCHES
# ============================================================

elif page == "Saved Searches":

    st.header(
        "🔎 " + tr("saved_searches")
    )

    if not st.session_state.logged_in:

        st.warning(
            tr("login_first")
        )

    else:

        st.write(
            "Save a search for future use."
        )

        with st.form("save_search"):

            name = st.text_input(
                "Search Name"
            )

            ptype = st.selectbox(
                tr("property_type"),
                ["All"] + PROPERTY_TYPES
            )

            province = st.selectbox(
                tr("province"),
                ["All"] + PROVINCES
            )

            if province == "All":

                city_options = [
                    "All"
                ] + sum(
                    CITIES.values(),
                    []
                )

            else:

                city_options = [
                    "All"
                ] + CITIES.get(
                    province,
                    []
                )

            city = st.selectbox(
                tr("city"),
                city_options
            )

            purpose = st.selectbox(
                tr("purpose"),
                [
                    "All",
                    "For Sale",
                    "For Rent"
                ]
            )

            maxp = st.number_input(
                "Maximum Price (PKR)",
                min_value=0.0,
                step=100000.0
            )

            submitted = st.form_submit_button(
                tr("save")
            )

            if submitted:

                if name.strip():

                    search_data = json.dumps(
                        {
                            "property_type": ptype,
                            "province": province,
                            "city": city,
                            "purpose": purpose,
                            "max_price": maxp
                        }
                    )

                    execute(
                        """
                        INSERT INTO saved_searches(
                            user_id,
                            search_name,
                            search_data
                        )
                        VALUES(?,?,?)
                        """,
                        (
                            st.session_state.user_id,
                            name.strip(),
                            search_data
                        )
                    )

                    st.success(
                        "Search saved."
                    )

                else:

                    st.error(
                        tr("required")
                    )

        st.divider()

        saved = rows(
            """
            SELECT *
            FROM saved_searches
            WHERE user_id=?
            ORDER BY created_at DESC
            """,
            (
                st.session_state.user_id,
            )
        )

        for s in saved:

            st.write(
                f"**{s['search_name']}**"
            )

            st.code(
                s["search_data"],
                language="json"
            )


# ============================================================
# COMPARE
# ============================================================

elif page == "Compare":

    st.header(
        "⚖️ " + tr("compare")
    )

    if not st.session_state.compare_ids:

        st.info(
            "Select up to 3 properties "
            "using Compare on property cards."
        )

    else:

        placeholders = ",".join(
            "?"
            for _ in st.session_state.compare_ids
        )

        props = rows(
            f"""
            SELECT *
            FROM properties
            WHERE id IN ({placeholders})
            """,
            tuple(
                st.session_state.compare_ids
            )
        )

        if props:

            st.subheader(
                "Property Comparison"
            )

            for p in props:

                with st.container(
                    border=True
                ):

                    st.subheader(
                        p["title"]
                    )

                    images = get_property_images(
                        p
                    )

                    if images:

                        st.image(
                            images[0],
                            width=300
                        )

                    st.write(
                        f"🏠 Type: "
                        f"{p['property_type']}"
                    )

                    st.write(
                        f"📍 Location: "
                        f"{p['city']}, "
                        f"{p['province']}"
                    )

                    st.write(
                        f"💰 Price: "
                        f"PKR {p['price']:,.0f}"
                    )

                    st.write(
                        f"📐 Area: "
                        f"{p['area_value']:g} "
                        f"{p['area_unit']}"
                    )

                    st.write(
                        f"🛏️ Bedrooms: "
                        f"{p['bedrooms']}"
                    )

                    st.write(
                        f"🛁 Bathrooms: "
                        f"{p['bathrooms']}"
                    )

                    st.write(
                        f"🛋️ Furnished: "
                        f"{p['furnished']}"
                    )

                    st.write(
                        f"🏗️ Condition: "
                        f"{p['condition']}"
                    )

        if st.button(
            "Clear Comparison",
            use_container_width=True
        ):

            st.session_state.compare_ids = []
            st.rerun()


# ============================================================
# REVIEWS
# ============================================================

elif page == "Reviews":

    st.header(
        "⭐ " + tr("reviews")
    )

    if not st.session_state.logged_in:

        st.warning(
            tr("login_first")
        )

    else:

        my_props = rows(
            """
            SELECT id,title
            FROM properties
            WHERE user_id!=?
            AND listing_status='Active'
            ORDER BY created_at DESC
            """,
            (
                st.session_state.user_id,
            )
        )

        if not my_props:

            st.info(
                "No eligible properties yet."
            )

        else:

            with st.form("review_form"):

                p = st.selectbox(
                    "Property",
                    my_props,
                    format_func=lambda x:
                        x["title"]
                )

                rating = st.slider(
                    "Rating",
                    1,
                    5,
                    5
                )

                text = st.text_area(
                    "Review"
                )

                submitted = st.form_submit_button(
                    "Submit Review"
                )

                if submitted:

                    execute(
                        """
                        INSERT OR REPLACE INTO reviews(
                            reviewer_id,
                            property_id,
                            rating,
                            review_text,
                            status
                        )
                        VALUES(?,?,?,?,?)
                        """,
                        (
                            st.session_state.user_id,
                            p["id"],
                            rating,
                            text.strip(),
                            "Visible"
                        )
                    )

                    owner = one(
                        """
                        SELECT user_id
                        FROM properties
                        WHERE id=?
                        """,
                        (
                            p["id"],
                        )
                    )

                    if owner:

                        notify(
                            owner["user_id"],
                            "New Review",
                            f"A new {rating}-star review "
                            "was posted on your property."
                        )

                    st.success(
                        "Review submitted."
                    )

            st.divider()

            all_reviews = rows(
                """
                SELECT
                    r.*,
                    u.full_name
                FROM reviews r
                JOIN users u
                    ON u.id=r.reviewer_id
                WHERE r.status='Visible'
                ORDER BY r.created_at DESC
                """
            )

            for r in all_reviews:

                st.write(
                    f"⭐ {r['rating']}/5 — "
                    f"**{r['full_name']}** — "
                    f"{r.get('review_text') or ''}"
                )


# ============================================================
# PROFILE
# ============================================================

elif page == "Profile":

    st.header(
        "👤 " + tr("profile")
    )

    if not st.session_state.logged_in:

        st.warning(
            tr("login_first")
        )

    else:

        u = one(
            """
            SELECT *
            FROM users
            WHERE id=?
            """,
            (
                st.session_state.user_id,
            )
        )

        if u:

            with st.form("profile_form"):

                name = st.text_input(
                    "Full Name",
                    value=u["full_name"]
                )

                email = st.text_input(
                    "Email",
                    value=u["email"] or ""
                )

                province_index = (
                    PROVINCES.index(
                        u["province"]
                    )
                    if u["province"]
                    in PROVINCES
                    else 0
                )

                province = st.selectbox(
                    tr("province"),
                    PROVINCES,
                    index=province_index
                )

                city_list = CITIES.get(
                    province,
                    []
                )

                city_index = (
                    city_list.index(
                        u["city"]
                    )
                    if u["city"]
                    in city_list
                    else 0
                )

                city = st.selectbox(
                    tr("city"),
                    city_list,
                    index=city_index
                )

                submitted = st.form_submit_button(
                    tr("update")
                )

                if submitted:

                    try:

                        execute(
                            """
                            UPDATE users
                            SET full_name=?,
                                email=?,
                                province=?,
                                city=?
                            WHERE id=?
                            """,
                            (
                                name.strip(),
                                email.strip()
                                or None,
                                province,
                                city,
                                st.session_state.user_id
                            )
                        )

                        st.session_state.user_name = (
                            name.strip()
                        )

                        st.success(
                            "Profile updated."
                        )

                    except sqlite3.IntegrityError:

                        st.error(
                            "Email already exists."
                        )


# ============================================================
# REPORT LISTING
# ============================================================

elif page == "Report":

    st.header(
        "🚩 Report Listing"
    )

    if not st.session_state.logged_in:

        st.warning(
            tr("login_first")
        )

    else:

        pid = st.session_state.get(
            "report_property_id"
        )

        if pid:

            property_info = one(
                """
                SELECT title
                FROM properties
                WHERE id=?
                """,
                (pid,)
            )

            if property_info:

                st.write(
                    f"Reporting: "
                    f"**{property_info['title']}**"
                )

        with st.form("report_form"):

            rtype = st.selectbox(
                "Reason",
                [
                    "Incorrect Information",
                    "Suspicious Listing",
                    "Fraud Concern",
                    "Inappropriate Content",
                    "Other"
                ]
            )

            details = st.text_area(
                "Details"
            )

            submitted = st.form_submit_button(
                "Submit Report"
            )

            if submitted:

                execute(
                    """
                    INSERT INTO reports(
                        reporter_id,
                        property_id,
                        report_type,
                        details
                    )
                    VALUES(?,?,?,?)
                    """,
                    (
                        st.session_state.user_id,
                        pid,
                        rtype,
                        details.strip()
                    )
                )

                st.success(
                    "Report submitted for review."
                )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

elif page == "Admin":

    st.header(
        "🛡️ " + tr("admin")
    )

    if not st.session_state.admin_logged:

        with st.form("admin_login"):

            au = st.text_input(
                "Admin Username"
            )

            ap = st.text_input(
                "Admin Password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Admin Login"
            )

            if submitted:

                admin = one(
                    """
                    SELECT *
                    FROM admin_users
                    WHERE username=?
                    AND password=?
                    """,
                    (
                        au,
                        ap
                    )
                )

                if admin:

                    st.session_state.admin_logged = True
                    st.success(
                        "Admin mode active."
                    )
                    st.rerun()

                else:

                    st.error(
                        "Invalid admin credentials."
                    )

    else:

        st.success(
            "🛡️ Admin mode active."
        )

        tab1, tab2, tab3 = st.tabs(
            [
                "Properties",
                "Users",
                "Reports"
            ]
        )

        # ----------------------------------------------------
        # ADMIN PROPERTIES
        # ----------------------------------------------------

        with tab1:

            admin_properties = rows(
                """
                SELECT *
                FROM properties
                ORDER BY created_at DESC
                """
            )

            if not admin_properties:

                st.info(
                    "No properties available."
                )

            for p in admin_properties:

                with st.container(
                    border=True
                ):

                    st.write(
                        f"**#{p['id']} "
                        f"{p['title']}**"
                    )

                    st.write(
                        f"📍 {p['city']}, "
                        f"{p['province']}"
                    )

                    st.write(
                        f"💰 PKR "
                        f"{p['price']:,.0f}"
                    )

                    st.write(
                        f"Verification: "
                        f"**{p['verification_status']}** "
                        f"| Listing: "
                        f"**{p['listing_status']}**"
                    )

                    images = get_property_images(
                        p
                    )

                    if images:

                        st.image(
                            images[0],
                            width=250
                        )

                        st.caption(
                            f"{len(images)} "
                            "picture(s)"
                        )

                    c1, c2, c3 = st.columns(3)

                    with c1:

                        if st.button(
                            "✅ Verify",
                            key=f"verify_{p['id']}",
                            use_container_width=True
                        ):

                            execute(
                                """
                                UPDATE properties
                                SET verification_status='Verified',
                                    updated_at=CURRENT_TIMESTAMP
                                WHERE id=?
                                """,
                                (
                                    p["id"],
                                )
                            )

                            notify(
                                p["user_id"],
                                "Listing Verified",
                                "Your property listing "
                                "has been verified."
                            )

                            st.rerun()

                    with c2:

                        if st.button(
                            "❌ Reject",
                            key=f"reject_{p['id']}",
                            use_container_width=True
                        ):

                            execute(
                                """
                                UPDATE properties
                                SET verification_status='Rejected',
                                    updated_at=CURRENT_TIMESTAMP
                                WHERE id=?
                                """,
                                (
                                    p["id"],
                                )
                            )

                            notify(
                                p["user_id"],
                                "Listing Update",
                                "Your property listing "
                                "was rejected."
                            )

                            st.rerun()

                    with c3:

                        if st.button(
                            "⛔ Deactivate",
                            key=f"deact_{p['id']}",
                            use_container_width=True
                        ):

                            execute(
                                """
                                UPDATE properties
                                SET listing_status='Inactive',
                                    updated_at=CURRENT_TIMESTAMP
                                WHERE id=?
                                """,
                                (
                                    p["id"],
                                )
                            )

                            notify(
                                p["user_id"],
                                "Listing Deactivated",
                                "Your property listing "
                                "has been deactivated."
                            )

                            st.rerun()

        # ----------------------------------------------------
        # ADMIN USERS
        # ----------------------------------------------------

        with tab2:

            users = rows(
                """
                SELECT
                    id,
                    full_name,
                    mobile,
                    email,
                    user_type,
                    province,
                    city,
                    is_active,
                    created_at
                FROM users
                ORDER BY created_at DESC
                """
            )

            if users:

                st.dataframe(
                    users,
                    use_container_width=True
                )

            else:

                st.info(
                    "No users registered yet."
                )

        # ----------------------------------------------------
        # ADMIN REPORTS
        # ----------------------------------------------------

        with tab3:

            reports = rows(
                """
                SELECT
                    r.*,
                    u.full_name AS reporter
                FROM reports r
                JOIN users u
                    ON u.id=r.reporter_id
                ORDER BY r.created_at DESC
                """
            )

            if not reports:

                st.info(
                    "No reports yet."
                )

            for r in reports:

                with st.container(
                    border=True
                ):

                    st.write(
                        f"🚩 **Report #{r['id']}**"
                    )

                    st.write(
                        f"Type: "
                        f"**{r['report_type']}**"
                    )

                    st.write(
                        f"Reporter: "
                        f"**{r['reporter']}**"
                    )

                    st.write(
                        f"Details: "
                        f"{r['details'] or 'No details'}"
                    )

                    st.write(
                        f"Status: "
                        f"**{r['status']}**"
                    )

                    st.caption(
                        r["created_at"]
                    )

                    c1, c2 = st.columns(2)

                    with c1:

                        if st.button(
                            "✅ Mark Resolved",
                            key=f"resolve_report_{r['id']}",
                            use_container_width=True
                        ):

                            execute(
                                """
                                UPDATE reports
                                SET status='Resolved'
                                WHERE id=?
                                """,
                                (
                                    r["id"],
                                )
                            )

                            st.rerun()

                    with c2:

                        if st.button(
                            "🔓 Keep Open",
                            key=f"open_report_{r['id']}",
                            use_container_width=True
                        ):

                            execute(
                                """
                                UPDATE reports
                                SET status='Open'
                                WHERE id=?
                                """,
                                (
                                    r["id"],
                                )
                            )

                            st.rerun()

        st.divider()

        if st.button(
            "🚪 Admin Logout",
            use_container_width=True
        ):

            st.session_state.admin_logged = False
            st.session_state.page = "Home"
            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Pakistan Estate Hub • "
    "Buy • Sell • Rent • Find Property Across Pakistan"
)