import streamlit as st
import pandas as pd
from groq import Groq

st.set_page_config(page_title="TerraTrack Mining Fleet", layout="wide")

# 1. Fetch Groq API key safely from Streamlit secrets
groq_api_key = st.secrets.get("GROQ_API_KEY", None)

if groq_api_key:
    client = Groq(api_key=groq_api_key)
else:
    client = None
    st.warning("⚠️ Groq API Key missing. Please add GROQ_API_KEY to your Streamlit secrets.")

# 2. Default Machinery List (Add permanent assets here)
DEFAULT_FLEET = [
    {"id": "TR-001", "type": "Semi-Trailer", "model": "Sinotruk HOWO", "status": "Active", "hours": 1420, "location": "Site A - Clay Pit"},
    {"id": "EX-001", "type": "Excavator", "model": "CAT 349D", "status": "Active", "hours": 3200, "location": "Site A - Clay Pit"},
    {"id": "EX-002", "type": "Excavator", "model": "Komatsu PC400", "status": "Under Repair", "hours": 4100, "location": "Workshop"},
    {"id": "RB-001", "type": "Rock Breaker", "model": "Furukawa F45", "status": "Active", "hours": 890, "location": "Site B - Quarry"},
]

# Store fleet in session state so you can add new equipment on screen
if "fleet_df" not in st.session_state:
    st.session_state.fleet_df = pd.DataFrame(DEFAULT_FLEET)

# 3. Sidebar Controls
st.sidebar.title("🚜 TerraTrack Control")

selected_asset_id = st.sidebar.selectbox(
    "Select Equipment:",
    options=st.session_state.fleet_df["id"].tolist()
)

# Form to add new machinery dynamically
with st.sidebar.expander("➕ Add New Machinery"):
    with st.form("add_machinery_form"):
        new_id = st.text_input("Asset ID (e.g., TR-002, DZ-001)")
        new_type = st.selectbox("Type", ["Semi-Trailer", "Excavator", "Rock Breaker", "Bulldozer", "Dump Truck"])
        new_model = st.text_input("Model")
        new_hours = st.number_input("Meter Hours", min_value=0, value=0)
        new_location = st.text_input("Location", "Site A")
        
        submitted = st.form_submit_button("Add to Fleet")
        if submitted and new_id:
            new_row = {"id": new_id, "type": new_type, "model": new_model, "status": "Active", "hours": new_hours, "location": new_location}
            st.session_state.fleet_df = pd.concat([st.session_state.fleet_df, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Added {new_id} to fleet!")
            st.rerun()

# 4. Main Dashboard Screen
st.title("🚜 TerraTrack Mining Fleet Dashboard")

st.subheader("Fleet Inventory")
st.dataframe(st.session_state.fleet_df, use_container_width=True)

# Display Selected Machine Details
asset_data = st.session_state.fleet_df[st.session_state.fleet_df["id"] == selected_asset_id].iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("Asset ID", asset_data["id"])
col2.metric("Type / Model", f"{asset_data['type']} ({asset_data['model']})")
col3.metric("Operating Hours", f"{asset_data['hours']} hrs")

# 5. Groq AI Integration
st.divider()
st.subheader("🤖 Groq AI Operational Diagnostics")

user_prompt = st.text_area(
    "Ask Groq AI for advice:", 
    f"Provide a maintenance checklist for {asset_data['type']} ({asset_data['model']}) at {asset_data['hours']} operating hours."
)

if st.button("Generate Insights with Groq"):
    if client:
        with st.spinner("Analyzing with Groq AI..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a heavy machinery mining fleet operations specialist."},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                )
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Groq API Error: {e}")
    else:
        st.error("Missing Groq API Key! Please configure GROQ_API_KEY in your Streamlit secrets.")