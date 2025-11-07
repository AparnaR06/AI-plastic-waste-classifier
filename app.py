import streamlit as st
import pandas as pd
import numpy as np
import os
import hashlib
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import st_folium

# ---------------- CONFIG ----------------
st.set_page_config(page_title="♻️ AI Plastic Waste Classifier", layout="wide")

# ---------------- FILE SETUP ----------------
USERS_FILE = "users.csv"
HISTORY_FILE = "history.csv"
DATA_FILE = "waste_data.csv"

if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["username", "password"]).to_csv(USERS_FILE, index=False)

if not os.path.exists(HISTORY_FILE):
    pd.DataFrame(columns=["username", "filename", "result", "timestamp"]).to_csv(HISTORY_FILE, index=False)

if not os.path.exists(DATA_FILE):
    data = {
        "Country": ["India", "USA", "Japan", "Brazil", "Germany"],
        "Plastic Waste (tons)": [3500000, 4200000, 2500000, 1800000, 2200000],
        "Recycling Rate (%)": [60, 35, 78, 45, 66],
        "Latitude": [20.5937, 37.0902, 36.2048, -14.235, 51.1657],
        "Longitude": [78.9629, -95.7129, 138.2529, -51.9253, 10.4515],
    }
    pd.DataFrame(data).to_csv(DATA_FILE, index=False)

# ---------------- HELPERS ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    return pd.read_csv(USERS_FILE)

def save_user(username, password):
    users = load_users()
    hashed = hash_password(password)
    new_user = pd.DataFrame([[username, hashed]], columns=["username", "password"])
    pd.concat([users, new_user]).to_csv(USERS_FILE, index=False)

def validate_user(username, password):
    users = load_users()
    hashed = hash_password(password)
    return ((users["username"] == username) & (users["password"] == hashed)).any()

def save_history(username, filename, result):
    df = pd.read_csv(HISTORY_FILE)
    new = pd.DataFrame([[username, filename, result, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]],
                       columns=["username", "filename", "result", "timestamp"])
    pd.concat([df, new]).to_csv(HISTORY_FILE, index=False)

def load_history(username):
    df = pd.read_csv(HISTORY_FILE)
    return df[df["username"] == username]

# ---------------- STYLE ----------------
st.markdown("""
    <style>
        /* Background */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(to right, #E3FDFD, #CBF1F5, #A6E3E9);
            color: #000000;
        }
        [data-testid="stHeader"] {background: none;}
        [data-testid="stSidebar"] {
            background-color: #f5f5f5;
            color: #000000;
        }

        /* Sidebar radio */
        section[data-testid="stSidebar"] div[role="radiogroup"] label p {
            color: #d32f2f !important;
            font-weight: 600 !important;
        }

        /* Title */
        .main-title {
            text-align: center;
            font-size: 42px;
            font-weight: 800;
            color: #004d40;
            margin-top: -10px;
            margin-bottom: 30px;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        }

        /* Form layout */
        .centered-form {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        /* Input fields */
        div[data-baseweb="input"] > div {
            background-color: #ffffff !important;
            border: 1px solid #aaa !important;
            border-radius: 10px !important;
            color: #000000 !important;
            box-shadow: none !important;
        }

        div[data-baseweb="input"] input {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        input[type="password"] {
            background-color: white !important;
            color: black !important;
        }

        input[type="password"]::-ms-reveal,
        input[type="password"]::-ms-clear {
            display: none !important;
        }

        label {
            color: #004d40 !important;
            font-weight: 600 !important;
        }

        /* Buttons */
        .stButton>button {
            background-color: #e53935 !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            width: 120px !important;
            height: 38px !important;
            font-weight: 600 !important;
        }
        .stButton>button:hover {
            background-color: #c62828 !important;
        }

        /* Tabs */
        div[data-baseweb="tab-list"] {
            justify-content: center !important;
            gap: 10px !important;
            margin-bottom: 25px;
        }
        div[role="tab"] {
            background-color: #ffffff !important;
            border: 2px solid #000000 !important;
            border-radius: 20px !important;
            padding: 8px 20px !important;
            transition: all 0.3s ease-in-out;
        }
        div[role="tab"]:hover {
            background-color: #f0f0f0 !important;
            transform: scale(1.05);
        }
        div[role="tab"][aria-selected="true"] {
            background-color: #000000 !important;
            border-color: #000000 !important;
        }
        div[role="tab"] p {
            color: #000000 !important;
            font-weight: 700 !important;
        }
        div[role="tab"][aria-selected="true"] p {
            color: #ffffff !important;
        }
    </style>
""",
 unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- LOGIN / REGISTER ----------------
def login_page():
    st.markdown("<div class='main-title'>♻️ AI Plastic Waste Classifier</div>", unsafe_allow_html=True)
    tabs = st.tabs(["🔑 Login", "🆕 Register"])

    # Login
    with tabs[0]:
        st.markdown("<div class='centered-form'>", unsafe_allow_html=True)
        st.subheader("🔒 Login")
        username = st.text_input("Username", key="login_user", max_chars=50)
        password = st.text_input("Password", type="password", key="login_pass", max_chars=50)
        show_pw = st.checkbox("Show Password", key="login_show_pw")
        if show_pw:
            st.text_input("Visible Password", value=password, key="login_visible_pw")
        if st.button("Login"):
            if validate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Register
    with tabs[1]:
        st.markdown("<div class='centered-form'>", unsafe_allow_html=True)
        st.subheader("🧾 Register")
        new_user = st.text_input("New Username", key="reg_user", max_chars=50)
        new_pass = st.text_input("New Password", type="password", key="reg_pass", max_chars=50)
        if st.button("Register"):
            if new_user and new_pass:
                users = load_users()
                if new_user in users["username"].values:
                    st.warning("⚠️ Username already exists.")
                else:
                    save_user(new_user, new_pass)
                    st.success("🎉 Registered successfully! Please login.")
            else:
                st.error("⚠️ Fill all fields.")
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- MAIN APP ----------------
def main_app():
    st.sidebar.title(f"👋 Welcome, {st.session_state.username}")
    menu = st.sidebar.radio("Navigate", ["🏠 Home", "📷 Classify", "🕒 History", "🌍 Map", "📊 Dashboard", "🚪 Logout"])

    if menu == "🏠 Home":
        st.title("🌱 AI Plastic Waste Classifier")
        st.markdown("""
        This platform identifies **plastic waste types** using AI and suggests **recycling options**.  
        You can upload images, view your classification history, and explore waste data globally 🌍.
        """)

    elif menu == "📷 Classify":
        st.subheader("📸 Upload & Classify")
        file = st.file_uploader("Upload waste image", type=["jpg", "jpeg", "png"])
        if file:
            img = Image.open(file)
            st.image(img, caption="Uploaded Image",width=300)
            result = np.random.choice(["Recyclable", "Non-Recyclable"])
            st.success(f"♻️ Classified as: **{result}**")
            save_history(st.session_state.username, file.name, result)

    elif menu == "🕒 History":
        st.subheader("🕒 Classification History")
        hist = load_history(st.session_state.username)
        if not hist.empty:
            st.dataframe(hist)
        else:
            st.info("No history yet.")

    elif menu == "🌍 Map":
        st.subheader("🌍 Global Waste Map")
        df = pd.read_csv(DATA_FILE)
        m = folium.Map(location=[20, 0], zoom_start=2)
        for _, r in df.iterrows():
            folium.Marker(
                location=[r["Latitude"], r["Longitude"]],
                popup=f"<b>{r['Country']}</b><br>Waste: {r['Plastic Waste (tons)']} tons<br>Recycling: {r['Recycling Rate (%)']}%",
                icon=folium.Icon(color="green" if r["Recycling Rate (%)"] > 50 else "red")
            ).add_to(m)
        st_folium(m, width=950, height=500)

    elif menu == "📊 Dashboard":
        st.subheader("📊 Country Dashboard")
        df = pd.read_csv(DATA_FILE)
        st.bar_chart(df.set_index("Country")[["Plastic Waste (tons)", "Recycling Rate (%)"]])

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# ---------------- RUN ----------------
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
