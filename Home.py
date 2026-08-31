import streamlit as st
from utils.translations import init_language, t

# ==========================================
# 0. Page Configuration & Language Init
# ==========================================
st.set_page_config(
    page_title="DataPilot AI — Platform Home",
    page_icon="🚀",
    layout="wide"
)

init_language()

# قراءة الـ CSS الموحد
try:
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# ==========================================
# Hero Section
# ==========================================
col_img, col_text = st.columns([1, 2.5], gap="large")

with col_img:
    try:
        st.image("assets/logo.png", use_container_width=True)
    except Exception:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); border-radius: 50%; width: 180px; height: 180px; display: flex; align-items: center; justify-content: center; margin: auto; box-shadow: 0 10px 25px rgba(37, 99, 235, 0.3);">
                <span style="font-size: 70px;">🚀</span>
            </div>
        """, unsafe_allow_html=True)

with col_text:
    st.markdown('<span style="background: #eff6ff; color: #2563EB; padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size: 13px;">✨ DataPilot AI — AI-Powered Data Analysis Platform</span>', unsafe_allow_html=True)
    st.title("Turn your raw data into insights in minutes.")
    st.markdown("Upload your CSV or Excel file and let **DataPilot AI** clean, analyze, visualize, and report your data automatically.")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# Quick Action Buttons & Status
# ==========================================
act_c1, act_c2, act_c3 = st.columns([1.2, 1.2, 1.8])

with act_c1:
    if st.button("🚀 Upload Dataset", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Upload.py")

with act_c2:
    if st.button("✨ Try Demo Dataset", use_container_width=True):
        import pandas as pd
        import numpy as np
        # تحميل بيانات ديمو افتراضية سريعة
        np.random.seed(42)
        demo_df = pd.DataFrame({
            "CustomerID": [f"CUST-{1000+i}" for i in range(100)],
            "Age": np.random.randint(18, 70, 100),
            "Income": np.random.randint(30000, 120000, 100),
            "Score": np.random.uniform(10, 100, 100),
            "Category": np.random.choice(["A", "B", "C"], 100)
        })
        st.session_state["df"] = demo_df.copy()
        st.session_state["original_df"] = demo_df.copy()
        st.session_state["file_name"] = "demo_dataset.csv"
        st.session_state["cleaning_log"] = []
        st.success("🎉 Demo dataset loaded successfully!")
        st.switch_page("pages/3_Data_Overview.py")

with act_c3:
    if "df" in st.session_state and st.session_state["df"] is not None:
        st.markdown(f'<div style="background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 10px 15px; border-radius: 8px; font-size: 14px; font-weight: 500;">📁 Active Dataset: <b>{st.session_state.get("file_name", "Dataset")}</b></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="background: #f8fafc; border: 1px solid #e2e8f0; color: #64748b; padding: 10px 15px; border-radius: 8px; font-size: 14px; font-weight: 500;">📂 No Active Dataset: Upload CSV or click \'Try Demo Dataset\'.</div>', unsafe_allow_html=True)

st.divider()

# ==========================================
# Explore Platform Modules & Pipeline
# ==========================================
st.subheader("🧭 Explore Platform Modules & Pipeline")

# الصف الأول من الموديولات
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown("""
    <div style='background: #eff6ff; border-left: 5px solid #2563EB; padding: 18px; border-radius: 10px; height: 140px;'>
        <h4 style='color: #1e3a8a; margin-top:0;'>1️⃣ Upload & Inspect</h4>
        <p style='color: #475569; font-size: 13px;'>Seamlessly ingest CSV and Excel files with automated encoding detection and structural verification.</p>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div style='background: #f0fdf4; border-left: 5px solid #16a34a; padding: 18px; border-radius: 10px; height: 140px;'>
        <h4 style='color: #14532d; margin-top:0;'>2️⃣ Data Overview</h4>
        <p style='color: #475569; font-size: 13px;'>Power BI-style diagnostics featuring a Data Health Score (0-100), quality metrics, and descriptive stats.</p>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div style='background: #fef2f2; border-left: 5px solid #dc2626; padding: 18px; border-radius: 10px; height: 140px;'>
        <h4 style='color: #7f1d1d; margin-top:0;'>3️⃣ Advanced Cleaning</h4>
        <p style='color: #475569; font-size: 13px;'>8-phase comprehensive sanitation: text normalization, word mapping, currency parsing, and outlier caps.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# الصف الثاني من الموديولات
m4, m5, m6 = st.columns(3)
with m4:
    st.markdown("""
    <div style='background: #fffbeb; border-left: 5px solid #d97706; padding: 18px; border-radius: 10px; height: 140px;'>
        <h4 style='color: #78350f; margin-top:0;'>4️⃣ Feature Engineering</h4>
        <p style='color: #475569; font-size: 13px;'>Perform feature scaling, categorical encoding, datetime extraction, and custom column engineering.</p>
    </div>
    """, unsafe_allow_html=True)

with m5:
    st.markdown("""
    <div style='background: #f5f3ff; border-left: 5px solid #7c3aed; padding: 18px; border-radius: 10px; height: 140px;'>
        <h4 style='color: #3b0764; margin-top:0;'>5️⃣ Exploratory Analysis</h4>
        <p style='color: #475569; font-size: 13px;'>Uncover patterns, correlations, distributions, and multi-variable trends via interactive Plotly charts.</p>
    </div>
    """, unsafe_allow_html=True)

with m6:
    st.markdown("""
    <div style='background: #ecfeff; border-left: 5px solid #0891b2; padding: 18px; border-radius: 10px; height: 140px;'>
        <h4 style='color: #164e63; margin-top:0;'>6️⃣ Interactive Dashboard</h4>
        <p style='color: #475569; font-size: 13px;'>Dynamic executive scorecards, KPI filters, treemaps, and custom scatter matrices.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# الصف الثالث من الموديولات
m7, m8, m9 = st.columns(3)
with m7:
    st.markdown("""
    <div style='background: #fff1f2; border-left: 5px solid #e11d48; padding: 18px; border-radius: 10px; height: 140px;'>
        <h4 style='color: #881337; margin-top:0;'>7️⃣ AI Analyst</h4>
        <p style='color: #475569; font-size: 13px;'>AI-powered insights, anomaly detection, automated summaries, and intelligent recommendations.</p>
    </div>
    """, unsafe_allow_html=True)

with m8:
    st.markdown("""
    <div style='background: #f0fdf4; border-left: 5px solid #059669; padding: 18px; border-radius: 10px; height: 140px;'>
        <h4 style='color: #064e3b; margin-top:0;'>8️⃣ Report Generator</h4>
        <p style='color: #475569; font-size: 13px;'>Professional PDF reports with charts, insights, KPIs, and executive summary sections.</p>
    </div>
    """, unsafe_allow_html=True)

with m9:
    st.markdown("""
    <div style='background: #faf5ff; border-left: 5px solid #9333ea; padding: 18px; border-radius: 10px; height: 140px;'>
        <h4 style='color: #581c87; margin-top:0;'>9️⃣ Export & Share</h4>
        <p style='color: #475569; font-size: 13px;'>Export cleaned data, dashboards, and reports. Share insights and collaborate effortlessly.</p>
    </div>
    """, unsafe_allow_html=True)
