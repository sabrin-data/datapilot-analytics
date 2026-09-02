import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.translations import init_language, t

# ==========================================
# 0. Page Configuration (Must be First)
# ==========================================
st.set_page_config(
    page_title="Executive Dashboard - DataPilot AI", 
    page_icon="📊",
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

st.title("📊 Executive Dashboard & AI Assistant")

# ==========================================
# 1. Check Dataset Availability
# ==========================================
if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("⚠️ Please upload a dataset first in the Upload page!")
    st.stop()

df = st.session_state["df"]

# تصنيف الأعمدة
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

# ==========================================
# 2. SIDEBAR: EXCEL-LIKE SLICERS & FILTERS
# ==========================================
st.sidebar.markdown("### 🎛️ Executive Slicers & Filters")
filtered_df = df.copy()

# فلترة ذكية: استثناء أعمدة الـ ID من السلايسر التلقائي لتجنب تفريغ البيانات
slicer_categorical_cols = [
    col for col in categorical_cols 
    if not any(id_kw in col.lower() for id_kw in ['id', 'code', 'index', 'txn'])
]

# إذا لم نجد أعمدة نصية عادية نستخدم الأحدث، بحد أقصى 3 أعمدة
target_slicers = slicer_categorical_cols[:3] if slicer_categorical_cols else categorical_cols[:3]

if target_slicers:
    for col in target_slicers:
        unique_vals = df[col].dropna().unique().tolist()
        selected_vals = st.sidebar.multiselect(
            f"Filter by {col}", 
            options=unique_vals, 
            default=unique_vals,
            key=f"filter_{col}"
        )
        if selected_vals:
            filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]
else:
    st.sidebar.info("No categorical columns available for slicing.")

# ==========================================
# 3. TOP KPIs SECTION (منطق ذكي ومعدّل لمنع التكرار)
# ==========================================
st.markdown("### 📈 Key Performance Indicators (KPIs)")

if not filtered_df.empty:
    kpi_cols = st.columns(4)
    
    # 1. إجمالي عدد العمليات/الطلبيات
    with kpi_cols[0]:
        st.metric(
            label="Total Transactions",
            value=f"{len(filtered_df):,}",
            delta="Total Records"
        )
        
    # 2. إجمالي المبيعات/الانفاق (أول عمود مالي)
    spend_cols = [c for c in numeric_cols if any(k in c.lower() for k in ['spent', 'total', 'revenue', 'price', 'amount'])]
    target_spend_col = spend_cols[0] if spend_cols else (numeric_cols[0] if numeric_cols else None)
    
    with kpi_cols[1]:
        if target_spend_col:
            total_val = filtered_df[target_spend_col].sum()
            avg_val = filtered_df[target_spend_col].mean()
            st.metric(
                label=f"Total {target_spend_col.replace('_', ' ').title()}", 
                value=f"{total_val:,.1f}",
                delta=f"Avg: {avg_val:,.1f}"
            )
        else:
            st.metric(label="Total Volume", value="N/A")

    # 3. إجمالي الكميات أو عمود رقمي مختلف (منع التكرار مع الكرت الثاني)
    qty_cols = [c for c in numeric_cols if any(k in c.lower() for k in ['qty', 'quantity', 'count', 'unit']) and c != target_spend_col]
    other_num_cols = [c for c in numeric_cols if c != target_spend_col]
    target_qty_col = qty_cols[0] if qty_cols else (other_num_cols[0] if other_num_cols else None)
    
    with kpi_cols[2]:
        if target_qty_col:
            total_qty = filtered_df[target_qty_col].sum()
            avg_qty = filtered_df[target_qty_col].mean()
            st.metric(
                label=f"Total {target_qty_col.replace('_', ' ').title()}", 
                value=f"{total_qty:,.1f}",
                delta=f"Avg: {avg_qty:,.1f}"
            )
        else:
            st.metric(label="Data Status", value="100% Valid")

    # 4. متوسط قيمة العملية (Average Value)
    with kpi_cols[3]:
        if target_spend_col:
            avg_order_val = filtered_df[target_spend_col].mean()
            st.metric(
                label="Avg Transaction Value",
                value=f"{avg_order_val:,.1f}",
                delta="Mean Revenue"
            )
        else:
            st.metric(label="Data Health", value="100%")

else:
    st.info("No data available to display KPIs based on current filters.")

st.divider()

# ==========================================
# 4. EXECUTIVE VISUAL BREAKDOWN (معدل للتركيز على Category)
# ==========================================
st.markdown("### 📉 Executive Visual Breakdown")

# منطق ذكي لاختيار العمود النصي الأنسب (تفضيل Category على Item لضمان وضوح الرسم)
preferred_cat_cols = [c for c in slicer_categorical_cols if any(k in c.lower() for k in ['category', 'type', 'group', 'payment', 'location'])]
main_chart_cat = preferred_cat_cols[0] if preferred_cat_cols else (slicer_categorical_cols[0] if slicer_categorical_cols else (categorical_cols[0] if categorical_cols else None))

chart_num_cols = [c for c in numeric_cols if not any(k in c.lower() for k in ['year', 'month', 'day', 'id'])]
if not chart_num_cols:
    chart_num_cols = numeric_cols

if not filtered_df.empty:
    col1, col2 = st.columns(2)

    with col1:
        if main_chart_cat and chart_num_cols:
            avg_df = filtered_df.groupby(main_chart_cat, as_index=False)[chart_num_cols[0]].mean()
            
            fig1 = px.bar(
                avg_df, 
                x=main_chart_cat, 
                y=chart_num_cols[0], 
                title=f"Average {chart_num_cols[0].replace('_', ' ')} by {main_chart_cat.title()}",
                color=main_chart_cat
            )
            fig1.update_layout(
                xaxis_tickangle=-30,
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=80)
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Bar Chart requires at least 1 Categorical & 1 Numeric column.")

    with col2:
        if main_chart_cat:
            counts = filtered_df[main_chart_cat].value_counts().reset_index()
            counts.columns = [main_chart_cat, 'count']
            
            if len(counts) > 10:
                top_10 = counts.iloc[:10]
                others_count = counts.iloc[10:]['count'].sum()
                others_df = pd.DataFrame([{main_chart_cat: 'Others', 'count': others_count}])
                counts_display = pd.concat([top_10, others_df], ignore_index=True)
            else:
                counts_display = counts

            fig2 = px.pie(
                counts_display, 
                names=main_chart_cat, 
                values='count',
                title=f"Distribution of {main_chart_cat.title()}",
                hole=0.4
            )
            fig2.update_traces(textposition='inside', textinfo='percent+label')
            fig2.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Pie Chart requires a Categorical column.")

    # Scatter Plot
    if len(chart_num_cols) >= 2:
        fig3 = px.scatter(
            filtered_df, 
            x=chart_num_cols[0], 
            y=chart_num_cols[1], 
            color=main_chart_cat if main_chart_cat else None,
            title=f"{chart_num_cols[0].replace('_', ' ')} vs {chart_num_cols[1].replace('_', ' ')} Analysis"
        )
        fig3.update_layout(margin=dict(l=20, r=20, t=40, b=40))
        st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("No data available for charts based on current filters.")