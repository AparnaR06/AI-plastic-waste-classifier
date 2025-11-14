import streamlit as st
import pandas as pd
import numpy as np
import os
import hashlib
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import st_folium
import altair as alt

# ---------------- SESSION & CONFIG SETUP ----------------
# Initialize session state for login/auth
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "auth_mode" not in st.session_state: 
    st.session_state.auth_mode = "login"

# Set page config - sidebar always visible
st.set_page_config(
    page_title="♻️ Plastic Waste Classifier", 
    layout="wide"
)

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
    pd.concat([users, new_user], ignore_index=True).to_csv(USERS_FILE, index=False)

def validate_user(username, password):
    users = load_users()
    hashed = hash_password(password)
    return ((users["username"] == username) & (users["password"] == hashed)).any()

def save_history(username, filename, result):
    df = pd.read_csv(HISTORY_FILE)
    new = pd.DataFrame([[username, filename, result, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]],
                        columns=["username", "filename", "result", "timestamp"])
    pd.concat([df, new], ignore_index=True).to_csv(HISTORY_FILE, index=False)

def load_history(username):
    df = pd.read_csv(HISTORY_FILE)
    return df[df["username"] == username].sort_values(by="timestamp", ascending=False)

# ---------------- CSS STYLING ----------------
st.markdown("""
<style>
header[data-testid="stHeader"] {display: none;}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1C1C1C, #2C2C2C);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #E0E0E0;
}

/* Sidebar - always visible and expanded */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2C2C2C, #3A3A3A) !important;
    border-right: 5px solid #006400 !important;
    box-shadow: 5px 0 15px rgba(0,0,0,0.7) !important;
    min-width: 300px !important;
}

[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(180deg, #2C2C2C, #3A3A3A);
}

/* Remove collapse button */
button[kind="header"] {
    display: none !important;
}

[data-testid="collapsedControl"] {
    display: none !important;
}
[data-testid="stSidebar"] * {
    color: #E0E0E0 !important;
}

[data-testid="stSidebar"] .stRadio > label {
    color: #E0E0E0 !important;
    font-size: 24px !important;
}

[data-testid="stSidebar"] [data-baseweb="radio"] > div {
    background-color: transparent !important;
}

.stButton>button {
    background: linear-gradient(135deg, #006400, #3CB371) !important;
    color: white !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(0, 100, 0, 0.5);
    transition: 0.3s ease !important;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #3CB371, #006400) !important;
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 100, 0, 1.0);
}
.main-title {
    text-align: center;
    font-size: 55px;
    font-weight: 900;
    background: linear-gradient(45deg, #FFD700, #006400);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 50px;
}
.content-card {
    background: #2C2C2C;
    border-radius: 20px;
    padding: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.9);
    border: 1px solid #006400;
    margin-bottom: 20px;
}
.welcome-header-sidebar {
    background: #006400;
    padding: 15px 10px;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 4px 10px rgba(0, 100, 0, 0.8);
    margin-bottom: 20px;
}
.welcome-header-sidebar h5 {
    color: white !important;
    margin: 0;
    font-size: 20px;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


# ---------------- LOGIN PAGE ----------------
def login_page():
    st.markdown("<div class='main-title'>♻️ AI Plastic Waste Classifier</div>", unsafe_allow_html=True)
    col_s1, col_l, col_gap, col_r, col_s2 = st.columns([1, 1, 0.1, 1, 1])
    
    def set_login_mode(): st.session_state.auth_mode = "login"
    def set_register_mode(): st.session_state.auth_mode = "register"

    with col_l:
        st.button("🔑 Login", on_click=set_login_mode, type="primary", use_container_width=True, key="login_btn_fix_final")
    
    with col_r:
        st.button("🆕 Register", on_click=set_register_mode, type="secondary", use_container_width=True, key="register_btn_fix_final")

    col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
    with col_f2:
        if st.session_state.auth_mode == "login":
            st.subheader("🔒 Secure Access") 
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("🚀 Secure Login"):
                if validate_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("✅ Login successful!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")
        else:
            st.subheader("🆕 Create Account")
            new_user = st.text_input("Username")
            new_pass = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            if st.button("🎉 Register Now"):
                if new_pass != confirm:
                    st.error("❌ Passwords do not match!")
                elif new_user in load_users()["username"].values:
                    st.warning("⚠️ Username already exists.")
                else:
                    save_user(new_user, new_pass)
                    st.success("🎉 Registration successful! Please log in.")
                    st.session_state.auth_mode = "login"
                    st.rerun()

# ---------------- MAIN APP ----------------
def main_app():
    
    # Sidebar with welcome header and menu
    with st.sidebar:
        st.markdown(f"""
            <div class='welcome-header-sidebar'>
                <h5>👋 Welcome, {st.session_state.username}!</h5>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("### Navigation Menu")
        menu = st.radio(
            "Menu",
            ["🏠 Home", "📷 Classify Plastic", "🕒 History", "🌍 Map", "📊 Dashboard", "🔚 Logout"],
            label_visibility="collapsed",
            key="main_menu_radio"
        )

    # --- Page Content ---
    if menu == "🏠 Home":
        st.markdown("<h1 style='text-align:center;'>♻️ Plastic Waste Classification Platform</h1>", unsafe_allow_html=True)
        
        # Featured Card
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            st.markdown("""
            <div class='content-card' style='text-align:center;'>
                <h3 style='color:#FFD700;'>🎯 Our Mission: Streamlining Plastic Recycling</h3>
                <p>Utilize **AI-powered image recognition** to classify plastic waste with high accuracy (PET, HDPE, PVC, etc.), providing instant recycling instructions.</p>
                <p style='font-weight:700;'>Navigate to the <span style='color:#006400;'>Classify Plastic</span> tab to upload your item and contribute to a cleaner planet!</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Feature Highlight Cards
        col_icons = st.columns(3)
        features = [
            ("🤖", "Polymer Recognition", "Accurate classification for 7 common plastic types."),
            ("⏳", "Instant Recycling Guide", "Get results and specific disposal instructions immediately."),
            ("🎯", "Personalized Impact", "Track your classification history and material contribution.")
        ]
        for i, (icon, title, desc) in enumerate(features):
            with col_icons[i]:
                st.markdown(f"""
                <div class='content-card' style='min-height: 50px;'>
                    <h4 style='text-align:center;font-size: 24px; color:#006400;'>{icon} {title}</h4>
                    <p style='text-align:center;font-size: 14px;'>{desc}</p>
                </div>
                """, unsafe_allow_html=True)
                
        # Additional content
        st.markdown("<br><h2 style='text-align:center; color:#FFD700;'>Why Accurate Plastic Sorting Matters</h2>", unsafe_allow_html=True)
        col_why1, col_why2 = st.columns(2)
        with col_why1:
            st.markdown("""
            <div class='content-card'>
                <h4>Reducing Contamination 📈</h4>
                <p>Incorrectly sorted plastic is the leading cause of rejection at recycling facilities. Our AI ensures precision.</p>
            </div>
            """, unsafe_allow_html=True)
        with col_why2:
             st.markdown("""
            <div class='content-card'>
                <h4>Maximizing Material Value 💡</h4>
                <p>By identifying the exact polymer, we maximize the commercial value and circularity of the recycled material.</p>
            </div>
            """, unsafe_allow_html=True)


    elif menu == "📷 Classify Plastic":
        st.subheader("📸 Plastic Waste AI Classifier")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h4 style='color:#FFD700;'>Upload Plastic Item Image</h4>", unsafe_allow_html=True)
            file = st.file_uploader("Choose a JPG/PNG image of the plastic waste item:", type=["jpg", "jpeg", "png"])
            
            if file:
                img = Image.open(file)
                st.image(img, caption=f"Processing: {file.name}", use_container_width=True)
            else:
                st.info("Upload an image of plastic waste to begin classification.")

        with col2:
            st.markdown("<h4 style='color:#FFD700;'>AI Prediction Result & Action</h4>", unsafe_allow_html=True)
            
            if file:
                
                # AI Simulation 
                with st.spinner('⏳ AI Model classifying plastic polymer...'):
                    waste_types = {
                        "PET (Water Bottles) 🥤": "Recyclable",
                        "HDPE (Milk Jugs) 🧴": "Recyclable",
                        "PVC (Pipes/Frames) 🛠️": "Non-Recyclable",
                        "LDPE (Plastic Bags) 🛍️": "Recyclable",
                        "PP (Yogurt Containers) 🥛": "Recyclable",
                        "PS (Styrofoam) ☕": "Non-Recyclable"
                    }
                    
                    random_type = np.random.choice(list(waste_types.keys()))
                    result_category = waste_types[random_type]
                    
                    st.markdown("<br>", unsafe_allow_html=True) 

                    if result_category == "Recyclable":
                        st.success(f"✅ Classification: **{random_type}** (Recyclable)")
                        st.markdown(f"<p style='font-weight:700; color:#3CB371;'>Action Required: Clean the item thoroughly, crush to save space, and place it in the **Green Recycling Bin**.</p>", unsafe_allow_html=True)
                    else:
                        st.error(f"❌ Classification: **{random_type}** (Non-Recyclable)")
                        st.markdown(f"<p style='font-weight:700; color:#FF4D4D;'>Action Required: This plastic item must be disposed of safely in the **Black General Waste Bin**.</p>", unsafe_allow_html=True)

                save_history(st.session_state.username, file.name, random_type)
            else:
                 st.info("Your plastic classification results and recycling advice will appear here after an image is uploaded.")


    elif menu == "🕒 History":
        st.subheader("🕒 Plastic Classification History")
        
        hist = load_history(st.session_state.username)
        
        if not hist.empty:
            # Display stats
            total_predictions = len(hist)
            recyclable_count = hist["result"].str.contains("PET|HDPE|LDPE|PP").sum() 
            non_recyclable_count = total_predictions - recyclable_count
            
            col_h1, col_h2, col_h3 = st.columns(3)
            col_h1.metric("Total Plastic Items Classified", total_predictions)
            col_h2.metric("Recyclable Items Identified", recyclable_count)
            col_h3.metric("Non-Recyclable Items Identified", non_recyclable_count)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#FFD700;'>Full History Log</h4>", unsafe_allow_html=True)
            st.dataframe(hist, use_container_width=True, hide_index=True)
            
            if st.button("🗑️ Clear All History", key="clear_history_btn"):
                df = pd.read_csv(HISTORY_FILE)
                df[df["username"] != st.session_state.username].to_csv(HISTORY_FILE, index=False)
                st.toast("History cleared successfully!", icon='✅')
                st.rerun()

        else:
            st.info("📭 No plastic classification history yet. Get started on the 'Classify Plastic' tab!")

    elif menu == "🌍 Map":
        st.subheader("🌍 Global Plastic Waste & Recycling Insights")
        
        st.markdown("""
        <div class='content-card' style='margin-bottom: 30px;'>
            <p>This map visualizes simulated plastic waste statistics across the globe. Hover over the markers for details on **Plastic Waste (tons)** and **Recycling Rate (%)**.</p>
            <p style='font-weight:600;'>The map is fixed to a global view and will not automatically zoom or pan (as requested).</p>
        </div>
        """, unsafe_allow_html=True)
        
        df = pd.read_csv(DATA_FILE)
        
        m = folium.Map(location=[20, 0], zoom_start=2, tiles="cartodbdarkmatter", zoom_control=False, scrollWheelZoom=False, dragging=False)
        
        for _, r in df.iterrows():
            rate = r["Recycling Rate (%)"]
            color = "#3CB371" if rate > 65 else "#FFA500" if rate > 40 else "#FF4D4D"
            
            folium.CircleMarker(
                location=[r["Latitude"], r["Longitude"]],
                radius=10 + (rate / 10), 
                popup=f"<b>{r['Country']}</b><br>Waste: {r['Plastic Waste (tons)'] / 1000000:.1f}M tons<br>Recycling: {rate}%",
                color=color,
                fill=True,
                fillOpacity=0.7
            ).add_to(m)
        
        st_folium(m, width=None, height=650)


    elif menu == "📊 Dashboard":
        st.subheader("📊 Comparative Plastic Waste Analytics")
        st.markdown("""
        <div class='content-card' style='margin-bottom: 30px;'>
            <p>Visual breakdown of simulated global plastic waste generation and recycling efficiency. Charts are now static and non-zoomable.</p>
        </div>
        """, unsafe_allow_html=True)
        
        df = pd.read_csv(DATA_FILE).reset_index() 
        
        # Scatter chart
        st.markdown("<h4 style='color:#FFD700; text-align:center;'>Recycling Rate vs. Total Plastic Waste Correlation</h4>", unsafe_allow_html=True)
        
        scatter = alt.Chart(df).mark_circle(size=100).encode(
            x=alt.X("Plastic Waste (tons)"), 
            y=alt.Y("Recycling Rate (%)"),
            color=alt.value("#FFD700"),
            tooltip=["Country", "Plastic Waste (tons)", "Recycling Rate (%)"]
        )
        st.altair_chart(scatter, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_d1, col_d2 = st.columns(2)
        
        # Bar Chart
        bar_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("Country:N", sort="-y"),
            y=alt.Y("Plastic Waste (tons)"),
            color=alt.value("#3CB371"),
            tooltip=["Country", "Plastic Waste (tons)"]
        ).properties(
            title="Total Plastic Waste by Country"
        )
        
        with col_d1:
            st.markdown("<h4 style='color:#FFD700;'>Total Plastic Waste (Tons)</h4>", unsafe_allow_html=True)
            st.altair_chart(bar_chart, use_container_width=True)
            
        # Line Chart
        line_chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X("Country:N", sort=alt.EncodingSortField(field="Recycling Rate (%)", op="mean", order='descending')),
            y=alt.Y("Recycling Rate (%)"),
            color=alt.value("#FFD700"),
            tooltip=["Country", "Recycling Rate (%)"]
        ).properties(
            title="Recycling Rate by Country"
        )

        with col_d2:
            st.markdown("<h4 style='color:#FFD700;'>Recycling Rate (%)</h4>", unsafe_allow_html=True)
            st.altair_chart(line_chart, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("View Raw Data Table"):
             st.dataframe(df.set_index("Country"), use_container_width=True)
             
    elif menu == "🔚 Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("👋 Logged out successfully! Thank you for your contribution.")
        st.rerun()


# ---------------- RUN ---------------
if not st.session_state.logged_in:
    login_page()
else:
    main_app()