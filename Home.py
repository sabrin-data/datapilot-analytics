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

# 🌐 1. Initialize Language & Sidebar Selector
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
        </style>
    """, unsafe_allow_html=True)

# Custom Styling
st.markdown("""
    <style>
        [data-testid="stSidebar"] img { display: none !important; }
        [data-testid="stSidebarNav"] * { font-weight: 700 !important; color: #0F172A !important; }
        
        .brand-badge {
            background-color: #eef2ff; color: #4f46e5; font-weight: 700;
            font-size: 0.9rem; padding: 6px 14px; border-radius: 20px;
            border: 1px solid #c7d2fe; display: inline-block; margin-bottom: 10px;
        }
        .hero-title {
            font-size: 38px; font-weight: 800;
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #8B5CF6 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 8px; line-height: 1.25;
        }
        .hero-subtitle { font-size: 16px; color: #475569; margin-bottom: 25px; font-weight: 500; line-height: 1.6; }
        
        .price-card {
            background: #FFFFFF; border-radius: 16px; padding: 24px; text-align: center;
            border: 2px solid #E2E8F0; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        }
        .price-value { font-size: 32px; font-weight: 800; color: #0F172A; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🚀 Hero Section
# ==========================================
head_col1, head_col2 = st.columns([1, 4.5], gap="medium")
with head_col1:
    try:
        st.image("assets/logo.png", use_container_width=True)
    except Exception:
        pass
with head_col2:
    st.markdown("<div class='brand-badge'>🚀 DataPilot AI — AI-Powered Data Analysis Platform</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-title'>Turn your raw data into insights in minutes.</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Upload your CSV or Excel file and let DataPilot AI clean, analyze, visualize, and report your data automatically.</div>", unsafe_allow_html=True)

# تهيئة حالة الاشتراك في الجلسة
if "is_subscribed" not in st.session_state:
    st.session_state["is_subscribed"] = False

# التحقق مما إذا كان المستخدم مشتركاً أم لا
if st.session_state["is_subscribed"]:
    # حالة الاشتراك المفعل (عرض أزرار العمل ورفع البيانات)
    st.success("🎉 **Active Subscription:** You are subscribed to DataPilot AI Pro! All platform features are unlocked.")
    
    btn_col1, btn_col2, col_status = st.columns([1.3, 1.3, 2.4], gap="small")
    with btn_col1:
        if st.button("🚀 Upload Dataset", type="primary", use_container_width=True):
            st.switch_page("pages/2_Upload.py")

    with btn_col2:
        if st.button("✨ Try Demo Dataset", type="secondary", use_container_width=True):
            np.random.seed(42)
            dates = pd.date_range(start="2026-01-01", periods=120, freq="D")
            demo_df = pd.DataFrame({
                "Transaction_ID": [f"TRX-{2000+i}" for i in range(120)],
                "Date": dates,
                "Region": np.random.choice(["North America", "Europe", "Asia-Pacific"], 120),
                "Sales_Amount": np.random.randint(250, 2500, 120),
                "Units_Sold": np.random.randint(1, 20, 120),
            })
            st.session_state["df"] = demo_df
            st.session_state["file_name"] = "Demo_Sales_Dataset.csv"
            st.toast("⚡ Demo Dataset Loaded Successfully!", icon="🎉")
            st.switch_page("pages/3_Data_Overview.py")

    with col_status:
        if "df" in st.session_state and st.session_state["df"] is not None:
            file_name = st.session_state.get("file_name", "Dataset")
            df_shape = st.session_state["df"].shape
            st.success(f"📁 **Active Dataset:** {file_name} ({df_shape[0]:,} rows × {df_shape[1]} cols)")
        else:
            st.info("📂 **No Active Dataset:** Upload CSV or click 'Try Demo Dataset'.")

    st.divider()
    
    if st.button("🔒 Cancel / Reset Subscription (For Testing)"):
        st.session_state["is_subscribed"] = False
        st.rerun()

else:
    # حالة عدم الاشتراك (عرض خطط الأسعار وإجبار المستخدم على الاشتراك للاستخدام)
    st.warning("🔒 **Subscription Required:** Please choose a pricing plan below to unlock DataPilot AI features and start analyzing your data.")
    st.divider()
    
    st.subheader("💳 Flexible Pricing Plans")
    p_col1, p_col2, p_col3 = st.columns(3)

    with p_col1:
        st.markdown("""
        <div class='price-card'>
            <h3>Monthly Plan</h3>
            <div class='price-value'>$29 <span style='font-size: 14px; color: #64748B;'>/ mo</span></div>
            <p style='color: #64748B; font-size: 13px;'>Billed monthly.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Subscribe Monthly", key="btn_m", use_container_width=True):
            st.session_state["is_subscribed"] = True
            st.balloons()
            st.success("✨ Subscription Successful! Welcome to Pro.")
            st.rerun()

    with p_col2:
        st.markdown("""
        <div class='price-card' style='border-color: #2563EB; background: #F8FAFC;'>
            <span style='background: #2563EB; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;'>POPULAR</span>
            <h3 style='margin-top: 5px;'>6-Month Plan</h3>
            <div class='price-value'>$140 <span style='font-size: 14px; color: #64748B;'>/ 6 mo</span></div>
            <p style='color: #64748B; font-size: 13px;'>Save ~20%.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Subscribe 6 Months", key="btn_6m", use_container_width=True):
            st.session_state["is_subscribed"] = True
            st.balloons()
            st.success("✨ Subscription Successful! Welcome to Pro.")
            st.rerun()

    with p_col3:
        st.markdown("""
        <div class='price-card'>
            <h3>Annual Plan</h3>
            <div class='price-value'>$260 <span style='font-size: 14px; color: #64748B;'>/ yr</span></div>
            <p style='color: #64748B; font-size: 13px;'>Best value for teams.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Subscribe Annually", key="btn_yr", use_container_width=True):
            st.session_state["is_subscribed"] = True
            st.balloons()
            st.success("✨ Subscription Successful! Welcome to Pro.")
            st.rerun()

st.divider()
st.info("💡 DataPilot AI gives you automated insights, data cleaning, and instant AI analytics.")
