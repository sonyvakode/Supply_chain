"""
ChainGuard AI — FINAL CLEAN VERSION (NO CRASH + CSV VALIDATION)
"""

import time
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st
from sklearn.linear_model import LinearRegression
import google.generativeai as genai

st.set_page_config(page_title="ChainGuard AI", layout="wide")

# ── GEMINI ─────────────────────────────
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ Please add GEMINI_API_KEY in Secrets")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

def safe_gemini(prompt):
    try:
        return model.generate_content(prompt).text
    except:
        return "⚠️ AI temporarily unavailable. Suggested: reroute or add buffer."

# ── CITY MAP ───────────────────────────
CITY_COORDS = {
    "mumbai":[19.07,72.87],
    "delhi":[28.61,77.20],
    "chennai":[13.08,80.27],
    "bangalore":[12.97,77.59],
}

# ── DEMO DATA ─────────────────────────
@st.cache_data
def sim_data():
    routes=[("mumbai","delhi"),("chennai","bangalore")]
    data=[]
    for i in range(8):
        frm,to=random.choice(routes)
        risk=int(np.clip(np.random.normal(50,20),0,100))
        delay=int(risk/5)
        data.append({
            "id":f"SHP-{1000+i}",
            "from":frm,
            "to":to,
            "risk":risk,
            "delay":delay,
            "eta":delay+10
        })
    return pd.DataFrame(data)

# ── CSV INPUT (SAFE) ───────────────────
st.sidebar.header("📂 Upload CSV")
file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if file:
    df = pd.read_csv(file)
    df.columns = df.columns.str.lower()

    # REQUIRED columns
    required_cols = {"id", "from", "to"}

    if not required_cols.issubset(df.columns):
        st.error("❌ Invalid CSV format. Required columns: id, from, to")
        st.stop()

    # Optional fixes
    if "risk" not in df.columns:
        st.warning("No 'risk' column → generating automatically")
        df["risk"] = np.random.randint(20,80,len(df))

    if "delay" not in df.columns:
        df["delay"] = df["risk"]//5

    if "eta" not in df.columns:
        df["eta"] = df["delay"]+10

    df["from"] = df["from"].str.lower()
    df["to"] = df["to"].str.lower()

    st.sidebar.success("Using uploaded data")

else:
    df = sim_data()
    st.sidebar.info("Using demo data")

# ── STATUS ─────────────────────────────
df["status"] = np.where(df["risk"]>=60,"CRITICAL",
                np.where(df["risk"]>=30,"AT RISK","ON TRACK"))

# ── UI ────────────────────────────────
st.title("🛡️ ChainGuard AI")

# KPIs
c1,c2,c3 = st.columns(3)
c1.metric("Shipments", len(df))
c2.metric("Critical", int((df["risk"]>=60).sum()))
c3.metric("Avg Delay", f"{df['delay'].mean():.1f} days")

st.markdown("---")

# MAP
st.subheader("🗺️ Shipment Map")

arcs=[]
for _,s in df.iterrows():
    if s["from"] in CITY_COORDS and s["to"] in CITY_COORDS:
        f=CITY_COORDS[s["from"]]
        t=CITY_COORDS[s["to"]]
        arcs.append({
            "from_lat":f[0],"from_lon":f[1],
            "to_lat":t[0],"to_lon":t[1],
        })

if arcs:
    st.pydeck_chart(pdk.Deck(layers=[pdk.Layer(
        "ArcLayer",
        data=arcs,
        get_source_position=["from_lon","from_lat"],
        get_target_position=["to_lon","to_lat"],
        get_width=3,
    )]))
else:
    st.info("Map unavailable for given locations")

st.markdown("---")

# ALERTS
st.subheader("🚨 Disruption Alerts")

filter_status = st.selectbox("Filter", ["All","CRITICAL","AT RISK","ON TRACK"])
view = df if filter_status=="All" else df[df["status"]==filter_status]

st.dataframe(view, use_container_width=True)

# AI
st.markdown("### 🧠 AI Insight")

selected = st.selectbox("Select Shipment", view["id"])

if st.button("Generate Insight"):
    row = view[view["id"]==selected].iloc[0]
    with st.spinner("Analyzing..."):
        st.success(safe_gemini(
            f"Shipment from {row['from']} to {row['to']} risk {row['risk']}. Suggest action."
        ))

st.markdown("---")

# FORECAST
st.subheader("📈 Forecast")

x=np.arange(1,20)
y=200+x*5+np.random.normal(0,20,19)

model_lr=LinearRegression().fit(x.reshape(-1,1),y)
future=np.arange(20,30)
pred=model_lr.predict(future.reshape(-1,1))

fig,ax=plt.subplots()
ax.plot(x,y,label="Actual")
ax.plot(future,pred,label="Forecast")
ax.legend()

st.pyplot(fig)
