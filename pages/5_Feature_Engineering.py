import streamlit as st
import pandas as pd
import numpy as np
from utils.translations import init_language, t

# ==========================================
# 0. Page Configuration
# ==========================================
st.set_page_config(
    page_title="Feature Engineering Studio",
    page_icon="🧪",
    layout="wide"
)

init_language()

try:
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("🧪 Feature Engineering Studio")
st.write("Create custom calculated columns, apply mathematical transformations, and encode variables.")

# ==========================================
# 1. Check Dataset
# ==========================================
if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("⚠️ Please upload a dataset first in the Upload page!")
    st.stop()

df = st.session_state["df"]

numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

# ==========================================
# Module 1: Custom Advanced Formula Builder
# ==========================================
with st.expander("📝 Module 1: Custom Advanced Formula Builder (Multi-Column)", expanded=True):
    st.write("Write dynamic arithmetic formulas using exact column names. Example: `(Quantity * Price_Per_Unit) - Discount`")
    
    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        formula_expr = st.text_input("Enter Formula Expression:", placeholder="Total Spent * 1.10")
    with f_col2:
        new_col_name = st.text_input("New Column Name:", value="Custom_Feature")

    if numeric_cols:
        st.caption(f"📌 Available Numeric Columns: {', '.join(numeric_cols)}")

    if st.button("🚀 Apply Advanced Formula", type="primary"):
        if formula_expr and new_col_name:
            try:
                df[new_col_name] = df.eval(formula_expr)
                st.session_state["df"] = df
                st.success(f"✅ Feature `{new_col_name}` successfully created!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error in formula evaluation: {str(e)}")

# ==========================================
# Module 2: Quick Calculated Column (A op B)
# ==========================================
with st.expander("➕ Module 2: Quick Calculated Column (A op B)"):
    if len(numeric_cols) >= 2:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            col_a = st.selectbox("Column A:", numeric_cols, key="quick_a")
        with c2:
            op = st.selectbox("Operation:", ["+", "-", "*", "/"], key="quick_op")
        with c3:
            col_b = st.selectbox("Column B:", [c for c in numeric_cols if c != col_a], key="quick_b")
        with c4:
            q_name = st.text_input("Result Name:", value=f"{col_a}_{op}_{col_b}")

        if st.button("Create Quick Feature"):
            if op == "+": df[q_name] = df[col_a] + df[col_b]
            elif op == "-": df[q_name] = df[col_a] - df[col_b]
            elif op == "*": df[q_name] = df[col_a] * df[col_b]
            elif op == "/": df[q_name] = df[col_a] / df[col_b].replace(0, np.nan)
            
            st.session_state["df"] = df
            st.success(f"✅ Created `{q_name}`!")
            st.rerun()
    else:
        st.info("Requires at least 2 numeric columns.")

# ==========================================
# Module 3: Feature Binning
# ==========================================
with st.expander("📦 Module 3: Feature Binning / Quantilization (Continuous to Categorical)"):
    if numeric_cols:
        b_col1, b_col2, b_col3 = st.columns(3)
        with b_col1:
            bin_target = st.selectbox("Target Column:", numeric_cols, key="bin_col")
        with b_col2:
            num_bins = st.slider("Number of Bins:", 2, 10, 4)
        with b_col3:
            bin_col_name = st.text_input("Grouped Column Name:", value=f"{bin_target}_Group")

        if st.button("Apply Binning"):
            df[bin_col_name] = pd.qcut(df[bin_target], q=num_bins, duplicates='drop').astype(str)
            st.session_state["df"] = df
            st.success(f"✅ Created Binned Feature `{bin_col_name}`!")
            st.rerun()

# ==========================================
# Module 4: Mathematical Transformations
# ==========================================
with st.expander("📐 Module 4: Mathematical Transformations (Skew Reduction)"):
    if numeric_cols:
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            trans_target = st.selectbox("Select Numeric Column:", numeric_cols, key="trans_col")
        with t_col2:
            trans_type = st.selectbox("Transformation:", ["Log (np.log1p)", "Square Root (np.sqrt)", "Absolute Value"])

        if st.button("Apply Transformation"):
            new_trans_name = f"{trans_target}_{trans_type.split()[0].lower()}"
            if "Log" in trans_type:
                df[new_trans_name] = np.log1p(np.maximum(0, df[trans_target]))
            elif "Square Root" in trans_type:
                df[new_trans_name] = np.sqrt(np.maximum(0, df[trans_target]))
            elif "Absolute" in trans_type:
                df[new_trans_name] = np.abs(df[trans_target])

            st.session_state["df"] = df
            st.success(f"✅ Created `{new_trans_name}`!")
            st.rerun()

# ==========================================
# Module 5: Categorical Encoding & Feature Scaling
# ==========================================
with st.expander("🔠 Module 5: Categorical Encoding & Feature Scaling", expanded=False):
    col_enc, col_scale = st.columns(2)

    # --- الجزء الأيسر: Categorical Encoding ---
    with col_enc:
        st.markdown("#### **Categorical Encoding**")
        if categorical_cols:
            enc_col = st.selectbox("Select Categorical Column", categorical_cols, key="enc_col_m5")
            enc_method = st.radio(
                "Encoding Method", 
                ["One-Hot Encoding (Dummy Variables)", "Ordinal / Label Encoding"],
                key="enc_method_m5"
            )
            
            if st.button("🏷️ Apply Encoding", type="primary", key="btn_apply_enc"):
                if "One-Hot" in enc_method:
                    df = pd.get_dummies(df, columns=[enc_col], prefix=enc_col, drop_first=True)
                else:
                    df[f"{enc_col}_encoded"] = df[enc_col].astype('category').cat.codes
                
                st.session_state["df"] = df
                st.success(f"✅ Encoding applied to `{enc_col}`!")
                st.rerun()
        else:
            st.info("No categorical columns available.")

    # --- الجزء الأيمن: Feature Scaling ---
    with col_scale:
        st.markdown("#### **Feature Scaling**")
        if numeric_cols:
            scale_cols = st.multiselect("Select Numeric Columns to Scale", numeric_cols, key="scale_cols_m5")
            scale_method = st.radio(
                "Scaling Strategy", 
                ["MinMax Scaling (0 to 1)", "Standardization (Z-Score)"],
                key="scale_method_m5"
            )

            if st.button("⚖️ Apply Scaling", type="primary", key="btn_apply_scale"):
                if scale_cols:
                    for col in scale_cols:
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
                    st.success("✅ Scaling applied successfully!")
                    st.rerun()
                else:
                    st.warning("Please select at least one numeric column.")
        else:
            st.info("No numeric columns available.")

st.divider()

# ==========================================
# Current Dataset Preview
# ==========================================
st.subheader("👁️ Current Dataset Preview (Post Feature Engineering)")
st.write(f"Total Rows: **{df.shape[0]:,}** | Total Columns: **{df.shape[1]}**")
st.dataframe(df.head(10), use_container_width=True)

st.divider()

# ==========================================
# Proceed Button (Proceed to EDA)
# ==========================================
col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
with col_b2:
    if st.button("Proceed to Exploratory Data Analysis (EDA) ➔", type="primary", use_container_width=True):
        st.switch_page("pages/6_Data_Analysis.py")
