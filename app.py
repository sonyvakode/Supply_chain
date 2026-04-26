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

st.set_page_config(page_title="ChainGuard", layout="wide", page_icon="🚚")

# ── STYLE ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.status-critical { color:#ff4b4b; font-weight:bold; }
.status-risk     { color:#ffa500; font-weight:bold; }
.status-ok       { color:#00c853; font-weight:bold; }
.card {
    padding: 16px; border-radius: 10px;
    background-color: #0d1b2a; border: 1px solid #1e3a5f;
    margin-bottom: 10px;
}
.big  { font-size: 22px; font-weight: bold; }
.kpi  { font-size: 36px; font-weight: bold; color: #00c6ae; }
.sub  { font-size: 13px; color: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# ── GEMINI SETUP (FIXED) ───────────────────────────────────────────────────────
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    gemini = genai.GenerativeModel("gemini-2.0-flash")  # ✅ FIXED MODEL
    GEMINI_OK = True
except Exception:
    GEMINI_OK = False

def ai_insight(row: pd.Series, cost_saved: float) -> str:
    if not GEMINI_OK:
        return (
            f"• Route {row['from'].title()} → {row['to'].title()} carries a "
            f"{row['risk']}% risk score.\n"
            f"• Potential savings ₹{cost_saved:.0f}"
        )
    prompt = (
        f"Shipment {row['id']} from {row['from']} to {row['to']} "
        f"risk {row['risk']}. Give 2 actionable insights."
    )
    try:
        res = gemini.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"• AI temporarily unavailable: {e}"

# ── CITY COORDINATES ───────────────────────────────────────────────────────────
CITIES = {
    "mumbai":[19.07,72.87], "delhi":[28.61,77.20],
    "chennai":[13.08,80.27], "bangalore":[12.97,77.59],
    "hyderabad":[17.38,78.48], "pune":[18.52,73.85],
    "kolkata":[22.57,88.36], "jaipur":[26.91,75.79],
    "ahmedabad":[23.02,72.57],
}

ROUTES = [
    ("mumbai","delhi"),("chennai","bangalore"),
    ("hyderabad","pune"),("kolkata","delhi"),
    ("mumbai","ahmedabad"),("jaipur","delhi"),
    ("bangalore","hyderabad"),
]

def haversine(c1,c2):
    lat1,lon1=CITIES[c1]
    lat2,lon2=CITIES[c2]
    R=6371
    dlat=math.radians(lat2-lat1)
    dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R*2*math.asin(math.sqrt(a))

def route_cost(frm,to):
    return haversine(frm,to)*12

def score_risk(base_risk):
    return int(np.clip(base_risk + np.random.normal(0,6),0,100))

# ── DATA ──────────────────────────────────────────────────────────────────────
def build_dataframe(n=15):
    rows=[]
    for i in range(n):
        frm,to=random.choice(ROUTES)
        risk=int(np.clip(np.random.normal(52,22),0,100))
        rows.append({"id":f"SHP-{1000+i}","from":frm,"to":to,"risk":risk})
    return pd.DataFrame(rows)

def enrich(df):
    df=df.copy()
    df["risk"]=df["risk"].apply(score_risk)
    df["delay"]=(df["risk"]//8).astype(int)
    df["eta"]=df["delay"]+10
    df["cost"]=df.apply(lambda r:route_cost(r["from"],r["to"]),axis=1)
    df["status"]=np.where(df["risk"]>=60,"CRITICAL",
                   np.where(df["risk"]>=30,"AT RISK","ON TRACK"))
    return df

# ── STATE ─────────────────────────────────────────────────────────────────────
if "df_base" not in st.session_state:
    st.session_state.df_base=build_dataframe()

df=enrich(st.session_state.df_base)

# ── KPI ───────────────────────────────────────────────────────────────────────
c1,c2,c3=st.columns(3)
c1.metric("Shipments",len(df))
c2.metric("Critical",(df["risk"]>=60).sum())
c3.metric("Cost",f"₹{df['cost'].sum():,.0f}")

# ── MAP ───────────────────────────────────────────────────────────────────────
lines=[]
for _,row in df.iterrows():
    f=CITIES[row["from"]]; t=CITIES[row["to"]]
    color=[255,75,75] if row["status"]=="CRITICAL" else [0,200,130]
    lines.append({"from":[f[1],f[0]],"to":[t[1],t[0]],"color":color})

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/dark-v10",
    initial_view_state=pdk.ViewState(latitude=20,longitude=78,zoom=4),
    layers=[
        pdk.Layer("LineLayer",data=lines,
                  get_source_position="from",
                  get_target_position="to",
                  get_color="color",
                  get_width=3)
    ]
))

# ── TABLE ─────────────────────────────────────────────────────────────────────
st.subheader("📦 Shipments")

for i,row in df.iterrows():
    col1,col2,col3,col4=st.columns([1,2,1,1])
    col1.write(row["id"])
    col2.write(f"{row['from']} → {row['to']}")
    col3.write(row["status"])
    if col4.button("AI",key=i):
        st.info(ai_insight(row,0))

# ── FORECAST ──────────────────────────────────────────────────────────────────
st.subheader("📈 Forecast")

x=np.arange(1,20).reshape(-1,1)
y=np.random.rand(19)*100
model=LinearRegression().fit(x,y)
future=model.predict(np.arange(20,30).reshape(-1,1))

fig,ax=plt.subplots()
ax.plot(y)
ax.plot(range(19,29),future)
st.pyplot(fig)
