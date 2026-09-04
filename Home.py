import streamlit as st
import pandas as pd
import numpy as np
from utils.translations import init_language, t

# ==========================================
# 0. Page Configuration
# ==========================================
st.set_page_config(
    page_title="DataPilot AI - Home",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🌐 1. Initialize Language & Sidebar
init_language()

# 🎨 2. Load Custom CSS from Assets
try:
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# 🔄 3. RTL Page Direction Handling
if st.session_state.get("lang") == "ar":
    st.markdown("""
        <style>
            .stApp {
                direction: RTL;
                text-align: right;
            }
            .cap-num {
                margin-right: 0px !important;
                margin-left: 10px !important;
            }
            .card-1, .card-2, .card-3, .card-4, .card-5, .card-6, .card-7, .card-8, .card-9 {
                border-left: none !important;
                border-right: 5px solid !important;
            }
            .card-1 { border-right-color: #3B82F6 !important; }
            .card-2 { border-right-color: #22C55E !important; }
            .card-3 { border-right-color: #EF4444 !important; }
            .card-4 { border-right-color: #F59E0B !important; }
            .card-5 { border-right-color: #8B5CF6 !important; }
            .card-6 { border-right-color: #06B6D4 !important; }
            .card-7 { border-right-color: #EC4899 !important; }
            .card-8 { border-right-color: #14B8A6 !important; }
            .card-9 { border-right-color: #A855F7 !important; }
        </style>
    """, unsafe_allow_html=True)

# Custom Styling with Colorful Modern UI & Sidebar
st.markdown("""
    <style>
        /* 🎯 Hide Sidebar Bottom Logo to prevent duplicate images */
        [data-testid="stSidebar"] img {
            display: none !important;
        }

        /* 🎯 Sidebar Navigation Complete Bold Fix */
        [data-testid="stSidebarNav"] * {
            font-weight: 700 !important;
            color: #0F172A !important;
        }

        [data-testid="stSidebarNav"] a, 
        [data-testid="stSidebarNav"] a span,
        [data-testid="stSidebarNav"] li div span {
            font-weight: 700 !important;
            font-size: 15px !important;
            color: #0F172A !important;
        }

        [data-testid="stSidebarNav"] a[aria-current="page"],
        [data-testid="stSidebarNav"] a[aria-current="page"] span {
            font-weight: 900 !important;
            color: #2563EB !important;
            background-color: #E0E7FF !important;
            border-radius: 8px !important;
        }

        [data-testid="stSidebarNav"] a:hover span {
            color: #2563EB !important;
        }

        /* Brand Badge Styling */
        .brand-badge {
            background-color: #eef2ff;
            color: #4f46e5;
            font-weight: 700;
            font-size: 0.9rem;
            padding: 6px 14px;
            border-radius: 20px;
            border: 1px solid #c7d2fe;
            display: inline-block;
            margin-bottom: 10px;
            box-shadow: 0 2px 5px rgba(79, 70, 229, 0.08);
        }

        /* Modern Title Styling (Hero Section) */
        .hero-title {
            font-size: 38px;
            font-weight: 800;
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #8B5CF6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
            line-height: 1.25;
        }
        .hero-subtitle {
            font-size: 16px;
            color: #475569;
            margin-bottom: 25px;
            font-weight: 500;
            line-height: 1.6;
        }

        /* 🚀 Custom Primary Button Styling */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
            color: white !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            padding: 10px 20px !important;
            border-radius: 12px !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
            transition: all 0.3s ease !important;
        }
        div.stButton > button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5) !important;
            background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
        }

        /* ✨ Custom Secondary Button Styling (Demo Dataset) */
        div.stButton > button[kind="secondary"] {
            background: #FFFFFF !important;
            color: #4F46E5 !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            padding: 10px 20px !important;
            border-radius: 12px !important;
            border: 2px solid #C7D2FE !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1) !important;
            transition: all 0.3s ease !important;
        }
        div.stButton > button[kind="secondary"]:hover {
            transform: translateY(-2px) !important;
            background: #EEF2FF !important;
            border-color: #6366F1 !important;
            box-shadow: 0 6px 18px rgba(99, 102, 241, 0.2) !important;
        }
        
        /* General Card Base */
        .cap-card {
            border-radius: 16px;
            padding: 22px;
            height: 100%;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.6);
        }
        .cap-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
        }

        /* Specific Vibrant Card Color Gradients */
        .card-1 { background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); border-left: 5px solid #3B82F6; }
        .card-2 { background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%); border-left: 5px solid #22C55E; }
        .card-3 { background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%); border-left: 5px solid #EF4444; }
        .card-4 { background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%); border-left: 5px solid #F59E0B; }
        .card-5 { background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%); border-left: 5px solid #8B5CF6; }
        .card-6 { background: linear-gradient(135deg, #ECFEFF 0%, #CFFAFE 100%); border-left: 5px solid #06B6D4; }
        .card-7 { background: linear-gradient(135deg, #FDF2F8 0%, #FCE7F3 100%); border-left: 5px solid #EC4899; }
        .card-8 { background: linear-gradient(135deg, #F0FDFA 0%, #CCFBF1 100%); border-left: 5px solid #14B8A6; }
        .card-9 { background: linear-gradient(135deg, #FAF5FF 0%, #F3E8FF 100%); border-left: 5px solid #A855F7; }

        /* Card Numbers & Headers */
        .cap-card h4 {
            margin-top: 0;
            margin-bottom: 12px;
            color: #1E293B;
            font-size: 18px;
            display: flex;
            align-items: center;
        }
        .cap-num {
            color: white;
            font-weight: 800;
            padding: 4px 10px;
            border-radius: 8px;
            margin-right: 10px;
            font-size: 14px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .num-1 { background-color: #3B82F6; }
        .num-2 { background-color: #22C55E; }
        .num-3 { background-color: #EF4444; }
        .num-4 { background-color: #F59E0B; }
        .num-5 { background-color: #8B5CF6; }
        .num-6 { background-color: #06B6D4; }
        .num-7 { background-color: #EC4899; }
        .num-8 { background-color: #14B8A6; }
        .num-9 { background-color: #A855F7; }

        .cap-card p {
            color: #334155;
            font-size: 14px;
            line-height: 1.5;
            margin: 0;
        }

        /* 💳 Pricing Card Custom Styling */
        .price-card {
            background: #FFFFFF;
            border: 2px solid #E2E8F0;
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
            transition: all 0.3s ease;
        }
        .price-card:hover {
            border-color: #2563EB;
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(37,99,235,0.12);
        }
        .price-card-popular {
            border: 2px solid #2563EB !important;
            background: linear-gradient(180deg, #EFF6FF 0%, #FFFFFF 100%) !important;
            position: relative;
        }
        .popular-badge {
            background: #2563EB;
            color: white;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 12px;
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🚀 Home / Landing Page Interface (Side-by-Side Logo & Title)
# ==========================================
head_col1, head_col2 = st.columns([1, 4.5], gap="medium")

with head_col1:
    try:
        st.image("assets/logo.png", use_container_width=True)
    except Exception:
        pass

with head_col2:
    st.markdown("""
        <div class='brand-badge'>
            🚀 DataPilot AI — AI-Powered Data Analysis Platform
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='hero-title'>Turn your raw data into insights in minutes.</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Upload your CSV or Excel file and let DataPilot AI clean, analyze, visualize, and report your data automatically.</div>", unsafe_allow_html=True)

# 🚀 Action Buttons & Active File Banner
btn_col1, btn_col2, col_status = st.columns([1.3, 1.3, 2.4], gap="small")

with btn_col1:
    if st.button("🚀 Upload Dataset", type="primary", use_container_width=True):
        st.switch_page("pages/2_Upload.py")

with btn_col2:
    if st.button("✨ Try Demo Dataset", type="secondary", use_container_width=True):
        np.random.seed(42)
        dates = pd.date_range(start="2026-01-01", periods=120, freq="D")
        regions = ["North America", "Europe", "Asia-Pacific", "Latin America"]
        products = ["DataPilot Pro", "DataPilot Enterprise", "DataPilot Starter"]
        channels = ["Online", "Direct Sales", "Partner"]
        
        demo_df = pd.DataFrame({
            "Transaction_ID": [f"TRX-{2000+i}" for i in range(120)],
            "Date": dates,
            "Region": np.random.choice(regions, 120),
            "Product": np.random.choice(products, 120),
            "Sales_Channel": np.random.choice(channels, 120),
            "Sales_Amount": np.random.randint(250, 2500, 120),
            "Units_Sold": np.random.randint(1, 20, 120),
            "Customer_Rating": np.random.uniform(3.8, 5.0, 120).round(1)
        })
        
        st.session_state["df"] = demo_df
        st.session_state["file_name"] = "Demo_Sales_Dataset.csv"
        st.toast("⚡ Demo Dataset Loaded Successfully!", icon="🎉")
        st.rerun()

with col_status:
    if "df" in st.session_state and st.session_state["df"] is not None:
        file_name = st.session_state.get("file_name", "Dataset")
        df_shape = st.session_state["df"].shape
        st.success(f"📁 **Active Dataset:** {file_name} ({df_shape[0]:,} rows × {df_shape[1]} cols)")
    else:
        st.info("📂 **No Active Dataset:** Upload CSV or click 'Try Demo Dataset'.")

st.divider()

# ==========================================
# 🎨 Platform Capabilities & Data Pipeline Section
# ==========================================
st.subheader("🎨 Explore Platform Modules & Pipeline")

# --- Row 1 (Steps 1, 2, 3) ---
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class='cap-card card-1'>
        <h4><span class='cap-num num-1'>1</span> Upload & Inspect</h4>
        <p>Seamlessly ingest CSV and Excel files with automated encoding detection and structural verification.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class='cap-card card-2'>
        <h4><span class='cap-num num-2'>2</span> Data Overview</h4>
        <p>Power BI-style diagnostics featuring a Data Health Score (0-100), quality metrics, and descriptive stats.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class='cap-card card-3'>
        <h4><span class='cap-num num-3'>3</span> Advanced Cleaning</h4>
        <p>8-phase comprehensive sanitation: text normalization, word mapping, currency parsing, and outlier caps.</p>
    </div>
    """, unsafe_allow_html=True)

# --- Row 2 (Steps 4, 5, 6) ---
c4, c5, c6 = st.columns(3)
with c4:
    st.markdown("""
    <div class='cap-card card-4'>
        <h4><span class='cap-num num-4'>4</span> Feature Engineering</h4>
        <p>Perform feature scaling, categorical encoding, datetime extraction, and custom column engineering.</p>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown("""
    <div class='cap-card card-5'>
        <h4><span class='cap-num num-5'>5</span> Exploratory Analysis</h4>
        <p>Uncover patterns, correlations, distributions, and multi-variable trends via interactive Plotly charts.</p>
    </div>
    """, unsafe_allow_html=True)

with c6:
    st.markdown("""
    <div class='cap-card card-6'>
        <h4><span class='cap-num num-6'>6</span> Interactive Dashboard</h4>
        <p>Dynamic executive scorecards, KPI filters, treemaps, and custom scatter matrices.</p>
    </div>
    """, unsafe_allow_html=True)

# --- Row 3 (Steps 7, 8, 9) ---
c7, c8, c9 = st.columns(3)
with c7:
    st.markdown("""
    <div class='cap-card card-7'>
        <h4><span class='cap-num num-7'>7</span> AI Machine Learning</h4>
        <p>Train automated ML models (Regression/Classification), analyze feature drivers, and run Isolation Forest anomaly detection.</p>
    </div>
    """, unsafe_allow_html=True)

with c8:
    st.markdown("""
    <div class='cap-card card-8'>
        <h4><span class='cap-num num-8'>8</span> Executive Report Generator</h4>
        <p>Compile dataset metrics, cleaning audit logs, and summary stats into printable HTML reports.</p>
    </div>
    """, unsafe_allow_html=True)

with c9:
    st.markdown("""
    <div class='cap-card card-9'>
        <h4><span class='cap-num num-9'>9</span> Project Bundle Export</h4>
        <p>Package all cleaned CSV/Excel files, audit text logs, and JSON schema metadata into a single ZIP file.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==========================================
# 💎 Subscription Plans & USDT Payment
# ==========================================
st.subheader("💳 Subscription Plans & Pricing")
st.write("Choose the plan that fits your analytics needs. Unlock full AI capacity and unlimited processing.")

p1, p2, p3 = st.columns(3)

with p1:
    st.markdown("""
    <div class='price-card'>
        <h3>Monthly Plan</h3>
        <h1 style='color: #2563EB;'>$29 <span style='font-size: 14px; color: #64748B;'>/ mo</span></h1>
        <p style='color: #64748B;'>Flexible month-to-month access</p>
        <hr style='border: 0.5px solid #F1F5F9;'>
        <ul style='text-align: left; color: #334155; font-size: 14px; line-height: 2;'>
            <td> Full Pipeline Access</td><br>
            <td> Unlimited File Uploads</td><br>
            <td> Standard Processing Speed</td>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with p2:
    st.markdown("""
    <div class='price-card price-card-popular'>
        <div class='popular-badge'>MOST POPULAR</div>
        <h3>Semi-Annual Plan</h3>
        <h1 style='color: #2563EB;'>$140 <span style='font-size: 14px; color: #64748B;'>/ 6 mos</span></h1>
        <p style='color: #16A34A; font-weight: 700;'>Save 20%</p>
        <hr style='border: 0.5px solid #E2E8F0;'>
        <ul style='text-align: left; color: #334155; font-size: 14px; line-height: 2;'>
            <td> All Monthly Features</td><br>
            <td> High Priority AI Execution</td><br>
            <td> Priority Support</td>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with p3:
    st.markdown("""
    <div class='price-card'>
        <h3>Annual Plan</h3>
        <h1 style='color: #2563EB;'>$260 <span style='font-size: 14px; color: #64748B;'>/ year</span></h1>
        <p style='color: #16A34A; font-weight: 700;'>Best Value (Save 25%)</p>
        <hr style='border: 0.5px solid #F1F5F9;'>
        <ul style='text-align: left; color: #334155; font-size: 14px; line-height: 2;'>
            <td> Complete Enterprise Suite</td><br>
            <td> Dedicated 24/7 Support</td><br>
            <td> Early Access to New Features</td>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --- USDT Payment Box ---
with st.expander("⚡ **Pay via Binance / USDT (TRC-20)**", expanded=True):
    pay_col1, pay_col2 = st.columns([1.5, 2])
    
    with pay_col1:
        st.markdown("### 📱 USDT Payment Info")
        st.write("**Network:** TRON (TRC-20)")
        # استبدلي هذا العنوان بعنوان محفظتك المنسوخ من بايننس
        st.code("THoVn...DsnQT", language="text")
        st.caption(" Please make sure to transfer via TRC-20 network only.")
        
    with pay_col2:
        st.markdown("### 📝 Confirm Your Subscription")
        with st.form("home_subscription_form"):
            selected_plan = st.selectbox("Select Subscription Plan:", ["Monthly Plan ($29)", "Semi-Annual Plan ($140)", "Annual Plan ($260)"])
            user_email = st.text_input("Your Account Email:")
            tx_id = st.text_input("Transaction ID (TxID):", help="Paste the TxID from your Binance transfer receipt.")
            
            submit_payment = st.form_submit_button("Verify & Activate Subscription", type="primary")
            
            if submit_payment:
                if user_email and tx_id:
                    st.success("🎉 Payment details submitted successfully! Your plan will be activated within minutes after verification.")
                else:
                    st.error(" Please fill in both your email address and the Transaction ID (TxID).")

st.divider()
st.info("👈 Use the navigation sidebar on the left to start exploring your dataset!")
