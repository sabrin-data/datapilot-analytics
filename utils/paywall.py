import streamlit as st

def check_subscription(page_title="Pro Feature"):
    """
    يفحص هذا التابع إذا كان المستخدم مشترِكاً أم لا.
    إذا لم يكن مشترِكاً، يوقف تنفيذ الصفحة ويوجه للمشرك.
    """
    if "is_subscribed" not in st.session_state:
        st.session_state["is_subscribed"] = False

    if not st.session_state["is_subscribed"]:
        st.title(f"🔒 {page_title}")
        st.warning(f"🔒 **Pro Feature Locked:** `{page_title}` is reserved for DataPilot Pro subscribers.")
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 30px; border-radius: 16px; color: white; text-align: center; margin: 20px 0;">
            <h2 style="color: white; margin-bottom: 10px;">👑 Unlock DataPilot Pro Features</h2>
            <p style="font-size: 16px; opacity: 0.9;">Get unlimited access to advanced data cleaning, exploratory analysis, interactive dashboards, AI insights, and executive exports.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("💳 View Subscription Plans", type="primary", use_container_width=True):
                st.switch_page("Home.py")
        with col2:
            # زر للتجربة والاختبار السريع أثناء التطوير
            if st.button("🔑 Unlock Feature (Demo Mode)", type="secondary", use_container_width=True):
                st.session_state["is_subscribed"] = True
                st.toast("🎉 Pro Access Unlocked!", icon="✅")
                st.rerun()

        st.stop()