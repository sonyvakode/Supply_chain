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

# ── GEMINI SETUP ─────────────────────────────────────────
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    gemini = genai.GenerativeModel("gemini-2.0-flash")
    GEMINI_OK = True
except:
    GEMINI_OK = False

# ── SMART AI INSIGHT (UPDATED) ───────────────────────────
def ai_insight(row: pd.Series, cost_saved: float) -> str:
    if not GEMINI_OK:
        insights = []

        # Risk logic
        if row["risk"] >= 70:
            insights.append(
                f"• High disruption risk ({row['risk']}%). Immediate rerouting or contingency planning required."
            )
        elif row["risk"] >= 40:
            insights.append(
                f"• Moderate risk detected on {row['from']} → {row['to']}. Monitor closely for delays."
            )
        else:
            insights.append(
                f"• Stable route with low risk ({row['risk']}%). No intervention needed."
            )

        # Delay logic
        if row["delay"] >= 5:
            insights.append(
                f"• Delay of {row['delay']} days may impact delivery commitments."
            )
        else:
            insights.append(
                f"• ETA of {row['eta']} days is within acceptable limits."
            )

        # Cost optimization
        if cost_saved > 0:
            insights.append(
                f"• Potential savings: ₹{int(cost_saved)} via optimized routing."
            )

        return "\n".join(insights[:2])

    # REAL AI (if API works)
    prompt = f"""
    Analyze shipment:
    Route: {row['from']} → {row['to']}
    Risk: {row['risk']}
    Delay: {row['delay']}
    Cost: ₹{row['cost']}

    Give 2 short actionable insights.
    """

    try:
        res = gemini.generate_content(prompt)
        return res.text
    except:
        return "• Insight temporarily unavailable."

# ── DATA ─────────────────────────────────────────
CITIES = {
    "mumbai": [19.07, 72.87],
    "delhi": [28.61, 77.20],
    "chennai": [13.08, 80.27],
    "bangalore": [12.97, 77.59],
    "hyderabad": [17.38, 78.48],
    "pune": [18.52, 73.85],
}

ROUTES = [
    ("mumbai", "delhi"),
    ("chennai", "bangalore"),
    ("hyderabad", "pune"),
]

def haversine(c1, c2):
    lat1, lon1 = CITIES[c1]
    lat2, lon2 = CITIES[c2]
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def route_cost(frm, to):
    return haversine(frm, to) * 12

# ── DATA GENERATION ─────────────────────────────────
def build_dataframe():
    rows = []
    for i in range(10):
        frm, to = random.choice(ROUTES)
        risk = random.randint(10, 95)
        rows.append({"id": f"SHP-{1000+i}", "from": frm, "to": to, "risk": risk})
    return pd.DataFrame(rows)

def enrich(df):
    df = df.copy()
    df["delay"] = (df["risk"] // 10)
    df["eta"] = df["delay"] + 5
    df["cost"] = df.apply(lambda r: route_cost(r["from"], r["to"]), axis=1)
    df["status"] = np.where(df["risk"] > 60, "CRITICAL",
                   np.where(df["risk"] > 30, "AT RISK", "SAFE"))
    return df

# ── INIT ─────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = build_dataframe()

df = enrich(st.session_state.df)

# ── UI ─────────────────────────────────────────
st.title("🚚 ChainGuard AI")
st.caption("Offline AI Simulation + Real Optimization")

st.metric("Total Shipments", len(df))

# ── TABLE ───────────────────────────────────────
cost_saved = 5000  # demo constant

for i, row in df.iterrows():
    cols = st.columns([2,2,1,1,2])

    cols[0].write(row["id"])
    cols[1].write(f"{row['from']} → {row['to']}")
    cols[2].write(row["status"])
    cols[3].write(f"{row['risk']}%")

    if cols[4].button("🧠 AI Insight", key=i):
        st.info("🧠 AI Insight (Local Engine)")
        st.write(ai_insight(row, cost_saved))

# ── SIMPLE CHART ────────────────────────────────
st.subheader("📊 Risk Distribution")

fig, ax = plt.subplots()
ax.hist(df["risk"], bins=10)
st.pyplot(fig)
