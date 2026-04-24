"""
ChainGuard AI — FINAL MOBILE FRIENDLY + DARK MODE
"""

import time
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st
from sklearn.linear_model import LinearRegression
from google import genai

# ── CONFIG ─────────────────────────────
st.set_page_config(page_title="ChainGuard AI", layout="wide")

# ── DARK MODE CSS ──────────────────────
st.markdown("""
<style>
body { background-color: #0f172a; color: white; }
.block-container { padding: 1rem; }
.stButton>button {
    background-color: #1e293b;
    color: white;
    border-radius: 10px;
}
.stDataFrame { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── GEMINI ─────────────────────────────
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ Add Gemini API key")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def safe_gemini(prompt):
    for _ in range(2):
        try:
            return client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            ).text
        except:
            time.sleep(1)
    return "⚠️ AI temporarily busy. Suggested: reroute or buffer."

# ── DATA ───────────────────────────────
CITY_COORDS = {
    "mumbai":[19.07,72.87],
    "delhi":[28.61,77.20],
    "chennai":[13.08,80.27],
    "bangalore":[12.97,77.59],
    "shanghai":[31.23,121.47],
    "rotterdam":[51.92,4.47],
}

@st.cache_data
def sim_data():
    routes=[("mumbai","delhi"),("chennai","bangalore"),("shanghai","rotterdam")]
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

# ── CSV ────────────────────────────────
file = st.file_uploader("📂 Upload CSV (optional)", type=["csv"])

if file:
    df = pd.read_csv(file)
    df.columns = df.columns.str.lower()

    if "risk" not in df.columns:
        df["risk"] = np.random.randint(20,80,len(df))
    if "delay" not in df.columns:
        df["delay"] = df["risk"]//5
    if "eta" not in df.columns:
        df["eta"] = df["delay"]+10

    df["from"] = df["from"].str.lower()
    df["to"] = df["to"].str.lower()
else:
    df = sim_data()

df["status"] = np.where(df["risk"]>=60,"CRITICAL",
                np.where(df["risk"]>=30,"AT RISK","ON TRACK"))

# ── TITLE ──────────────────────────────
st.title("🛡️ ChainGuard AI")
st.caption("AI-powered disruption detection system")

# ── KPIs (mobile friendly) ─────────────
col1, col2 = st.columns(2)
col1.metric("Shipments", len(df))
col2.metric("Critical", int((df["risk"]>=60).sum()))

st.metric("Avg Delay", f"{df['delay'].mean():.1f} days")

# ── MAP ───────────────────────────────
st.subheader("🗺️ Shipments")

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

# ── ALERTS ─────────────────────────────
st.subheader("🚨 Alerts")

filter_status = st.selectbox("Filter", ["All","CRITICAL","AT RISK","ON TRACK"])
view = df if filter_status=="All" else df[df["status"]==filter_status]

st.dataframe(view, use_container_width=True)

# ── AI INSIGHT FIX (VISIBLE) ───────────
st.subheader("🧠 AI Insights")

selected = st.selectbox("Select Shipment", view["id"])

if st.button("Get AI Insight"):
    row = view[view["id"]==selected].iloc[0]

    with st.spinner("Analyzing..."):
        result = safe_gemini(
            f"Shipment from {row['from']} to {row['to']} risk {row['risk']}. Suggest action."
        )

    st.success(result)

# ── FORECAST ───────────────────────────
st.subheader("📈 Forecast")

x=np.arange(1,20)
y=200+x*5+np.random.normal(0,20,19)

model=LinearRegression().fit(x.reshape(-1,1),y)
future=np.arange(20,30)
pred=model.predict(future.reshape(-1,1))

fig,ax=plt.subplots()
ax.plot(x,y,label="Actual")
ax.plot(future,pred,label="Forecast")
ax.legend()

st.pyplot(fig)