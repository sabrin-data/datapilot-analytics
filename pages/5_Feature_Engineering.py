import streamlit as st
import pandas as pd
import numpy as np
from utils.translations import init_language, t

# ==========================================
# 0. Page Configuration & Language Init
# ==========================================
st.set_page_config(
    page_title="Feature Engineering Studio",
    page_icon="⚙️",
    layout="wide"
)

# 🔒 Paywall / Subscription Check (Freemium Gate)
from utils.paywall import check_subscription
check_subscription("Feature Engineering Studio")

# يقرأ اللغة المختارة ويظهر القائمة الجانبية
init_language()

# قراءة الـ CSS الموحد
try:
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("⚙️ Advanced Feature Engineering Studio")
st.write("Construct new predictive indicators, apply mathematical transformations, bin continuous variables, and encode features.")

# ==========================================
# 1. Check Dataset Availability
# ==========================================
if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("📂 Please upload a dataset first from the Upload page.")
    st.stop()

df = st.session_state["df"]
file_name = st.session_state.get("file_name", "Dataset")

st.info(f"📁 Active Dataset: **{file_name}** | Shape: **{df.shape[0]:,} rows × {df.shape[1]} columns**")
st.divider()

# Separate data types
num_cols = df.select_dtypes(include=np.number).columns.tolist()
cat_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()

# ==========================================
# 🧪 Module 1: Custom Advanced Multi-Column Formula
# ==========================================
with st.expander("🧪 Module 1: Custom Advanced Formula Builder (Multi-Column)", expanded=True):
    st.markdown("Write dynamic arithmetic formulas using exact column names. Example: `(Quantity * Price_Per_Unit) - Discount`")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        custom_formula = st.text_input(
            "Enter Formula Expression:", 
            placeholder="e.g. Quantity * Price_Per_Unit",
            key="custom_formula_expr"
        )
    with col2:
        new_custom_col_name = st.text_input(
            "New Column Name:", 
            value="Custom_Feature",
            key="custom_formula_col_name"
        )
        
    st.caption(f"📌 **Available Numeric Columns:** `{', '.join(num_cols)}`")

    if st.button("⚡ Apply Advanced Formula", type="primary", key="btn_apply_formula"):
        if not custom_formula.strip():
            st.warning("Please enter a valid formula expression.")
        elif new_custom_col_name in df.columns:
            st.error("⚠️ Column name already exists. Please enter a unique name.")
        else:
            try:
                df[new_custom_col_name] = df.eval(custom_formula)
                st.session_state["df"] = df
                st.success(f"🎉 Successfully created column `{new_custom_col_name}` using formula: `{custom_formula}`!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error evaluating formula. Details: {e}")

# ==========================================
# 🛠️ Module 2: Quick Two-Column Math Creator
# ==========================================
with st.expander("➕ Module 2: Quick Calculated Column (A op B)"):
    if len(num_cols) >= 2:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            col_a = st.selectbox("Select First Column (A)", num_cols, key="math_col_a_key")
        with c2:
            op = st.selectbox("Select Operation", ["Add (+)", "Subtract (-)", "Multiply (*)", "Divide (/)"], key="math_op_key")
        with c3:
            col_b = st.selectbox("Select Second Column (B)", num_cols, key="math_col_b_key")
        with c4:
            new_col_name = st.text_input("New Column Name", value=f"{col_a}_{op[0].lower()}", key="math_new_col_key")

        if st.button("✨ Construct Calculated Feature", type="primary", key="btn_construct_a_b"):
            if new_col_name in df.columns:
                st.error("⚠️ Column name already exists. Please enter a unique name.")
            else:
                if "Add" in op:
                    df[new_col_name] = df[col_a] + df[col_b]
                elif "Subtract" in op:
                    df[new_col_name] = df[col_a] - df[col_b]
                elif "Multiply" in op:
                    df[new_col_name] = df[col_a] * df[col_b]
                elif "Divide" in op:
                    df[new_col_name] = np.where(df[col_b] != 0, df[col_a] / df[col_b], np.nan)

                st.session_state["df"] = df
                st.success(f"🎉 Created feature `{new_col_name}` successfully!")
                st.rerun()
    else:
        st.info("At least two numeric columns are required for custom arithmetic feature construction.")

# ==========================================
# 📊 Module 3: Binning & Discretization
# ==========================================
with st.expander("📦 Module 3: Feature Binning / Quantilization (Continuous to Categorical)"):
    if num_cols:
        b1, b2, b3 = st.columns(3)
        with b1:
            bin_target = st.selectbox("Select Numeric Column to Bin", num_cols, key="bin_target_key")
        with b2:
            num_bins = st.slider("Number of Bins / Groups", min_value=2, max_value=10, value=3, key="num_bins_slider_key")
        with b3:
            bin_col_name = st.text_input("Binned Column Name", value=f"{bin_target}_Group", key="bin_col_name_input_key")

        bin_labels_str = st.text_input("Custom Group Labels (Comma Separated - Optional)", placeholder="Low, Medium, High", key="bin_labels_input_key")

        if st.button("📦 Generate Binned Feature", key="btn_bin_feature"):
            try:
                if bin_labels_str.strip():
                    labels = [l.strip() for l in bin_labels_str.split(",")]
                    if len(labels) != num_bins:
                        st.error(f"⚠️ Label count ({len(labels)}) must match number of bins ({num_bins}).")
                        st.stop()
                else:
                    labels = [f"Group_{i+1}" for i in range(num_bins)]

                try:
                    df[bin_col_name] = pd.qcut(df[bin_target], q=num_bins, labels=labels, duplicates="drop")
                except ValueError:
                    df[bin_col_name] = pd.cut(df[bin_target], bins=num_bins, labels=labels)

                st.session_state["df"] = df
                st.success(f"🎉 Created binned column `{bin_col_name}`!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to bin feature: {str(e)}")
    else:
        st.info("No numeric columns available for binning.")

# ==========================================
# 📐 Module 4: Mathematical Transformations
# ==========================================
with st.expander("📐 Module 4: Mathematical Transformations (Skew Reduction)"):
    if num_cols:
        t1, t2 = st.columns(2)
        with t1:
            trans_col = st.selectbox("Select Column to Transform", num_cols, key="trans_col_key")
        with t2:
            trans_type = st.selectbox("Select Transformation", ["Log Transformation (log1p)", "Square Root (sqrt)", "Absolute Value (abs)"], key="trans_type_key")

        if st.button("📐 Apply Transformation", key="btn_apply_transform"):
            trans_name = f"{trans_col}_{trans_type.split()[0].lower()}"
            if "Log" in trans_type:
                df[trans_name] = np.log1p(np.maximum(0, df[trans_col]))
            elif "Square Root" in trans_type:
                df[trans_name] = np.sqrt(np.maximum(0, df[trans_col]))
            elif "Absolute" in trans_type:
                df[trans_name] = np.abs(df[trans_col])

            st.session_state["df"] = df
            st.success(f"🎉 Created transformed feature `{trans_name}`!")
            st.rerun()
    else:
        st.info("No numeric columns available for mathematical transformations.")

# ==========================================
# 🏷️ Module 5: Categorical Encoding & Feature Scaling
# ==========================================
with st.expander("🏷️ Module 5: Categorical Encoding & Feature Scaling"):
    e1, e2 = st.columns(2)
    
    with e1:
        st.markdown("##### **Categorical Encoding**")
        if cat_cols:
            encode_target = st.selectbox("Select Categorical Column", cat_cols, key="encode_target_col_key")
            encode_method = st.radio("Encoding Method", ["One-Hot Encoding (Dummy Variables)", "Ordinal / Label Encoding"], key="encode_method_radio_key")
            
            if st.button("🏷️ Apply Encoding", key="btn_apply_encode"):
                if "One-Hot" in encode_method and df[encode_target].nunique() > 50:
                    st.error(f"⚠️ Column `{encode_target}` has too many unique values ({df[encode_target].nunique()}). One-Hot Encoding disabled.")
                else:
                    if "One-Hot" in encode_method:
                        df = pd.get_dummies(df, columns=[encode_target], drop_first=True, dtype=int)
                    else:
                        df[f"{encode_target}_encoded"] = df[encode_target].astype("category").cat.codes
                    
                    st.session_state["df"] = df
                    st.success(f"🎉 Encoded `{encode_target}` successfully!")
                    st.rerun()
        else:
            st.info("No categorical columns available for encoding.")

    with e2:
        st.markdown("##### **Feature Scaling**")
        if num_cols:
            scale_target = st.multiselect("Select Numeric Columns to Scale", num_cols, key="scale_target_cols_key")
            scale_method = st.radio("Scaling Strategy", ["MinMax Scaling (0 to 1)", "Standardization (Z-Score)"], key="scale_method_radio_key")

            if st.button("⚖️ Apply Scaling", key="btn_apply_scale"):
                if scale_target:
                    for col in scale_target:
                        if "MinMax" in scale_method:
                            min_val = df[col].min()
                            max_val = df[col].max()
                            if max_val != min_val:
                                df[f"{col}_minmax"] = (df[col] - min_val) / (max_val - min_val)
                        else:
                            mean_val = df[col].mean()
                            std_val = df[col].std()
                            if std_val != 0:
                                df[f"{col}_zscore"] = (df[col] - mean_val) / std_val

                    st.session_state["df"] = df
                    st.success("🎉 Scaling applied successfully!")
                    st.rerun()
                else:
                    st.warning("Select at least one numeric column to scale.")
        else:
            st.info("No numeric columns available for scaling.")

st.divider()

# Preview updated dataset
st.subheader("👀 Current Dataset Preview (Post Feature Engineering)")
st.dataframe(df.head(10), use_container_width=True)

# Transition button
col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
with col_b2:
    if st.button("Proceed to Exploratory Data Analysis (EDA) ➔", type="primary", use_container_width=True, key="btn_proceed_eda"):
        st.switch_page("pages/6_Data_Analysis.py")