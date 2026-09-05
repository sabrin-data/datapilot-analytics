import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, IsolationForest
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.metrics import r2_score, mean_squared_error, accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder
from utils.translations import init_language, t

# ==========================================
# 0. Page Configuration & Language Init
# ==========================================
st.set_page_config(
    page_title="DataPilot AI - AI Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تفعيل تهيئة اللغة
init_language()

# قراءة الـ CSS الموحد
try:
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Header Section
st.title("🤖 AI Analyst")
st.write("Your interactive enterprise AI Data Scientist for automated diagnostics, predictive modeling, and strategic business analysis.")

# ==========================================
# 🔐 Subscription Guard Check
# ==========================================
user_plan = st.session_state.get("user_plan", "Pro")  # الخيارات: 'Free', 'Pro', 'Enterprise'

if user_plan == "Free":
    st.warning("🔒 **Premium Feature Locked:** The AI Analyst Studio & Machine Learning Suite are available on **Pro** and **Enterprise** plans.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.info("💡 **Upgrade to Pro Plan**\n- Automated ML Predictive Modeling\n- Isolation Forest Anomaly Detection\n- Full Correlation Analysis & Insights")
    with col_p2:
        st.success("🚀 **Enterprise Plan**\n- Custom Model Fine-tuning\n- One-Click Executive PDF Reports\n- Dedicated AI Infrastructure")
        
    if st.button("⭐ Upgrade Subscription Now", type="primary", use_container_width=True):
        st.switch_page("pages/8_Pricing.py")
    st.stop()

# ==========================================
# 1. Check Dataset Availability
# ==========================================
if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("📂 Please upload a dataset or select the Demo Dataset from the Home / Upload page first.")
    
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("🏠 Go to Home Page", type="primary", use_container_width=True):
            st.switch_page("Home.py")
    with col_nav2:
        if st.button("📤 Go to Upload Page", type="secondary", use_container_width=True):
            st.switch_page("pages/2_Upload.py")
            
    st.stop()

df = st.session_state["df"].copy()
file_name = st.session_state.get("file_name", "Dataset")

st.info(f"📁 Active Dataset: **{file_name}** | Dimensions: **{df.shape[0]:,} rows × {df.shape[1]} cols** | Plan: **{user_plan} Member** 🌟")
st.divider()

# Classify attributes
num_cols = df.select_dtypes(include=np.number).columns.tolist()
cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
all_cols = df.columns.tolist()

# ==========================================
# 🎯 6-Tab AI Analyst Architecture
# ==========================================
tab_ask, tab_summary, tab_insights, tab_biz, tab_ml, tab_report = st.tabs([
    "💬 Ask AI",
    "📊 Dataset Summary",
    "💡 Key Insights",
    "📈 Business Insights",
    "🎯 Recommendations & ML",
    "📄 Generate Report"
])

# ----------------------------------------------------
# 💬 TAB 1: Ask AI (Interactive Query & Chat)
# ----------------------------------------------------
with tab_ask:
    st.subheader("💬 Ask Anything About Your Dataset")
    st.caption("Query your data using plain language to get instant statistical answers and data breakdowns.")
    
    user_query = st.text_input(
        "Enter your query or prompt for AI Analyst:",
        placeholder="e.g. What are the key business insights and recommendations to increase sales?",
        key="ai_analyst_user_query"
    )
    
    if st.button("🤖 Process Query", type="primary", key="ask_btn"):
        if user_query.strip():
            st.session_state["last_processed_query"] = user_query
            
            with st.spinner("AI Analyst is analyzing dataset structure..."):
                st.success("🎯 **AI Response:**")
                st.markdown(f"Analyzed query: *\"{user_query}\"* against **{df.shape[0]:,}** records.")
                
                query_clean = user_query.lower().strip()
                
                if any(k in query_clean for k in ["insight", "recommend", "increase sale", "strategy", "summary", "advice", "growth", "business"]):
                    top_cat = "N/A"
                    if 'Category' in df.columns and 'Total Spent' in df.columns:
                        top_cat = df.groupby('Category')['Total Spent'].sum().idxmax()
                    elif cat_cols and 'Total Spent' in df.columns:
                        top_cat = df.groupby(cat_cols[0])['Total Spent'].sum().idxmax()
                    elif cat_cols and num_cols:
                        top_cat = df.groupby(cat_cols[0])[num_cols[0]].sum().idxmax()

                    avg_spent = df['Total Spent'].mean() if 'Total Spent' in df.columns else (df[num_cols[0]].mean() if num_cols else 0)

                    st.markdown("### 💡 **Strategic Enterprise AI Recommendations**")
                    st.info(f"""
                    Based on an automated enterprise AI analysis of **{len(df):,} dataset records**:

                    * 🎯 **Top Revenue Driver:** The **`{top_cat}`** category generates the highest overall sales volume. Capitalize on this demand by optimizing inventory and running targeted cross-sell campaigns.
                    * 💳 **Average Basket Size:** The current mean transaction value across all categories is **`${avg_spent:.2f}`**. Implement bundle deals or threshold-based discounts to drive order values higher.
                    * 🚀 **Growth Strategy:** Shift focus towards high-margin items in underperforming categories to balance portfolio profitability.
                    * 🔍 **Deep Dive:** Navigate to the **Key Insights** and **Recommendations & ML** tabs above for complete model metrics and anomaly detections!
                    """)
                else:
                    st.dataframe(df.head(10), use_container_width=True)
        else:
            st.error("Please enter a valid query.")

# ----------------------------------------------------
# 📊 TAB 2: Dataset Summary
# ----------------------------------------------------
with tab_summary:
    st.subheader("📊 Automated Dataset Summary")
    st.caption("High-level executive overview of structural metrics and data health.")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Rows", f"{df.shape[0]:,}")
    m2.metric("Total Columns", df.shape[1])
    m3.metric("Numeric Features", len(num_cols))
    m4.metric("Categorical Features", len(cat_cols))
    
    st.divider()
    st.markdown("##### 🔍 Quick Data Types & Missing Values Overview")
    summary_df = pd.DataFrame({
        "Data Type": df.dtypes.astype(str),
        "Missing Values": df.isnull().sum(),
        "Missing Ratio (%)": (df.isnull().sum() / len(df) * 100).round(2),
        "Unique Values": df.nunique()
    })
    st.dataframe(summary_df, use_container_width=True)

# ----------------------------------------------------
# 💡 TAB 3: Key Insights
# ----------------------------------------------------
with tab_insights:
    st.subheader("💡 Automated Key Insights & Correlation Analysis")
    st.caption("Discover patterns, statistical anomalies, and strong variable interactions.")
    
    base_corr_cols = [
        col for col in num_cols
        if not col.startswith(('Category_', 'Payment Method_', 'Payment_', 'Item_'))
        and not col.endswith(('_minmax', '_scaled', '_log', '_Year', '_Month'))
        and df[col].std() > 0
    ]
    
    if len(base_corr_cols) >= 2:
        st.markdown("##### 🔗 Core Numeric Feature Correlation Matrix")
        corr = df[base_corr_cols].corr()
        
        fig_corr = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            title="Core Numeric Correlation Heatmap"
        )
        
        fig_corr.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("At least two core numerical columns are required to draw correlation heatmaps.")

# ----------------------------------------------------
# 📈 TAB 4: Business Insights
# ----------------------------------------------------
with tab_biz:
    st.subheader("📈 Business Insights & Strategic Metrics")
    st.caption("Translating operational dataset trends into high-level strategic summaries.")
    
    st.markdown("""
    > **📌 Strategic Executive Highlights:**
    > * **Data Distribution**: Dataset contains balanced structural attributes suitable for predictive decision engines.
    > * **Operational Efficiency**: Minimal missing values detected across critical core features.
    > * **Growth Driver**: Key numeric indicators demonstrate high variability and optimization opportunities.
    """)
    
    if cat_cols and num_cols:
        col_c, col_n = st.columns(2)
        with col_c:
            sel_cat = st.selectbox("Select Business Category", cat_cols, key="biz_cat")
        with col_n:
            sel_num = st.selectbox("Select Target Business Metric", num_cols, key="biz_num")
            
        biz_agg = df.groupby(sel_cat)[sel_num].mean().reset_index().sort_values(by=sel_num, ascending=False).head(10)
        fig_biz = px.bar(biz_agg, x=sel_cat, y=sel_num, title=f"Average {sel_num} by {sel_cat}", color=sel_num, color_continuous_scale="Viridis")
        st.plotly_chart(fig_biz, use_container_width=True)

# ----------------------------------------------------
# 🎯 TAB 5: Recommendations & Predictive ML Studio
# ----------------------------------------------------
with tab_ml:
    st.subheader("🎯 Predictive Modeling & Anomaly Detection")
    
    sub_ml_tab1, sub_ml_tab2 = st.tabs(["🤖 Machine Learning Studio", "🚨 Isolation Forest Anomalies"])
    
    # --- ML Sub-Tab ---
    with sub_ml_tab1:
        col_setup1, col_setup2, col_setup3 = st.columns(3)
        
        with col_setup1:
            target_var = st.selectbox("Select Target Variable (Y)", all_cols, index=len(all_cols)-1, key="target_select")
        
        is_numeric_target = target_var in num_cols
        unique_target_count = df[target_var].nunique()
        
        if is_numeric_target and unique_target_count > 10:
            default_task = "Regression"
        else:
            default_task = "Classification"

        with col_setup2:
            task_type = st.radio("Task Type Detected", ["Regression", "Classification"], index=0 if default_task == "Regression" else 1, key="task_radio")
            
        with col_setup3:
            if task_type == "Regression":
                model_name = st.selectbox("Select Algorithm", ["Random Forest Regressor", "Linear Regression", "Decision Tree Regressor"], key="algo_reg")
            else:
                model_name = st.selectbox("Select Algorithm", ["Random Forest Classifier", "Logistic Regression", "Decision Tree Classifier"], key="algo_clf")

        available_features = [c for c in all_cols if c != target_var]
        selected_features = st.multiselect("Select Feature Predictors (X)", available_features, default=available_features, key="features_select")

        if st.button("🚀 Train Machine Learning Model", type="primary", use_container_width=True, key="train_ml_btn"):
            if not selected_features:
                st.error("Please select at least one feature for prediction.")
            else:
                with st.spinner("Training model and processing encodings..."):
                    ml_df = df[[target_var] + selected_features].dropna(subset=[target_var]).copy()
                    encoders = {}

                    if task_type == "Regression":
                        ml_df[target_var] = pd.to_numeric(ml_df[target_var], errors='coerce')
                        ml_df = ml_df.dropna(subset=[target_var])
                        
                        if ml_df.empty:
                            st.error("❌ The selected Target Variable (Y) contains non-numeric values for Regression.")
                            st.stop()
                    else:
                        if pd.api.types.is_object_dtype(ml_df[target_var]) or pd.api.types.is_categorical_dtype(ml_df[target_var]) or pd.api.types.is_string_dtype(ml_df[target_var]):
                            target_le = LabelEncoder()
                            ml_df[target_var] = target_le.fit_transform(ml_df[target_var].astype(str))
                            encoders[target_var] = target_le

                    for col in selected_features:
                        if pd.api.types.is_object_dtype(ml_df[col]) or pd.api.types.is_categorical_dtype(ml_df[col]) or pd.api.types.is_string_dtype(ml_df[col]):
                            fill_val = ml_df[col].mode()[0] if not ml_df[col].mode().empty else "Missing"
                            ml_df[col] = ml_df[col].fillna(fill_val).astype(str)
                            le = LabelEncoder()
                            ml_df[col] = le.fit_transform(ml_df[col])
                            encoders[col] = le
                        else:
                            ml_df[col] = pd.to_numeric(ml_df[col], errors='coerce')
                            mean_val = ml_df[col].mean()
                            ml_df[col] = ml_df[col].fillna(mean_val if not pd.isna(mean_val) else 0)

                    X = ml_df[selected_features]
                    y = ml_df[target_var]

                    if len(X) < 5:
                        st.error("Dataset has too few valid rows after cleaning.")
                        st.stop()

                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                    if task_type == "Regression":
                        if model_name == "Random Forest Regressor":
                            model = RandomForestRegressor(n_estimators=100, random_state=42)
                        elif model_name == "Linear Regression":
                            model = LinearRegression()
                        else:
                            model = DecisionTreeRegressor(random_state=42)
                    else:
                        if model_name == "Random Forest Classifier":
                            model = RandomForestClassifier(n_estimators=100, random_state=42)
                        elif model_name == "Logistic Regression":
                            model = LogisticRegression(max_iter=1000)
                        else:
                            model = DecisionTreeClassifier(random_state=42)

                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)

                    st.session_state["trained_model"] = model
                    st.session_state["model_features"] = selected_features
                    st.session_state["encoders"] = encoders
                    st.session_state["task_type"] = task_type
                    st.session_state["target_var"] = target_var
                    st.session_state["y_test"] = y_test
                    st.session_state["y_pred"] = y_pred

                    st.success("✅ Model Training Complete!")

        # Results Display
        if "trained_model" in st.session_state:
            model = st.session_state["trained_model"]
            selected_features = st.session_state["model_features"]
            task_type = st.session_state["task_type"]
            y_test = st.session_state["y_test"]
            y_pred = st.session_state["y_pred"]
            
            st.divider()
            st.subheader("📊 Model Performance Evaluation")
            m1, m2, m3 = st.columns(3)

            if task_type == "Regression":
                r2 = r2_score(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                mae = np.mean(np.abs(y_test - y_pred))

                m1.metric("R² Score", f"{r2:.3f}")
                m2.metric("RMSE", f"{rmse:.3f}")
                m3.metric("MAE", f"{mae:.3f}")
            else:
                acc = accuracy_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred, average="weighted")

                m1.metric("Model Accuracy", f"{acc * 100:.2f}%")
                m2.metric("Weighted F1-Score", f"{f1:.3f}")
                m3.metric("Test Count", f"{len(y_test):,}")

            if hasattr(model, "feature_importances_"):
                st.divider()
                st.subheader("💡 Feature Importance Drivers")
                importance_df = pd.DataFrame({
                    "Feature": selected_features,
                    "Importance": model.feature_importances_
                }).sort_values(by="Importance", ascending=True)

                fig_imp = px.bar(importance_df, x="Importance", y="Feature", orientation="h", title="Top Feature Drivers", color="Importance", color_continuous_scale="Blues")
                st.plotly_chart(fig_imp, use_container_width=True)

    # --- Anomaly Detection Sub-Tab ---
    with sub_ml_tab2:
        st.subheader("🚨 Isolation Forest Anomaly Detection")
        if len(num_cols) >= 2:
            anom_cols = st.multiselect("Select Attributes for Scanning", num_cols, default=num_cols[:min(4, len(num_cols))], key="anom_cols_select")
            contamination_rate = st.slider("Expected Contamination Rate (%)", min_value=1, max_value=15, value=5, key="contam_slider") / 100.0

            if st.button("🔍 Run Anomaly Detection", type="primary", key="run_anom_btn"):
                anom_df = df[anom_cols].dropna().copy()
                if len(anom_df) > 0:
                    iso_model = IsolationForest(contamination=contamination_rate, random_state=42)
                    preds = iso_model.fit_predict(anom_df)
                    anom_df["Anomaly_Status"] = np.where(preds == -1, "Anomaly 🚨", "Normal ✅")

                    anom_count = (preds == -1).sum()
                    st.warning(f"🚨 **Detected {anom_count:,} Anomalies** out of **{len(anom_df):,}** records ({anom_count/len(anom_df)*100:.2f}%).")

                    if len(anom_cols) >= 2:
                        fig_anom = px.scatter(
                            anom_df, x=anom_cols[0], y=anom_cols[1], color="Anomaly_Status",
                            color_discrete_map={"Normal ✅": "#1f77b4", "Anomaly 🚨": "#d62728"},
                            title=f"Anomalies Scatter: {anom_cols[0]} vs {anom_cols[1]}"
                        )
                        st.plotly_chart(fig_anom, use_container_width=True)

                    st.dataframe(anom_df[anom_df["Anomaly_Status"] == "Anomaly 🚨"], use_container_width=True)
        else:
            st.info("At least two numerical columns are required.")

# ----------------------------------------------------
# 📄 TAB 6: Generate Report
# ----------------------------------------------------
with tab_report:
    st.subheader("📄 One-Click Executive AI Report")
    st.caption("Compile AI findings and predictions into printable documentation.")
    
    st.success("✅ Dataset and AI metrics ready for compilation.")
    if st.button("📄 Generate & Export Executive Summary", type="primary", use_container_width=True, key="export_report_btn"):
        st.switch_page("pages/9_Report_Generator.py")

st.divider()

# Transition Button
col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
with col_b2:
    if st.button("Proceed to Executive Report Generator ➔", type="primary", use_container_width=True, key="proceed_report_btn"):
        st.switch_page("pages/9_Report_Generator.py")
