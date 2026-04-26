import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st
import random
import math
import time
import google.generativeai as genai
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="ChainGuard", layout="wide")

# ── STYLE ─────────────────────────────
st.markdown("""
<style>
.status-critical {color:#ff4b4b; font-weight:bold;}
.status-risk {color:#ffa500; font-weight:bold;}
.status-ok {color:#00c853; font-weight:bold;}
.card {
    padding:15px;
    border-radius:10px;
    background-color:#111;
    margin-bottom:10px;
}
.big {font-size:20px; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# ── GEMINI ────────────────────────────
genai.configure(api_key=st.secrets.get("GEMINI_API_KEY",""))
model = genai.GenerativeModel("gemini-1.5-flash")

def ai_insight(risk, cost_saved):
    try:
        res = model.generate_content(
            f"Shipment risk {risk}%, cost saved {cost_saved}. Give 2 short business insights."
        )
        return res.text
    except:
        return "• Risk reduced\n• Cost optimized"

# ── CITY DATA ─────────────────────────
CITY_COORDS = {
    "mumbai":[19.07,72.87],
    "delhi":[28.61,77.20],
    "chennai":[13.08,80.27],
    "bangalore":[12.97,77.59],
    "hyderabad":[17.38,78.48],
    "pune":[18.52,73.85],
    "kolkata":[22.57,88.36],
}

def distance(c1,c2):
    lat1,lon1 = CITY_COORDS[c1]
    lat2,lon2 = CITY_COORDS[c2]
    return math.sqrt((lat1-lat2)**2+(lon1-lon2)**2)

def predict_risk(base):
    trend = base + np.random.normal(0,5)
    return int(np.clip(trend,0,100))

# ── DATA ──────────────────────────────
@st.cache_data
def sim_data():
    routes=[("mumbai","delhi"),("chennai","bangalore"),("hyderabad","pune")]
    data=[]
    for i in range(12):
        frm,to=random.choice(routes)
        risk=int(np.clip(np.random.normal(50,20),0,100))
        data.append({
            "id":f"SHP-{1000+i}",
            "from":frm,
            "to":to,
            "risk":risk
        })
    return pd.DataFrame(data)

file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if file:
    df = pd.read_csv(file)
    df.columns = df.columns.str.lower().str.strip()
    df["from"] = df["from"].str.lower()
    df["to"] = df["to"].str.lower()
else:
    df = sim_data()

# ── AUTO MODE ─────────────────────────
auto_mode = st.sidebar.toggle("⚡ Auto Mode (Live Simulation)", value=False)

# apply smarter risk
df["risk"] = df["risk"].apply(predict_risk)

# compute fields
df["delay"] = df["risk"]//5
df["eta"] = df["delay"]+10
df["cost"] = df.apply(lambda x: distance(x["from"],x["to"])*100, axis=1)

df["status"] = np.where(df["risk"]>=60,"CRITICAL",
                np.where(df["risk"]>=30,"AT RISK","ON TRACK"))

# ── FILTERS ───────────────────────────
st.sidebar.header("Filters")
status_filter = st.sidebar.multiselect(
    "Status", ["CRITICAL","AT RISK","ON TRACK"],
    default=["CRITICAL","AT RISK","ON TRACK"]
)

df = df[df["status"].isin(status_filter)]

# auto refresh
if auto_mode:
    time.sleep(2)
    st.rerun()

# ── HEADER ────────────────────────────
st.title("🚚 ChainGuard")
st.caption("AI Supply Chain Optimization Prototype")

# KPIs
c1,c2,c3 = st.columns(3)
c1.metric("Shipments", len(df))
c2.metric("Critical", int((df["risk"]>=60).sum()))
c3.metric("Total Cost", f"{df['cost'].sum():.0f}")

st.markdown("---")

# ── OPTIMIZATION ──────────────────────
st.subheader("⚡ Smart Optimization")

before_cost = df["cost"].sum()
before_risk = df["risk"].mean()

optimize = st.button("Optimize Network")

if optimize:
    for i in df.index:
        if df.loc[i,"risk"]>=60:
            frm = df.loc[i,"from"]
            best = min(CITY_COORDS.keys(), key=lambda c: distance(frm,c))

            df.loc[i,"to"] = best
            df.loc[i,"risk"] = max(20, df.loc[i,"risk"]-30)

    df["delay"] = df["risk"]//5
    df["eta"] = df["delay"]+10
    df["cost"] = df.apply(lambda x: distance(x["from"],x["to"])*100, axis=1)

after_cost = df["cost"].sum()
after_risk = df["risk"].mean()

if optimize:
    col1,col2 = st.columns(2)
    col1.markdown(f"<div class='card big'>💰 Cost Saved: {before_cost-after_cost:.0f}</div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card big'>📉 Risk Reduced: {before_risk-after_risk:.1f}%</div>", unsafe_allow_html=True)

    # impact chart
    st.subheader("📊 Impact Visualization")
    fig, ax = plt.subplots()
    ax.bar(["Before","After"], [before_cost, after_cost])
    ax.set_title("Cost Comparison")
    st.pyplot(fig)

st.markdown("---")

# ── MAP ───────────────────────────────
st.subheader("🌍 Network Flow")

pulse = int(time.time()) % 2

lines=[]
for _,s in df.iterrows():
    if s["from"] in CITY_COORDS and s["to"] in CITY_COORDS:
        f_lat,f_lon = CITY_COORDS[s["from"]]
        t_lat,t_lon = CITY_COORDS[s["to"]]

        color = [255,0,0] if s["status"]=="CRITICAL" else (
            [0,255,150] if pulse else [0,200,100]
        )

        lines.append({
            "from":[f_lon,f_lat],
            "to":[t_lon,t_lat],
            "color":color
        })

st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(latitude=20, longitude=78, zoom=4),
    layers=[pdk.Layer(
        "LineLayer",
        data=lines,
        get_source_position="from",
        get_target_position="to",
        get_color="color",
        get_width=4,
    )]
))

st.markdown("---")

# ── SHIPMENTS ─────────────────────────
st.subheader("📦 Shipment Insights")

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

        if st.button("AI Insight", key=i):
            st.info(ai_insight(s["risk"], before_cost-after_cost))

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
