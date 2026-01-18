import streamlit as st
from engine import TriageEngine
import pandas as pd
from PIL import Image
import io
# ReportLab imports needed for PDF logic (omitted here for brevity in constraints, but kept in env)
# We focus on the UI update requests

st.set_page_config(page_title="Disaster Triage AI PRO (Offline)", page_icon="🚑", layout="centered")

@st.cache_resource
def get_engine():
    return TriageEngine()

engine = get_engine()

st.title("🚑 Disaster Triage AI (Offline)")
st.markdown("### 100% Free • Local Analysis • Privacy Focused")

# --- UI CONTROLS ---

message = st.text_area("Distress Message", height=100, placeholder="Describe situation (e.g., 'Flooding in basement, elderly trapped')...")
uploaded_file = st.file_uploader("Upload Scene Image", type=['jpg', 'jpeg', 'png'])

image_display_width = st.slider("Image Display Width (px)", min_value=250, max_value=1000, value=500)

image = None
if uploaded_file is not None:
    # Metadata
    file_bytes = uploaded_file.getvalue()
    size_kb = len(file_bytes) / 1024
    
    image = Image.open(uploaded_file)
    width, high = image.size
    
    st.caption(f"Image Metadata: {width}x{high} px | Size: {size_kb:.2f} KB")
    
    # User controlled width
    st.image(image, caption='Evidence', width=image_display_width)

if st.button("🚨 Analyze Situation", type="primary"):
    if message or image:
        with st.spinner("Running Local Heuristics..."):
            result = engine.predict(message, image)
            
            # --- RESULTS ---
            color_map = {'High': '#ff4b4b', 'Medium': '#ffa500', 'Low': '#09ab3b'}
            bg_color = color_map.get(result['final_priority'], '#808080')
            
            st.markdown(f"""
            <div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; text-align: center; color: white; margin-bottom: 20px;">
                <h1 style="margin:0; color: white;">{result['final_priority'].upper()} PRIORITY</h1>
                <h3 style="margin:0; color: white; opacity: 0.9;">{result['final_category']}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Risk Metrics Grid
            if result['image_result']:
                st.markdown("### 📸 Image Risk Analysis")
                r1, r2, r3, r4 = st.columns(4)
                
                img_res = result['image_result']
                
                with r1:
                    st.metric("Flood Severity", img_res['flood_severity'], delta=f"{img_res['water_coverage']:.1f}% Water")
                with r2:
                    st.metric("Visibility", "High" if "Day" in img_res['visibility'] else "Low", delta=img_res['visibility'], delta_color="off")
                with r3:
                    is_fire = img_res['fire_risk'] == 'Detected'
                    st.metric("Fire Risk", img_res['fire_risk'], delta="🔥 ALERT" if is_fire else "Safe", delta_color="inverse")
                with r4:
                    st.metric("Debris/Rubble", img_res['debris_risk'])
                
                st.markdown("---")

            # --- ACTION CARDS ---
            st.markdown("### 📋 Emergency Action Plan")
            
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.error("⚡ IMMEDIATE ACTIONS")
                for item in result['action_cards']['immediate']:
                    st.markdown(f"**•** {item}")
                    
            with c2:
                st.warning("🚫 DO NOT")
                for item in result['action_cards']['not_to_do']:
                    st.markdown(f"**•** {item}")
                    
            with c3:
                st.info("🧰 CHECKLIST")
                for item in result['action_cards']['checklist']:
                    st.markdown(f"**•** {item}")

            # Explainability
            with st.expander("Why this result?"):
                if result['risk_flags']:
                    st.write(f"**Vulnerabilities Flagged:** {', '.join(result['risk_flags'])}")
                if result['text_result']['matched_keywords']:
                    st.write(f"**Keywords:** {', '.join(result['text_result']['matched_keywords'])}")
                if result['image_result']:
                    st.write("**Image Analysis Factor:**")
                    st.json(result['image_result'])
            
    else:
        st.warning("Please enter a distress message or upload an image.")

# Sidebar
st.sidebar.markdown("## 🛡️ Privacy Note")
st.sidebar.info("This application runs 100% offline. No data is sent to the cloud.")
