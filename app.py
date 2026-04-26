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

# ── GLASS UI STYLE ───────────────────────────────────────────────────────────
st.markdown("""
<style>
.main {background: linear-gradient(135deg,#020617,#0f172a);}
.status-critical { color:#ff4b4b; font-weight:bold; }
.status-risk     { color:#ffa500; font-weight:bold; }
.status-ok       { color:#00c853; font-weight:bold; }

.card {
    backdrop-filter: blur(14px);
    background: rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 16px;
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 10px;
}

.alert {
    padding:10px;
    border-radius:8px;
    margin:6px 0;
    background:rgba(255,75,75,0.15);
    color:#ff4b4b;
    font-size:14px;
}
</style>
""", unsafe_allow_html=True)

# ── GEMINI SETUP ─────────────────────────────────────────────────────────────
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    gemini = genai.GenerativeModel("gemini-1.5-flash")
    GEMINI_OK = True
except:
    GEMINI_OK = False

# ── CITY DATA ────────────────────────────────────────────────────────────────
CITIES = {
    "mumbai":[19.07,72.87], "delhi":[28.61,77.20],
    "chennai":[13.08,80.27], "bangalore":[12.97,77.59],
    "hyderabad":[17.38,78.48], "pune":[18.52,73.85],
    "kolkata":[22.57,88.36], "jaipur":[26.91,75.79],
    "ahmedabad":[23.02,72.57]
}

ROUTES = [
    ("mumbai","delhi"),("chennai","bangalore"),
    ("hyderabad","pune"),("kolkata","delhi"),
    ("mumbai","ahmedabad"),("jaipur","delhi"),
    ("bangalore","hyderabad")
]

# ── DISTANCE ────────────────────────────────────────────────────────────────
def haversine(c1,c2):
    lat1,lon1=CITIES[c1]; lat2,lon2=CITIES[c2]
    R=6371
    dlat=math.radians(lat2-lat1)
    dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R*2*math.asin(math.sqrt(a))

def route_cost(frm,to):
    return haversine(frm,to)*12

# ── ALERT SYSTEM ─────────────────────────────────────────────────────────────
def generate_alerts(df):
    alerts=[]
    for _,row in df.iterrows():
        if row["delay"]>=5:
            alerts.append(f"🚨 Shipment {row['id']} delayed in {row['from'].title()}")
        elif row["risk"]>=70:
            alerts.append(f"⚠️ High risk route: {row['from']} → {row['to']}")
    return alerts

# ── MOVING TRUCKS ────────────────────────────────────────────────────────────
def interpolate_position(lat1,lon1,lat2,lon2,progress):
    lat=lat1+(lat2-lat1)*progress
    lon=lon1+(lon2-lon1)*progress
    return lat,lon

def build_trucks(df):
    now=time.time()
    trucks=[]
    for _,row in df.iterrows():
        f=CITIES[row["from"]]
        t=CITIES[row["to"]]
        progress=(now/8)%1
        lat,lon=interpolate_position(f[0],f[1],t[0],t[1],progress)
        trucks.append({"lat":lat,"lon":lon})
    return trucks

# ── DATA ─────────────────────────────────────────────────────────────────────
def build_dataframe(n=15):
    rows=[]
    for i in range(n):
        frm,to=random.choice(ROUTES)
        risk=int(np.clip(np.random.normal(52,22),0,100))
        rows.append({"id":f"SHP-{1000+i}","from":frm,"to":to,"risk":risk})
    return pd.DataFrame(rows)

def enrich(df):
    df=df.copy()
    df["delay"]=(df["risk"]//8).astype(int)
    df["eta"]=df["delay"]+10
    df["cost"]=df.apply(lambda r:route_cost(r["from"],r["to"]),axis=1)
    df["status"]=np.where(df["risk"]>=60,"CRITICAL",
                   np.where(df["risk"]>=30,"AT RISK","ON TRACK"))
    return df

# ── STATE ────────────────────────────────────────────────────────────────────
if "df_base" not in st.session_state:
    st.session_state.df_base=build_dataframe()

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    auto_mode=st.toggle("🔴 Live Simulation", value=False)

# ── AUTO MODE FIXED ──────────────────────────────────────────────────────────
if auto_mode:
    if "last_update" not in st.session_state:
        st.session_state.last_update=time.time()

    if time.time()-st.session_state.last_update>3:
        st.session_state.df_base=build_dataframe()
        st.session_state.last_update=time.time()
        st.rerun()

df=enrich(st.session_state.df_base)

# ── KPI ──────────────────────────────────────────────────────────────────────
c1,c2,c3=st.columns(3)
c1.metric("Shipments",len(df))
c2.metric("Critical",(df["risk"]>=60).sum())
c3.metric("Cost",f"₹{df['cost'].sum():,.0f}")

# ── ALERTS ───────────────────────────────────────────────────────────────────
st.subheader("🚨 Alerts")
alerts=generate_alerts(df)
for a in alerts:
    st.markdown(f"<div class='alert'>{a}</div>",unsafe_allow_html=True)

# ── MAP WITH TRUCKS ──────────────────────────────────────────────────────────
lines=[]
for _,row in df.iterrows():
    f=CITIES[row["from"]]; t=CITIES[row["to"]]
    color=[255,75,75] if row["status"]=="CRITICAL" else [0,200,130]
    lines.append({"from":[f[1],f[0]],"to":[t[1],t[0]],"color":color})

trucks=build_trucks(df)

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/dark-v10",
    initial_view_state=pdk.ViewState(latitude=20,longitude=78,zoom=4),
    layers=[
        pdk.Layer("LineLayer",data=lines,
                  get_source_position="from",
                  get_target_position="to",
                  get_color="color",
                  get_width=3),

        pdk.Layer("ScatterplotLayer",data=trucks,
                  get_position="[lon,lat]",
                  get_color=[0,200,255],
                  get_radius=30000)
    ]
))

# ── TABLE ────────────────────────────────────────────────────────────────────
st.subheader("📦 Shipments")
st.dataframe(df)
