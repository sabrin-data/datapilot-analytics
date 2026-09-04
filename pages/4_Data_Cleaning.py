import streamlit as st
import pandas as pd
import numpy as np
import re
from utils.translations import init_language, t

# ==========================================
# 0. Page Configuration & Language Init
# ==========================================
st.set_page_config(
    page_title="Data Sanitation Engine",
    page_icon="🧹",
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

st.title("🧹 Advanced Data Cleaning & Sanitation Engine")
st.write("Comprehensive data sanitation, text standardization, currency parsing, and outlier treatment.")

# ==========================================
# 1. Check Dataset Availability & State Setup
# ==========================================
if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("📂 Please upload a dataset or select the Demo Dataset from the Home / Upload page first.")
    
    col_nav1, col_nav2 = st.columns([1, 1])
    with col_nav1:
        if st.button("🏠 Go to Home Page", type="primary", use_container_width=True):
            st.switch_page("Home.py")
    with col_nav2:
        if st.button("📤 Go to Upload Page", type="secondary", use_container_width=True):
            st.switch_page("pages/2_Upload.py")
            
    st.stop()

# Backup copy for resetting capabilities
if "original_df" not in st.session_state or st.session_state["original_df"] is None:
    st.session_state["original_df"] = st.session_state["df"].copy()

df = st.session_state["df"]
file_name = st.session_state.get("file_name", "Active_Dataset.csv")

# Header status bar & reset button
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.success(f"📁 Active File: **{file_name}** | Current Shape: **{df.shape[0]:,} rows × {df.shape[1]} columns**")
with col_h2:
    if st.button("🔄 Reset to Original Dataset", type="secondary", use_container_width=True):
        st.session_state["df"] = st.session_state["original_df"].copy()
        if "cleaning_log" in st.session_state:
            del st.session_state["cleaning_log"]
        st.success("Dataset successfully reset to original state!")
        st.rerun()

st.divider()

# ==========================================
# 🤖 Smart AI Audit & Data Validation
# ==========================================
st.subheader("🤖 Smart Data Health Audit & AI Recommendations")

ai_suggestions = []
single_val_cols = [c for c in df.columns if df[c].nunique(dropna=False) == 1]
high_null_cols = [c for c in df.columns if (df[c].isnull().sum() / len(df)) > 0.9]

text_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
num_as_str_cols = []
for c in text_cols:
    sample = df[c].dropna().astype(str)
    cleaned_sample = sample.str.replace(r"[$,₪,€,%,£]", "", regex=True)
    if not cleaned_sample.empty and cleaned_sample.str.replace(".", "", regex=False).str.isnumeric().all():
        num_as_str_cols.append(c)

if single_val_cols:
    ai_suggestions.append(f"⚠️ **Constant Columns Detected:** `{single_val_cols}` contain only 1 unique value. Dropping is recommended.")
if high_null_cols:
    ai_suggestions.append(f"🔴 **High Missing Rate:** `{high_null_cols}` are >90% empty. Consider dropping them.")
if num_as_str_cols:
    ai_suggestions.append(f"💡 **Numbers Stored as Text:** `{num_as_str_cols}` appear to be numeric formatted as text or currency.")

if ai_suggestions:
    for sug in ai_suggestions:
        st.info(sug)
else:
    st.success("✅ Smart Audit: No critical structural anomalies detected!")

st.divider()

# ==========================================
# ⚙️ Cleaning Configuration Options
# ==========================================
st.subheader("⚙️ Select Sanitation Rules")

# --- Phase 1: Structural & Missing ---
with st.expander("🧹 Phase 1: Structural & Missing Values Handling", expanded=True):
    col_p1_1, col_p1_2 = st.columns(2)
    with col_p1_1:
        drop_dup_rows = st.checkbox("Remove Duplicate Rows", value=True, key="chk_drop_dup_rows")
        drop_dup_cols = st.checkbox("Remove Duplicate Columns", key="chk_drop_dup_cols")
        drop_empty_rows = st.checkbox("Drop Completely Empty Rows", value=True, key="chk_drop_empty_rows")
        drop_empty_cols = st.checkbox("Drop Completely Empty Columns", value=True, key="chk_drop_empty_cols")
    with col_p1_2:
        fill_num_method = st.selectbox(
            "Numeric Missing Strategy",
            ["Do Nothing", "Fill with Mean", "Fill with Median", "Fill with 0", "Drop Rows with Missing"],
            key="sel_fill_num_method"
        )
        fill_cat_method = st.selectbox(
            "Categorical Missing Strategy",
            ["Do Nothing", "Fill with Mode (Most Frequent)", "Fill with 'Unknown'", "Drop Rows with Missing"],
            key="sel_fill_cat_method"
        )

# --- Phase 2: Text Standardization ---
with st.expander("🔤 Phase 2: Text Sanitation & Value Standardization"):
    col_p2_1, col_p2_2 = st.columns(2)
    with col_p2_1:
        strip_spaces = st.checkbox("Remove Leading & Trailing Spaces", value=True, key="chk_strip_spaces")
        remove_extra_spaces = st.checkbox("Normalize Multiple Internal Whitespaces", value=True, key="chk_remove_extra_spaces")
        case_transform = st.selectbox("Text Case Transformation", ["Do Nothing", "UPPERCASE", "lowercase", "Title Case"], key="sel_case_transform")
    with col_p2_2:
        standardize_common = st.checkbox("Standardize Equivalent Values", value=True, help="Unifies variations like 'm/male/MALE' -> 'Male', 'y/yes/YES' -> 'Yes', 'USA/U.S.A' -> 'United States'", key="chk_standardize_common")
        text_cols_selected = st.multiselect("Apply to Specific Text Columns (Leave empty for ALL)", text_cols, key="ms_text_cols_selected")

# --- Phase 3: Numeric Sanitation ---
with st.expander("🔢 Phase 3: Numeric Sanitation (Currencies, Symbols & Percentages)"):
    col_p3_1, col_p3_2 = st.columns(2)
    with col_p3_1:
        clean_currency_symbols = st.checkbox("Remove Currency Symbols ($, €, ₪, £, etc.) & Commas", key="chk_clean_currency_symbols")
        clean_percentages = st.checkbox("Convert Percentage Strings ('12%') to Decimal (0.12)", key="chk_clean_percentages")
    with col_p3_2:
        remove_negatives = st.checkbox("Handle Negative Values (Replace with NaN)", key="chk_remove_negatives")
        auto_convert_num_str = st.checkbox("Auto-Convert Numeric Strings to Float/Integer", value=True, key="chk_auto_convert_num_str")

# --- Phase 4: Date Standardization ---
with st.expander("📅 Phase 4: Date Parsing & Feature Extraction"):
    col_p4_1, col_p4_2 = st.columns(2)
    with col_p4_1:
        auto_parse_dates = st.checkbox("Auto-Detect and Convert Date Formats", key="chk_auto_parse_dates")
        date_target_cols = st.multiselect("Select Target Date Columns", df.columns.tolist(), key="ms_date_target_cols")
    with col_p4_2:
        extract_date_parts = st.checkbox("Extract Date Components (Year, Month, Day, Day Name)", key="chk_extract_date_parts")

# --- Phase 5: Outlier Management ---
with st.expander("📊 Phase 5: Outlier Detection & Treatment (IQR Method)"):
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    if num_cols:
        col_p7_1, col_p7_2 = st.columns(2)
        with col_p7_1:
            detect_outliers = st.checkbox("Enable Outlier Detection & Treatment", key="chk_detect_outliers")
            outlier_cols = st.multiselect("Select Columns for Outlier Treatment", num_cols, default=num_cols[:2] if len(num_cols) >= 2 else num_cols, key="ms_outlier_cols")
        with col_p7_2:
            outlier_action = st.selectbox(
                "Outlier Action",
                ["Cap Outliers (Winsorize to IQR Boundaries)", "Remove Outlier Rows", "Replace Outliers with Median"],
                key="sel_outlier_action"
            )
    else:
        st.info("No numerical attributes available for outlier analysis.")

st.divider()

# ==========================================
# 🚀 EXECUTION & CLEANING LOG GENERATION
# ==========================================
if st.button("🚀 Execute Comprehensive Cleaning", type="primary", use_container_width=True):

    cleaned_df = df.copy()
    cleaning_log = []

    # --- Phase 1 Execution ---
    if drop_dup_rows:
        b = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        rem = b - len(cleaned_df)
        if rem > 0:
            cleaning_log.append(f"✔ Removed **{rem:,}** duplicate rows.")

    if drop_dup_cols:
        b = cleaned_df.shape[1]
        cleaned_df = cleaned_df.loc[:, ~cleaned_df.columns.duplicated()]
        rem = b - cleaned_df.shape[1]
        if rem > 0:
            cleaning_log.append(f"✔ Removed **{rem}** duplicate columns.")

    if drop_empty_rows:
        b = len(cleaned_df)
        cleaned_df = cleaned_df.dropna(how="all")
        rem = b - len(cleaned_df)
        if rem > 0:
            cleaning_log.append(f"✔ Removed **{rem:,}** completely empty rows.")

    if drop_empty_cols:
        b = cleaned_df.shape[1]
        cleaned_df = cleaned_df.dropna(axis=1, how="all")
        rem = b - cleaned_df.shape[1]
        if rem > 0:
            cleaning_log.append(f"✔ Removed **{rem}** completely empty columns.")

    # --- Missing Values Execution ---
    curr_num_cols = cleaned_df.select_dtypes(include=np.number).columns
    if fill_num_method == "Fill with Mean":
        cleaned_df[curr_num_cols] = cleaned_df[curr_num_cols].fillna(cleaned_df[curr_num_cols].mean())
        cleaning_log.append("✔ Imputed missing numeric values using **Mean**.")
    elif fill_num_method == "Fill with Median":
        cleaned_df[curr_num_cols] = cleaned_df[curr_num_cols].fillna(cleaned_df[curr_num_cols].median())
        cleaning_log.append("✔ Imputed missing numeric values using **Median**.")
    elif fill_num_method == "Fill with 0":
        cleaned_df[curr_num_cols] = cleaned_df[curr_num_cols].fillna(0)
        cleaning_log.append("✔ Filled missing numeric values with **0**.")
    elif fill_num_method == "Drop Rows with Missing":
        b = len(cleaned_df)
        cleaned_df = cleaned_df.dropna(subset=curr_num_cols)
        cleaning_log.append(f"✔ Dropped **{b - len(cleaned_df):,}** rows containing numeric missing values.")

    curr_cat_cols = cleaned_df.select_dtypes(include=["object", "category", "string"]).columns
    if fill_cat_method == "Fill with Mode (Most Frequent)":
        for col in curr_cat_cols:
            if not cleaned_df[col].mode().empty:
                cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mode()[0])
        cleaning_log.append("✔ Imputed missing categorical values using **Mode**.")
    elif fill_cat_method == "Fill with 'Unknown'":
        cleaned_df[curr_cat_cols] = cleaned_df[curr_cat_cols].fillna("Unknown")
        cleaning_log.append("✔ Filled missing categorical values with **'Unknown'**.")

    # --- Phase 2 Execution (Text Sanitation) ---
    target_str_cols = text_cols_selected if text_cols_selected else curr_cat_cols.tolist()

    for col in target_str_cols:
        if col in cleaned_df.columns:
            s = cleaned_df[col].astype(str)

            if strip_spaces:
                s = s.str.strip()
            if remove_extra_spaces:
                s = s.str.replace(r"\s+", " ", regex=True)

            if case_transform == "UPPERCASE":
                s = s.str.upper()
            elif case_transform == "lowercase":
                s = s.str.lower()
            elif case_transform == "Title Case":
                s = s.str.title()

            if standardize_common:
                gender_map = {r"(?i)^(male|m|males)$": "Male", r"(?i)^(female|f|females)$": "Female"}
                bool_map = {r"(?i)^(yes|y|true|t|1)$": "Yes", r"(?i)^(no|n|false|f|0)$": "No"}
                country_map = {r"(?i)^(usa|u\.s\.a|united states|us)$": "United States", r"(?i)^(uk|u\.k|united kingdom)$": "United Kingdom"}

                full_map = {**gender_map, **bool_map, **country_map}

                for pattern, replacement in full_map.items():
                    s = s.replace(pattern, replacement, regex=True)

            cleaned_df[col] = s

    if strip_spaces or remove_extra_spaces:
        cleaning_log.append("✔ Normalized whitespaces (Leading, trailing, and internal).")
    if case_transform != "Do Nothing":
        cleaning_log.append(f"✔ Standardized text case transformation to **{case_transform}**.")
    if standardize_common:
        cleaning_log.append("✔ Unified word variations (Gender, Boolean, and Country codes).")

    # --- Phase 3 Execution (Numeric Sanitation) ---
    if clean_currency_symbols or clean_percentages or auto_convert_num_str:
        for col in target_str_cols:
            if col in cleaned_df.columns:
                series_str = cleaned_df[col].astype(str)

                if clean_currency_symbols:
                    series_str = series_str.str.replace(r"[$,₪,€,£,]", "", regex=True)

                if clean_percentages:
                    has_pct = series_str.str.contains("%", na=False)
                    series_str = series_str.str.replace("%", "", regex=False)

                converted = pd.to_numeric(series_str, errors="coerce")

                if converted.notnull().sum() > 0.5 * len(cleaned_df):
                    if clean_percentages:
                        converted = np.where(has_pct, converted / 100.0, converted)

                    cleaned_df[col] = converted

        cleaning_log.append("✔ Cleaned currency symbols, commas, and percentage strings into numeric dtypes.")

    if remove_negatives:
        for col in cleaned_df.select_dtypes(include=np.number).columns:
            cleaned_df[col] = np.where(cleaned_df[col] < 0, np.nan, cleaned_df[col])
        cleaning_log.append("✔ Replaced negative values with NaN across numeric columns.")

    # --- Phase 4 Execution (Date Sanitation) ---
    date_cols_process = date_target_cols if date_target_cols else []
    if auto_parse_dates and not date_cols_process:
        for c in cleaned_df.columns:
            if "date" in c.lower() or "time" in c.lower() or "day" in c.lower():
                date_cols_process.append(c)

    for d_col in date_cols_process:
        if d_col in cleaned_df.columns:
            parsed_dates = pd.to_datetime(cleaned_df[d_col], errors="coerce")
            if parsed_dates.notnull().sum() > 0:
                cleaned_df[d_col] = parsed_dates

                if extract_date_parts:
                    cleaned_df[f"{d_col}_Year"] = parsed_dates.dt.year
                    cleaned_df[f"{d_col}_Month"] = parsed_dates.dt.month
                    cleaned_df[f"{d_col}_DayName"] = parsed_dates.dt.day_name()

    if date_cols_process:
        cleaning_log.append(f"✔ Standardized date formats for `{date_cols_process}`.")

    # --- Outliers IQR Execution ---
    if 'detect_outliers' in locals() and detect_outliers and outlier_cols:
        total_outliers = 0
        for o_col in outlier_cols:
            if o_col in cleaned_df.columns:
                Q1 = cleaned_df[o_col].quantile(0.25)
                Q3 = cleaned_df[o_col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                outliers_mask = (cleaned_df[o_col] < lower_bound) | (cleaned_df[o_col] > upper_bound)
                cnt = int(outliers_mask.sum())
                total_outliers += cnt

                if outlier_action == "Cap Outliers (Winsorize to IQR Boundaries)":
                    cleaned_df[o_col] = np.clip(cleaned_df[o_col], lower_bound, upper_bound)
                elif outlier_action == "Remove Outlier Rows":
                    cleaned_df = cleaned_df[~outliers_mask]
                elif outlier_action == "Replace Outliers with Median":
                    med_val = cleaned_df[o_col].median()
                    cleaned_df.loc[outliers_mask, o_col] = med_val

        cleaning_log.append(f"✔ Handled **{total_outliers:,}** outlier points across `{outlier_cols}` using strategy: **{outlier_action}**.")

    # Save to Session State
    st.session_state["df"] = cleaned_df
    st.session_state["cleaning_log"] = cleaning_log

    st.success("🎉 Dataset Sanitation Completed Successfully!")
    st.balloons()
    st.rerun()

# ==========================================
# 📋 Cleaning Log & Export Output
# ==========================================
if "cleaning_log" in st.session_state and st.session_state["cleaning_log"]:
    st.divider()
    st.subheader("📋 Cleaning Log Audit Trail")

    for log_item in st.session_state["cleaning_log"]:
        st.markdown(log_item)

    st.divider()
    st.subheader("👀 Preview Cleaned Dataset")
    st.dataframe(df.head(10), use_container_width=True)

    csv_data = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="⬇️ Download Cleaned Dataset (CSV)",
        data=csv_data,
        file_name=f"cleaned_{file_name}.csv",
        mime="text/csv",
        type="primary"
    )
