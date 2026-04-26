import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st
import math
import time
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="ChainGuard", layout="wide", page_icon="🚚")

# ── CITY DATA (REAL GEO COORDS) ───────────────────────────────────────────────
CITIES = {
    "mumbai":[19.07,72.87], "delhi":[28.61,77.20],
    "chennai":[13.08,80.27], "bangalore":[12.97,77.59],
    "hyderabad":[17.38,78.48], "pune":[18.52,73.85],
    "kolkata":[22.57,88.36], "jaipur":[26.91,75.79],
    "ahmedabad":[23.02,72.57]
}

# ── REAL DISTANCE CALCULATION ─────────────────────────────────────────────────
def haversine(c1,c2):
    lat1,lon1=CITIES[c1]
    lat2,lon2=CITIES[c2]
    R=6371
    dlat=math.radians(lat2-lat1)
    dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R*2*math.asin(math.sqrt(a))

def route_cost(frm,to):
    return haversine(frm,to)*12  # ₹12/km realistic baseline

# ── VALIDATION ────────────────────────────────────────────────────────────────
def validate(df):
    df.columns=df.columns.str.lower().str.strip()
    required={"id","from","to","delay"}
    if not required.issubset(df.columns):
        return False,"CSV must contain: id, from, to, delay"
    return True,""

# ── REAL ENRICHMENT ───────────────────────────────────────────────────────────
def enrich(df):
    df=df.copy()
    
    # Real distance
    df["distance"]=df.apply(lambda r:haversine(r["from"],r["to"]),axis=1)
    
    # Real cost
    df["cost"]=df["distance"]*12
    
    # Risk derived logically (not random)
    df["risk"]=np.clip((df["delay"]*8)+(df["distance"]/100),0,100).astype(int)
    
    df["status"]=np.where(df["risk"]>=60,"CRITICAL",
                   np.where(df["risk"]>=30,"AT RISK","ON TRACK"))
    
    return df

# ── UI ────────────────────────────────────────────────────────────────────────
st.title("🚚 ChainGuard — Real Supply Chain Intelligence")

uploaded=st.file_uploader("Upload Real Shipment Data CSV")

if uploaded:
    df=pd.read_csv(uploaded)
    
    ok,msg=validate(df)
    if not ok:
        st.error(msg)
        st.stop()
    
    df["from"]=df["from"].str.lower()
    df["to"]=df["to"].str.lower()
    
    df=enrich(df)

    # ── KPI ───────────────────────────────────────────────────────────────────
    c1,c2,c3=st.columns(3)
    c1.metric("Shipments",len(df))
    c2.metric("Critical",(df["risk"]>=60).sum())
    c3.metric("Total Cost",f"₹{df['cost'].sum():,.0f}")

    # ── MAP ───────────────────────────────────────────────────────────────────
    st.subheader("🌍 Live Network")

    lines=[]
    for _,row in df.iterrows():
        f=CITIES[row["from"]]
        t=CITIES[row["to"]]
        
        color=[255,75,75] if row["status"]=="CRITICAL" else [0,200,130]
        
        lines.append({
            "from":[f[1],f[0]],
            "to":[t[1],t[0]],
            "color":color
        })

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=pdk.ViewState(latitude=20,longitude=78,zoom=4),
        layers=[
            pdk.Layer("LineLayer",
                      data=lines,
                      get_source_position="from",
                      get_target_position="to",
                      get_color="color",
                      get_width=4)
        ]
    ))

    # ── TABLE ─────────────────────────────────────────────────────────────────
    st.subheader("📦 Shipment Analysis")
    st.dataframe(df)

    # ── REAL FORECAST (BASED ON DATA) ─────────────────────────────────────────
    st.subheader("📈 Demand Forecast (Real Trend)")

    demand=df.groupby("from").size().values.reshape(-1,1)
    
    if len(demand)>2:
        x=np.arange(len(demand)).reshape(-1,1)
        model=LinearRegression().fit(x,demand)
        
        future=model.predict(np.arange(len(demand),len(demand)+5).reshape(-1,1))
        
        fig,ax=plt.subplots()
        ax.plot(demand,label="Current Demand")
        ax.plot(range(len(demand),len(demand)+5),future,label="Forecast")
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning("Not enough data for forecasting")

else:
    st.info("Upload real dataset to begin")
