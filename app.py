"""
ChainGuard AI — FINAL WINNER VERSION (Judge-Optimized)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st
import random
import google.generativeai as genai
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="ChainGuard AI", layout="wide")

# ── GEMINI SETUP ──────────────────────
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ Please add GEMINI_API_KEY in Secrets")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

def safe_gemini(prompt):
    try:
        return model.generate_content(prompt).text
    except:
        return "⚠️ AI temporarily unavailable. Suggest rerouting or adding buffer."

# ── CITY COORDS ───────────────────────
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
    for i in range(10):
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

# ── CSV INPUT ─────────────────────────
st.sidebar.header("📂 Upload CSV")
file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if file:
    df = pd.read_csv(file)
    df.columns = df.columns.str.lower()

    if not {"id","from","to"}.issubset(df.columns):
        st.error("❌ CSV must contain columns: id, from, to")
        st.stop()

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
st.caption("AI-powered disruption detection and decision-support system")
st.info("🇮🇳 Designed to support Indian MSMEs in logistics decision-making")

# KPIs
c1,c2,c3 = st.columns(3)
c1.metric("Shipments", len(df))
c2.metric("Critical", int((df["risk"]>=60).sum()))
c3.metric("Avg Delay", f"{df['delay'].mean():.1f} days")

# ── AI SYSTEM INSIGHT ─────────────────
st.markdown("### 🤖 AI System Insight")

if st.button("Generate System Insight"):
    summary = df.describe().to_string()
    with st.spinner("Analyzing..."):
        st.success(safe_gemini(
            f"Analyze this supply chain data:\n{summary}\nGive key risks and recommendations."
        ))

st.markdown("---")

# ── MAP ───────────────────────────────
st.subheader("🗺️ Shipment Map")

points=[]
for _,s in df.iterrows():
    if s["from"] in CITY_COORDS:
        lat,lon = CITY_COORDS[s["from"]]
        color = [255,0,0] if s["status"]=="CRITICAL" else [0,128,255]
        points.append({"lat":lat,"lon":lon,"color":color})

if points:
    st.pydeck_chart(pdk.Deck(
        layers=[pdk.Layer(
            "ScatterplotLayer",
            data=points,
            get_position=["lon","lat"],
            get_color="color",
            get_radius=50000,
        )]
    ))
else:
    st.info("Map unavailable for uploaded locations")

st.markdown("---")

# ── ALERTS ────────────────────────────
st.subheader(" Disruption Alerts")

st.dataframe(df[["id","from","to","risk","status"]],
             use_container_width=True)

st.markdown("### 🔍 Details")

for i,s in df.iterrows():
    with st.expander(f"{s['id']} | {s['from']} → {s['to']} | Risk {s['risk']}%"):

        st.write(f"Delay: {s['delay']} days")
        st.write(f"ETA: {s['eta']} days")

        # AI EXPLANATION (CRITICAL FEATURE)
        if st.button("🧠 Why is this critical?", key=f"why{i}"):
            with st.spinner("Analyzing..."):
                st.info(safe_gemini(
                    f"Explain why shipment from {s['from']} to {s['to']} with risk {s['risk']} is critical and how to mitigate it."
                ))

st.markdown("---")

# ── FORECAST ──────────────────────────
st.subheader("📈 Demand Forecast")

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
