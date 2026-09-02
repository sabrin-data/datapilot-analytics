import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.translations import init_language, t

# ==========================================
# 0. Page Configuration & Language Init
# ==========================================
st.set_page_config(
    page_title="Data Overview & Health Profile",
    page_icon="📋",
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

st.title("📋 Automated Data Overview & Health Audit")
st.write(t("sub_title") if t("sub_title") != "sub_title" else "Comprehensive dataset diagnostics, automated statistical profiling, and AI data health assessment.")

# ==========================================
# 1. Check Dataset Availability
# ==========================================
if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning(t("no_dataset") if t("no_dataset") != "no_dataset" else "📂 Please upload a dataset first from the Upload page.")
    st.stop()

df = st.session_state["df"]
file_name = st.session_state.get("file_name", "Dataset")

st.divider()

# ==========================================
# 📂 Section 1: Dataset Information
# ==========================================
with st.expander("📂 Section 1: Dataset Information & Dtypes Breakdown", expanded=True):
    rows, cols = df.shape
    file_size_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    dt_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    bool_cols = df.select_dtypes(include="bool").columns.tolist()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📄 File Name", file_name)
    col2.metric(t("total_rows") if t("total_rows") != "total_rows" else "📊 Total Rows", f"{rows:,}")
    col3.metric(t("total_columns") if t("total_columns") != "total_columns" else "📊 Total Columns", cols)
    col4.metric("💾 Memory Footprint", f"{file_size_mb:.2f} MB")

    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔢 Numeric Columns", len(num_cols))
    c2.metric("📝 Text/Categorical", len(cat_cols))
    c3.metric("📅 Date/Time Columns", len(dt_cols))
    c4.metric("✔ Boolean Columns", len(bool_cols))

# ==========================================
# ⭐ Section 2: Data Quality Score
# ==========================================
with st.expander("⭐ Section 2: Data Quality & Health Score", expanded=True):
    total_cells = rows * cols
    missing_total = int(df.isnull().sum().sum())
    duplicates = int(df.duplicated().sum())
    empty_cols_cnt = len(df.columns[df.isnull().all()])
    constant_cols_cnt = len([c for c in df.columns if df[c].nunique() == 1])

    # Percentage Calculations
    missing_pct = (missing_total / total_cells * 100) if total_cells > 0 else 0
    dup_pct = (duplicates / rows * 100) if rows > 0 else 0
    
    # Mathematical Quality Score Calculation
    quality_score = 100 - (missing_pct * 1.5) - (dup_pct * 2.0) - (empty_cols_cnt * 5) - (constant_cols_cnt * 3)
    quality_score = max(0, min(100, int(round(quality_score))))

    if quality_score >= 85:
        badge = f"🟢 Excellent ({quality_score}/100)"
    elif quality_score >= 60:
        badge = f"🟡 Moderate Health ({quality_score}/100)"
    else:
        badge = f"🔴 Poor Quality ({quality_score}/100)"

    st.markdown(f"### Overall Health Metric: **{badge}**")
    st.progress(quality_score / 100)

    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    q_col1.metric(t("missing_values") if t("missing_values") != "missing_values" else "Missing Values", f"{missing_total:,} ({missing_pct:.1f}%)")
    q_col2.metric("Duplicate Rows", f"{duplicates:,} ({dup_pct:.1f}%)")
    q_col3.metric("Empty Columns", empty_cols_cnt)
    q_col4.metric("Constant Columns", constant_cols_cnt)

# ==========================================
# 📊 Section 3: Interactive Charts
# ==========================================
with st.expander("📊 Section 3: Visual Diagnostics & Distribution Plots", expanded=False):
    chart_tab1, chart_tab2, chart_tab3, chart_tab4, chart_tab5 = st.tabs([
        "1️⃣ Data Types Pie", "2️⃣ Missing Bar", "3️⃣ Histogram", "4️⃣ Correlation Heatmap", "5️⃣ Outlier Boxplot"
    ])

    # 1. Data Types Pie Chart
    with chart_tab1:
        type_counts = {
            "Numeric": len(num_cols),
            "Categorical": len(cat_cols),
            "Datetime": len(dt_cols),
            "Boolean": len(bool_cols)
        }
        fig_pie = px.pie(
            names=list(type_counts.keys()), 
            values=list(type_counts.values()),
            title="Data Types Distribution Ratio",
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # 2. Missing Values Bar Chart
    with chart_tab2:
        missing_series = df.isnull().sum()
        missing_filtered = missing_series[missing_series > 0]
        if not missing_filtered.empty:
            fig_miss = px.bar(
                x=missing_filtered.index, 
                y=missing_filtered.values,
                labels={"x": "Column Name", "y": "Missing Count"},
                title="Missing Values Count per Column"
            )
            st.plotly_chart(fig_miss, use_container_width=True)
        else:
            st.success("🎉 Zero missing values detected across all attributes!")

    # 3. Histogram Distribution
    with chart_tab3:
        if num_cols:
            selected_num = st.selectbox("Select Column for Distribution Analysis", num_cols, key="hist_select")
            fig_hist = px.histogram(df, x=selected_num, title=f"Distribution Profile for '{selected_num}'", marginal="box")
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No numeric columns available for histogram plotting.")

    # 4. Correlation Heatmap
    with chart_tab4:
        if len(num_cols) >= 2:
            corr = df[num_cols].corr()
            fig_corr = px.imshow(corr, text_auto=True, title="Numeric Feature Correlation Heatmap", aspect="auto")
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("At least two numeric columns are required to display a correlation heatmap.")

    # 5. Outlier Boxplot
    with chart_tab5:
        if num_cols:
            box_col = st.selectbox("Select Column for Outlier Inspection", num_cols, key="box_select")
            fig_box = px.box(df, y=box_col, title=f"Outlier Dispersion Boxplot for '{box_col}'")
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("No numeric columns available for outlier inspection.")

# ==========================================
# 📈 Section 4: Dataset Preview & Sampling
# ==========================================
with st.expander("📈 Section 4: Dataset Preview & Multi-Angle Sampling", expanded=False):
    prev_tab1, prev_tab2, prev_tab3 = st.tabs(["Head (First 5)", "Tail (Last 5)", "Random Sample (5 Rows)"])
    
    with prev_tab1:
        st.dataframe(df.head(), use_container_width=True)
    with prev_tab2:
        st.dataframe(df.tail(), use_container_width=True)
    with prev_tab3:
        st.dataframe(df.sample(min(5, len(df))), use_container_width=True)

# ==========================================
# 📊 Section 5: Advanced Statistical Profiling
# ==========================================
with st.expander("📊 Section 5: Extended Descriptive Statistics", expanded=False):
    if num_cols:
        stats_df = pd.DataFrame(index=num_cols)
        stats_df["Mean"] = df[num_cols].mean()
        stats_df["Median"] = df[num_cols].median()
        stats_df["Min"] = df[num_cols].min()
        stats_df["Max"] = df[num_cols].max()
        stats_df["Range"] = stats_df["Max"] - stats_df["Min"]
        stats_df["Std Dev"] = df[num_cols].std()
        stats_df["Variance"] = df[num_cols].var()
        stats_df["Skewness"] = df[num_cols].skew()
        stats_df["Kurtosis"] = df[num_cols].kurt()

        st.dataframe(stats_df.round(3), use_container_width=True)
    else:
        st.info("No numerical variables found for descriptive statistics.")

# ==========================================
# 🤖 Section 6, 7, & 8: AI Summary, Warnings & Recommendations
# ==========================================
with st.expander("🤖 Section 6, 7 & 8: AI Summary, Health Warnings & Actionable Recommendations", expanded=True):
    ai_col1, ai_col2 = st.columns(2)

    with ai_col1:
        st.subheader("🤖 AI Dataset Summary")
        st.info(f"""
        • The dataset contains **{rows:,} rows** and **{cols} columns**.
        • Missing cells represent **{missing_pct:.2f}%** of the total volume.
        • Calculated Health Score is **{quality_score}/100**.
        • Pipeline Readiness: **{"Ready for cleaning and model ingestion" if quality_score > 70 else "Sanitation highly recommended before analysis"}**.
        """)

        st.subheader("⚠️ Automated Quality Warnings")
        warnings = []
        if missing_pct > 0: warnings.append(f"⚠ Found **{missing_total:,} missing values** across columns.")
        if duplicates > 0: warnings.append(f"⚠ Detected **{duplicates:,} duplicate rows**.")
        if constant_cols_cnt > 0: warnings.append(f"⚠ Found **{constant_cols_cnt} constant columns** containing single values.")
        if not warnings: warnings.append("✅ No critical data health warnings detected!")
        for w in warnings: st.write(w)

    with ai_col2:
        st.subheader("💡 Actionable AI Recommendations")
        recs = []
        if duplicates > 0: recs.append("✔ Deduplicate rows in the Data Cleaning page.")
        if missing_pct > 0: recs.append("✔ Apply missing value imputation (Mean/Median/Mode) or drop empty cells.")
        if constant_cols_cnt > 0: recs.append("✔ Drop non-informative constant columns.")
        recs.append("✔ Verify numeric columns stored as text formats.")
        for r in recs: st.write(r)

st.divider()

# ==========================================
# 🚀 Section 9: Next Pipeline Transition
# ==========================================
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("Continue to Data Cleaning ➔", type="primary", use_container_width=True):
        st.switch_page("pages/4_Data_Cleaning.py")