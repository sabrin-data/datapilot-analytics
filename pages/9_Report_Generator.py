import io
import base64
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
from utils.translations import init_language, t

# 🔒 Paywall / Subscription Check (Freemium Gate)
from utils.paywall import check_subscription

# ==========================================
# 0. Page Configuration & Language Init
# ==========================================
st.set_page_config(
    page_title="Executive Report Generator",
    page_icon="📄",
    layout="wide"
)

# تفعيل فحص اشتراك المستخدم لهذه الصفحة
check_subscription("Executive Report Generator")

# يقرأ اللغة المختارة ويظهر القائمة الجانبية
init_language()

# قراءة الـ CSS الموحد
try:
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("📄 Executive Report Generator & Export Studio")
st.write(t("sub_title") if t("sub_title") != "sub_title" else "Synthesize dataset metrics, cleaning logs, statistical insights, and visual dashboards into a comprehensive report.")

# ==========================================
# 1. Check Dataset Availability
# ==========================================
if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning(t("no_dataset") if t("no_dataset") != "no_dataset" else "📂 Please upload a dataset first from the Upload page.")
    st.stop()

df = st.session_state["df"].copy()
file_name = st.session_state.get("file_name", "Dataset")
cleaning_log = st.session_state.get("cleaning_log", [])

# ==========================================
# 📊 Section 1: Executive Overview Summary
# ==========================================
st.subheader("📌 Executive Dataset Overview")

col1, col2, col3, col4 = st.columns(4)
col1.metric(t("total_rows") if t("total_rows") != "total_rows" else "Total Rows", f"{len(df):,}")
col2.metric(t("total_columns") if t("total_columns") != "total_columns" else "Total Columns", f"{df.shape[1]}")
col3.metric(t("missing_values") if t("missing_values") != "missing_values" else "Missing Values", f"{df.isnull().sum().sum():,}")
col4.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

st.divider()

# ==========================================
# ⚙️ Section 2: Report Customization
# ==========================================
st.subheader("⚙️ Configure Executive Report Sections")

col_cfg1, col_cfg2 = st.columns(2)

with col_cfg1:
    report_title = st.text_input("Report Title", value=f"Data Insight Analysis Report - {file_name}")
    author_name = st.text_input("Prepared By", value="DataPilot AI Analyst")
    include_summary = st.checkbox("Include Summary Statistics Table", value=True)
    include_charts = st.checkbox("Include Dashboard Visual Charts", value=True)

with col_cfg2:
    include_logs = st.checkbox("Include Data Sanitation Audit Logs", value=True)
    include_missing = st.checkbox("Include Missing Value Breakdown", value=True)
    include_sample = st.checkbox("Include Data Sample Preview (First 10 Rows)", value=True)

st.divider()

# ==========================================
# 📄 Section 3: HTML Report Generator Function
# ==========================================
def generate_html_report(dataframe, title, author, inc_summary, inc_charts, inc_logs, inc_missing, inc_sample, logs_list, lang):
    num_cols = dataframe.select_dtypes(include=np.number).columns.tolist()
    
    # 🔍 فلترة الأعمدة النصية
    raw_cat_cols = dataframe.select_dtypes(include=["object", "category"]).columns.tolist()
    cat_cols = [
        col for col in raw_cat_cols 
        if dataframe[col].nunique() < 30 and 'id' not in col.lower()
    ]
    
    # تحديد اتجاه الصفحة واللغة
    text_dir = "rtl" if lang == "ar" else "ltr"
    align_dir = "right" if lang == "ar" else "left"

    # 1. Summary stats HTML
    summary_html = ""
    if inc_summary and num_cols:
        desc_df = dataframe[num_cols].describe().T.reset_index()
        desc_df.rename(columns={"index": "Column Name"}, inplace=True)
        summary_html = f"<h3>Numerical Attributes Summary</h3>" + desc_df.to_html(index=False, classes="styled-table")

    # 2. Audit Logs HTML
    logs_html = ""
    if inc_logs and logs_list:
        logs_items = "".join([f"<li>{log}</li>" for log in logs_list])
        logs_html = f"<h3>Data Sanitation Audit Log</h3><ul>{logs_items}</ul>"
    elif inc_logs:
        logs_html = "<h3>Data Sanitation Audit Log</h3><p>No automated cleaning operations logged in this session.</p>"

    # 3. Missing Values HTML
    missing_html = ""
    if inc_missing:
        missing_df = dataframe.isnull().sum().reset_index()
        missing_df.columns = ["Column Name", "Missing Count"]
        missing_df["Missing Percentage (%)"] = (missing_df["Missing Count"] / len(dataframe) * 100).round(2)
        missing_df = missing_df[missing_df["Missing Count"] > 0]
        
        if not missing_df.empty:
            missing_html = "<h3>Missing Values Breakdown</h3>" + missing_df.to_html(index=False, classes="styled-table")
        else:
            missing_html = "<h3>Missing Values Breakdown</h3><p>✅ Complete Dataset: No missing values detected!</p>"

    # 4. Dashboard Charts HTML
    charts_html = ""
    if inc_charts:
        charts_html += "<h3>Executive Dashboard Visualizations</h3>"
        
        # لوحة ألوان احترافية متنوعة
        color_palette = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4']

        # Chart 1: Bar Chart
        if len(cat_cols) > 0 and len(num_cols) > 0:
            avg_df = dataframe.groupby(cat_cols[0], as_index=False)[num_cols[0]].mean().head(10)
            fig1 = px.bar(
                avg_df, 
                x=cat_cols[0], 
                y=num_cols[0], 
                title=f"Top {cat_cols[0]} by Avg {num_cols[0]}",
                template="plotly_white",
                color_discrete_sequence=['#4F46E5']
            )
            fig1.update_traces(marker_color='#4F46E5')
            fig1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            charts_html += fig1.to_html(full_html=False, include_plotlyjs='cdn')
            
        # Chart 2: Pie Chart
        if len(cat_cols) > 0:
            top_cat_counts = dataframe[cat_cols[0]].value_counts().head(10).reset_index()
            top_cat_counts.columns = [cat_cols[0], 'Count']
            fig2 = px.pie(
                top_cat_counts, 
                names=cat_cols[0], 
                values='Count', 
                title=f"Distribution of Top {cat_cols[0]}",
                template="plotly_white",
                color_discrete_sequence=color_palette
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            charts_html += fig2.to_html(full_html=False, include_plotlyjs='cdn')

    # 5. Data Sample HTML
    sample_html = ""
    if inc_sample:
        sample_html = "<h3>Dataset Preview (Top 10 Rows)</h3>" + dataframe.head(10).to_html(index=False, classes="styled-table")

    # Complete HTML Document
    html_content = f"""
    <!DOCTYPE html>
    <html dir="{text_dir}">
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 40px;
                background-color: #f9f9f9;
                color: #333;
                direction: {text_dir};
                text-align: {align_dir};
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #0066cc;
                padding-bottom: 10px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #0066cc;
                margin-bottom: 5px;
            }}
            .header p {{
                color: #666;
                font-size: 14px;
            }}
            .kpi-box {{
                display: flex;
                justify-content: space-around;
                background-color: #ffffff;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }}
            .kpi-card {{
                text-align: center;
            }}
            .kpi-card h4 {{
                margin: 0;
                color: #888;
            }}
            .kpi-card p {{
                margin: 5px 0 0 0;
                font-size: 20px;
                font-weight: bold;
                color: #0066cc;
            }}
            .styled-table {{
                border-collapse: collapse;
                margin: 25px 0;
                font-size: 14px;
                min-width: 100%;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
                background-color: #ffffff;
            }}
            .styled-table th {{
                background-color: #0066cc;
                color: #ffffff;
                text-align: {align_dir};
                padding: 12px 15px;
            }}
            .styled-table td {{
                padding: 12px 15px;
                border-bottom: 1px solid #dddddd;
            }}
            .styled-table tr:nth-of-type(even) {{
                background-color: #f3f3f3;
            }}
            .footer {{
                margin-top: 50px;
                text-align: center;
                font-size: 12px;
                color: #aaa;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{title}</h1>
            <p>Generated by <strong>{author}</strong> | Source File: <em>{file_name}</em></p>
        </div>

        <div class="kpi-box">
            <div class="kpi-card"><h4>Total Rows</h4><p>{len(dataframe):,}</p></div>
            <div class="kpi-card"><h4>Total Attributes</h4><p>{dataframe.shape[1]}</p></div>
            <div class="kpi-card"><h4>Numeric Attributes</h4><p>{len(num_cols)}</p></div>
            <div class="kpi-card"><h4>Categorical Attributes</h4><p>{len(cat_cols)}</p></div>
        </div>

        {logs_html}
        {missing_html}
        {charts_html}
        {summary_html}
        {sample_html}

        <div class="footer">
            <p>Generated automatically via DataPilot AI Studio.</p>
        </div>
    </body>
    </html>
    """
    return html_content

# توليد التقرير بالمتغيرات المحددة
current_lang = st.session_state.get("lang", "en")
html_report = generate_html_report(
    df, report_title, author_name, 
    include_summary, include_charts, include_logs, 
    include_missing, include_sample, cleaning_log, current_lang
)

# ==========================================
# 📥 Section 4: Export Options & Downloads
# ==========================================
st.subheader("📥 Export Reports & Cleaned Datasets")

col_exp1, col_exp2, col_exp3 = st.columns(3)

with col_exp1:
    st.download_button(
        label="📄 Download Executive HTML Report",
        data=html_report,
        file_name=f"Executive_Report_{file_name}.html",
        mime="text/html",
        type="primary",
        use_container_width=True
    )

with col_exp2:
    csv_data = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="⬇️ Download Cleaned Data (CSV)",
        data=csv_data,
        file_name=f"Final_Cleaned_{file_name}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_exp3:
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Cleaned Data')
    excel_data = excel_buffer.getvalue()

    st.download_button(
        label="📊 Download Cleaned Data (Excel)",
        data=excel_data,
        file_name=f"Final_Cleaned_{file_name}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.divider()

# Interactive Preview of HTML Report
with st.expander("👁️ Live Preview Generated HTML Executive Report", expanded=False):
    components.html(html_report, height=600, scrolling=True)

st.success("🎉 Report Studio Ready!")