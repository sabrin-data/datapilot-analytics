import io
import chardet
import pandas as pd
import streamlit as st
from utils.translations import init_language, t

# ==========================================
# 0. Page Configuration & Language Init
# ==========================================
st.set_page_config(
    page_title="Dataset Ingestion & Upload",
    page_icon="📂",
    layout="wide"
)

init_language()

try:
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("📂 Dataset Ingestion & Validation")
st.write(t("sub_title") if t("sub_title") != "sub_title" else "Upload your dataset in CSV or Excel format to initialize the automated data pipeline.")

st.divider()

# ==========================================
# 1. Helper Function: Safe File Loader
# ==========================================
def load_dataset(uploaded_file):
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
    try:
        with st.spinner("Parsing dataset and verifying structural integrity..."):
            df, filename, used_encoding = load_dataset(uploaded_file)

        st.session_state["df"] = df.copy()
        st.session_state["original_df"] = df.copy()
        st.session_state["file_name"] = filename
        st.session_state["cleaning_log"] = []  

        st.success(f"🎉 Dataset **'{filename}'** successfully uploaded and loaded into active memory!")

        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("📊 Total Rows", f"{len(df):,}")
        m_col2.metric("📊 Total Columns", df.shape[1])
        m_col3.metric("🔤 Detected Encoding", used_encoding)
        m_col4.metric("💾 Memory Footprint", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")

        st.divider()

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

        c_space, c_btn, c_space2 = st.columns([1, 2, 1])
        with c_btn:
            if st.button("Proceed to Data Overview ➔", type="primary", use_container_width=True):
                st.switch_page("pages/3_Data_Overview.py")

    except Exception as e:
        st.error(f"❌ Failed to parse file: {str(e)}")

else:
    if "df" in st.session_state and st.session_state["df"] is not None:
        st.info(f"📁 Active Dataset in Memory: **{st.session_state.get('file_name', 'Dataset')}** ({st.session_state['df'].shape[0]:,} rows × {st.session_state['df'].shape[1]} columns)")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Continue with Active Dataset ➔", type="primary", use_container_width=True):
                st.switch_page("pages/3_Data_Overview.py")
        with c2:
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
