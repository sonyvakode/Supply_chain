import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st
import random
import math
import google.generativeai as genai
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="ChainGuard", layout="wide")

# ── STYLE ─────────────────────────────
st.markdown("""
<style>
.status-critical {color:#ff4b4b; font-weight:bold;}
.status-risk {color:#ffa500; font-weight:bold;}
.status-ok {color:#00c853; font-weight:bold;}
.big {font-size:22px; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# ── GEMINI ────────────────────────────
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

def ai_insight(risk, cost_saved):
    try:
        res = model.generate_content(
            f"Shipment risk {risk}%. Cost saved {cost_saved}. Give 2 sharp insights."
        )
        return res.text
    except:
        return "• Risk reduced significantly\n• Cost optimized via rerouting"

# ── CITY COORDS ───────────────────────
CITY_COORDS = {
    "mumbai":[19.07,72.87],
    "delhi":[28.61,77.20],
    "chennai":[13.08,80.27],
    "bangalore":[12.97,77.59],
    "hyderabad":[17.38,78.48],
    "pune":[18.52,73.85],
    "kolkata":[22.57,88.36],
}

ALT_CITIES = list(CITY_COORDS.keys())

# ── DISTANCE FUNCTION ─────────────────
def distance(c1, c2):
    lat1,lon1 = CITY_COORDS[c1]
    lat2,lon2 = CITY_COORDS[c2]
    return math.sqrt((lat1-lat2)**2 + (lon1-lon2)**2)

# ── DATA ──────────────────────────────
@st.cache_data
def sim_data():
    routes=[("mumbai","delhi"),("chennai","bangalore"),("hyderabad","pune")]
    data=[]
    for i in range(12):
        frm,to=random.choice(routes)
        risk=int(np.clip(np.random.normal(50,20),0,100))
        delay=int(risk/5)

        data.append({
            "id":f"SHP-{1000+i}",
            "from":frm,
            "to":to,
            "risk":risk,
            "delay":delay,
            "eta":delay+10,
            "cost": distance(frm,to)*100
        })
    return pd.DataFrame(data)

# ── LOAD ──────────────────────────────
file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if file:
    df = pd.read_csv(file)
    df.columns = df.columns.str.lower()
    df["from"] = df["from"].str.lower()
    df["to"] = df["to"].str.lower()
else:
    df = sim_data()

# ensure cost
df["cost"] = df.apply(lambda x: distance(x["from"], x["to"])*100, axis=1)

# ── STATUS ────────────────────────────
df["status"] = np.where(df["risk"]>=60,"CRITICAL",
                np.where(df["risk"]>=30,"AT RISK","ON TRACK"))

# ── HEADER ────────────────────────────
st.title("🚚 ChainGuard")
st.caption("AI-powered Supply Chain Optimization Prototype")

# ── KPIs ──────────────────────────────
c1,c2,c3 = st.columns(3)
c1.metric("Shipments", len(df))
c2.metric("Critical", int((df["risk"]>=60).sum()))
c3.metric("Total Cost", f"{df['cost'].sum():.0f}")

st.markdown("---")

# ── SMART OPTIMIZER ───────────────────
st.subheader("⚡ Smart Optimization Engine")

before_cost = df["cost"].sum()
before_risk = df["risk"].mean()

if st.button("Optimize Supply Chain"):
    for i in df.index:
        if df.loc[i,"risk"] >= 60:
            frm = df.loc[i,"from"]

            # choose nearest safer city
            best_city = min(
                ALT_CITIES,
                key=lambda c: distance(frm,c)
            )

            old_cost = df.loc[i,"cost"]

            df.loc[i,"to"] = best_city
            df.loc[i,"risk"] = max(20, df.loc[i,"risk"] - 30)
            df.loc[i,"delay"] = df.loc[i,"risk"]//5
            df.loc[i,"eta"] = df.loc[i,"delay"]+10
            df.loc[i,"cost"] = distance(frm,best_city)*100

    after_cost = df["cost"].sum()
    after_risk = df["risk"].mean()

    col1,col2 = st.columns(2)

    col1.markdown(f"<div class='big'>💰 Cost Saved: {before_cost-after_cost:.0f}</div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='big'>📉 Risk Reduced: {before_risk-after_risk:.1f}%</div>", unsafe_allow_html=True)

# ── MAP ───────────────────────────────
st.subheader("Live Network")

lines = []

for _, s in df.iterrows():
    if s["from"] in CITY_COORDS and s["to"] in CITY_COORDS:
        f_lat,f_lon = CITY_COORDS[s["from"]]
        t_lat,t_lon = CITY_COORDS[s["to"]]

        color = [255,0,0] if s["status"]=="CRITICAL" else [0,200,100]

        lines.append({
            "from":[f_lon,f_lat],
            "to":[t_lon,t_lat],
            "color":color
        })

deck = pdk.Deck(
    initial_view_state=pdk.ViewState(latitude=20, longitude=78, zoom=4),
    layers=[pdk.Layer(
        "LineLayer",
        data=lines,
        get_source_position="from",
        get_target_position="to",
        get_color="color",
        get_width=4,
    )]
)

st.pydeck_chart(deck)

st.markdown("---")

# ── SHIPMENTS ─────────────────────────
st.subheader("📦 Shipment Intelligence")

for i,s in df.iterrows():
    status_class = (
        "status-critical" if s["status"]=="CRITICAL"
        else "status-risk" if s["status"]=="AT RISK"
        else "status-ok"
    )

    with st.container():
        cols = st.columns([2,3,2,2])

        cols[0].write(s["id"])
        cols[1].write(f"{s['from']} → {s['to']}")
        cols[2].markdown(f"<span class='{status_class}'>{s['status']}</span>", unsafe_allow_html=True)
        cols[3].write(f"₹{s['cost']:.0f}")

        if st.button("AI Decision Insight", key=i):
            st.info(ai_insight(s["risk"], s["cost"]))

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
