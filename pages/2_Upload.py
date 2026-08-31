import io
import chardet
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from utils.translations import init_language, t

# ==========================================
# 0. Page Configuration & Language Init
# ==========================================
st.set_page_config(
    page_title="Dataset Ingestion & Upload",
    page_icon="📂",
    layout="wide"
)

# يقرأ اللغة المختارة ويظهر القائمة الجانبية
init_language()

# قراءة الـ CSS الموحد
try:
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("📂 Dataset Ingestion & Validation")
st.write(t("sub_title") if t("sub_title") != "sub_title" else "Upload your dataset in CSV or Excel format to initialize the automated data pipeline.")

st.divider()

# ==========================================
# 🔒 Paddle Paywall Configuration (شرط الدفع والاشتراك لرفع الملفات)
# ==========================================
PADDLE_CLIENT_TOKEN = "live_348aab7f372a0cc9cce3a87e467"
PRICE_MONTHLY = "pri_01m19xbb6ktbg8y28k9p5dvjyh"
PRICE_6MONTHS = "pri_01m19x6w138sn1sr3cnjfn90cn"
PRICE_ANNUAL = "pri_01m19x068bamgcp9agk0rcf9h4"

def render_paddle_checkout_wall():
    st.markdown("""
        <div style="background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%); border: 2px solid #EF4444; border-radius: 16px; padding: 30px; text-align: center; margin: 20px 0; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.15);">
            <h2 style="color: #991B1B; margin-top: 0;">🔒 Subscription Required to Upload Custom Files</h2>
            <p style="color: #7F1D1D; font-size: 16px; margin-bottom: 20px;">
                To upload and process your personal datasets from your computer, an active DataPilot AI subscription is required. Choose a plan below to unlock full access.
            </p>
        </div>
    """, unsafe_allow_html=True)

    def render_paywall_paddle_button(price_id, button_text):
        html_code = f"""
        <script src="https://cdn.paddle.com/paddle/v2/paddle.js"></script>
        <script>
         Paddle.Environment.set('live'); 
         Paddle.Initialize({{ token: '{PADDLE_CLIENT_TOKEN}' }});

         function openCheckout() {{
           Paddle.Checkout.open({{
             items: [{{ priceId: '{price_id}', quantity: 1 }}]
           }});
         }}
        </script>
        <button onclick="openCheckout()" style="
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            font-size: 15px;
            width: 100%;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
            transition: all 0.3s ease;
        ">
            {button_text}
        </button>
        """
        components.html(html_code, height=60)

    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        st.markdown("""
        <div class='price-card' style='background: #fff; border: 1px solid #cbd5e1; border-radius: 12px; padding: 20px; text-align: center;'>
            <h3>Monthly</h3>
            <div style='font-size: 28px; font-weight: bold; color: #0f172a; margin: 10px 0;'>$29</div>
        </div>
        """, unsafe_allow_html=True)
        render_paywall_paddle_button(PRICE_MONTHLY, "Subscribe Monthly")

    with p_col2:
        st.markdown("""
        <div class='price-card' style='background: #fff; border: 2px solid #2563EB; border-radius: 12px; padding: 20px; text-align: center;'>
            <h3>6-Month</h3>
            <div style='font-size: 28px; font-weight: bold; color: #2563EB; margin: 10px 0;'>$140</div>
        </div>
        """, unsafe_allow_html=True)
        render_paywall_paddle_button(PRICE_6MONTHS, "Subscribe 6 Months")

    with p_col3:
        st.markdown("""
        <div class='price-card' style='background: #fff; border: 1px solid #cbd5e1; border-radius: 12px; padding: 20px; text-align: center;'>
            <h3>Annual</h3>
            <div style='font-size: 28px; font-weight: bold; color: #0f172a; margin: 10px 0;'>$260</div>
        </div>
        """, unsafe_allow_html=True)
        render_paywall_paddle_button(PRICE_ANNUAL, "Subscribe Annually")

# التحقق من حالة الاشتراك في الجلسة
is_subscribed = st.session_state.get("is_subscribed", False)

# ==========================================
# 1. Helper Function: Safe File Loader
# ==========================================
def load_dataset(uploaded_file):
    """Loads CSV or Excel files with automatic encoding detection."""
    filename = uploaded_file.name
    
    if filename.endswith(".csv"):
        raw_bytes = uploaded_file.getvalue()
        detected = chardet.detect(raw_bytes[:50000])  
        encoding_detected = detected.get("encoding", "utf-8")
        
        encodings_to_try = [encoding_detected, "utf-8", "utf-8-sig", "latin1", "cp1252", "iso-8859-1"]
        
        for enc in encodings_to_try:
            if not enc:
                continue
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding=enc)
                return df, filename, enc
            except (UnicodeDecodeError, Exception):
                continue
        
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding="utf-8", errors="replace")
        return df, filename, "utf-8 (coerced)"

    elif filename.endswith((".xlsx", ".xls")):
        uploaded_file.seek(0)
        df = pd.read_excel(uploaded_file)
        return df, filename, "Excel Native"
    
    else:
        raise ValueError("Unsupported file format. Please upload a .csv, .xlsx, or .xls file.")

# ==========================================
# 2. File Upload Widget & Processing
# ==========================================
uploaded_file = st.file_uploader(
    "Choose a file from your computer", 
    type=["csv", "xlsx", "xls"],
    help="Supported formats: CSV, Excel (.xlsx, .xls)"
)

if uploaded_file is not None:
    # إذا حاول رفع ملف ولم يكن مشتركاً ولم يضغط على زر محاكاة الاشتراك في الهوم
    if not is_subscribed:
        render_paddle_checkout_wall()
        st.stop()  # إيقاف التنفيذ لمنع رفع الملف

    try:
        with st.spinner("Parsing dataset and verifying structural integrity..."):
            df, filename, used_encoding = load_dataset(uploaded_file)

        # حفظ البيانات في الـ Session State
        st.session_state["df"] = df.copy()
        st.session_state["original_df"] = df.copy()
        st.session_state["file_name"] = filename
        st.session_state["cleaning_log"] = []  

        st.success(f"🎉 Dataset **'{filename}'** successfully uploaded and loaded into active memory!")

        # إحصائيات سريعة
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("📊 Total Rows", f"{len(df):,}")
        m_col2.metric("📊 Total Columns", df.shape[1])
        m_col3.metric("🔤 Detected Encoding", used_encoding)
        m_col4.metric("💾 Memory Footprint", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")

        st.divider()

        # معاينة سريعة
        st.subheader("🔍 Initial Structural Verification")
        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown("##### **First 5 Rows Preview**")
            st.dataframe(df.head(), use_container_width=True)

        with col_right:
            st.markdown("##### **Column Dtypes & Null Count**")
            schema_df = pd.DataFrame({
                "Column Name": df.columns,
                "Data Type": df.dtypes.astype(str),
                "Missing Values": df.isnull().sum().values
            })
            st.dataframe(schema_df, use_container_width=True, height=220)

        st.divider()

        # زر المتابعة
        c_space, c_btn, c_space2 = st.columns([1, 2, 1])
        with c_btn:
            if st.button("Proceed to Data Overview ➔", type="primary", use_container_width=True):
                st.switch_page("pages/3_Data_Overview.py")

    except Exception as e:
        st.error(f"❌ Failed to parse file: {str(e)}")

else:
    # التحقق من وجود بيانات مسبقة (مثل ملف الديمو أو ملف مرفوع سابقاً)
    if "df" in st.session_state and st.session_state["df"] is not None:
        st.info(f"📁 Active Dataset in Memory: **{st.session_state.get('file_name', 'Dataset')}** ({st.session_state['df'].shape[0]:,} rows × {st.session_state['df'].shape[1]} columns)")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Continue with Active Dataset ➔", type="primary", use_container_width=True):
                st.switch_page("pages/3_Data_Overview.py")
        with c2:
            # زر لتحميل النسخة الحالية المعالجة كملف CSV (تعديل الـ Download)
            csv_data = st.session_state["df"].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Current Dataset (CSV)",
                data=csv_data,
                file_name=st.session_state.get('file_name', 'datapilot_export.csv'),
                mime='text/csv',
                use_container_width=True
            )
    else:
        st.warning("👈 Please upload a file above or try the Demo Dataset from the Home page to unlock the analysis pipeline.")
