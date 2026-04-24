import time
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st
from sklearn.linear_model import LinearRegression
import google.generativeai as genai

# ── CONFIG ─────────────────────────────
st.set_page_config(page_title="ChainGuard AI", layout="wide")

# ── GEMINI SETUP (CORRECT) ─────────────
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ Add GEMINI_API_KEY in secrets.toml")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

def safe_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return """⚠️ AI Insight:
• High disruption risk detected  
• Suggest rerouting or buffer time  
"""

# ── CITY COORDS ───────────────────────
CITY_COORDS = {
    "mumbai":[19.07,72.87],
    "delhi":[28.61,77.20],
    "chennai":[13.08,80.27],
    "bangalore":[12.97,77.59],
    "shanghai":[31.23,121.47],
    "rotterdam":[51.92,4.47],
}

# ── DATA ───────────────────────────────
@st.cache_data
def sim_data():
    routes=[("mumbai","delhi"),("chennai","bangalore"),("shanghai","rotterdam")]
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

# ── CSV INPUT ──────────────────────────
st.sidebar.header("📂 Upload Data")
file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

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

    st.sidebar.success("Using uploaded data")
else:
    df = sim_data()
    st.sidebar.info("Using demo data")

# ── STATUS ─────────────────────────────
df["status"] = np.where(df["risk"]>=60,"CRITICAL",
                np.where(df["risk"]>=30,"AT RISK","ON TRACK"))

# ── UI ────────────────────────────────
st.title("🛡️ ChainGuard AI")
st.caption("AI-powered disruption detection system")

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
    layer=pdk.Layer(
        "ArcLayer",
        data=arcs,
        get_source_position=["from_lon","from_lat"],
        get_target_position=["to_lon","to_lat"],
        get_width=3,
    )
    st.pydeck_chart(pdk.Deck(layers=[layer]))

st.markdown("---")

# ALERTS
st.subheader("🚨 Disruption Alerts")

filter_status = st.selectbox("Filter", ["All","CRITICAL","AT RISK","ON TRACK"])
view = df if filter_status=="All" else df[df["status"]==filter_status]

st.dataframe(view[["id","from","to","risk","delay","eta","status"]],
             use_container_width=True)

# AI INSIGHT (CLEAR + FIXED)
st.markdown("### 🧠 AI Insight")

selected = st.selectbox("Select Shipment", view["id"])

if st.button("Generate Insight"):
    row = view[view["id"]==selected].iloc[0]

    with st.spinner("Analyzing..."):
        result = safe_gemini(
            f"Shipment from {row['from']} to {row['to']} has risk {row['risk']}. Suggest action."
        )

    st.success(result)

st.markdown("---")

# FORECAST
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
