import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st
import random
import math
import time

# OPTIONAL Gemini (will silently fail if no quota)
try:
    import google.generativeai as genai
    genai.configure(api_key=st.secrets.get("GEMINI_API_KEY", ""))
    gemini = genai.GenerativeModel("gemini-2.0-flash")
    GEMINI_OK = True
except:
    GEMINI_OK = False

st.set_page_config(page_title="ChainGuard AI", layout="wide", page_icon="🚚")

# ── AI INSIGHT ENGINE (HYBRID) ─────────────────────────────
def ai_insight(row: pd.Series, cost_saved: float) -> str:
    # Try Gemini (will silently fail if quota exceeded)
    if GEMINI_OK:
        try:
            prompt = f"""
            Analyze shipment:
            Route: {row['from']} → {row['to']}
            Risk: {row['risk']}
            Delay: {row['delay']}
            Cost: ₹{row['cost']}

            Give exactly 2 short actionable insights.
            """
            res = gemini.generate_content(prompt)
            return res.text
        except:
            pass  # ⛔ hide API errors completely

    # ── SMART LOCAL AI (fallback) ──
    insights = []

    # Risk logic
    if row["risk"] >= 70:
        insights.append(
            f"• High disruption risk ({row['risk']}%). Immediate rerouting or contingency planning required."
        )
    elif row["risk"] >= 40:
        insights.append(
            f"• Moderate risk on {row['from']} → {row['to']}. Monitor closely for delays."
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
            f"• ETA {row['eta']} days is within acceptable limits."
        )

    # Cost logic
    if cost_saved > 0:
        insights.append(
            f"• Optimization opportunity: Save approx ₹{int(cost_saved)}."
        )

    return "\n".join(insights[:2])


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
    ("bangalore", "hyderabad"),
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


# ── DATA GENERATION ─────────────────────────────
def build_dataframe(n=12):
    rows = []
    for i in range(n):
        frm, to = random.choice(ROUTES)
        risk = random.randint(10, 95)
        rows.append({
            "id": f"SHP-{1000+i}",
            "from": frm,
            "to": to,
            "risk": risk
        })
    return pd.DataFrame(rows)

def enrich(df):
    df = df.copy()
    df["delay"] = (df["risk"] // 10)
    df["eta"] = df["delay"] + 5
    df["cost"] = df.apply(lambda r: route_cost(r["from"], r["to"]), axis=1)

    df["status"] = np.where(df["risk"] >= 60, "CRITICAL",
                   np.where(df["risk"] >= 30, "AT RISK", "ON TRACK"))
    return df


# ── SESSION STATE ─────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = build_dataframe()

df = enrich(st.session_state.df)

# ── HEADER ─────────────────────────────────────
st.title("🚚 ChainGuard AI")
st.caption("AI-Powered Supply Chain Optimization · Hybrid Intelligence Engine")

# ── KPI ────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Total Shipments", len(df))
col2.metric("Critical", int((df["risk"] >= 60).sum()))
col3.metric("Avg Risk", f"{df['risk'].mean():.1f}")

st.divider()

# ── MAP ────────────────────────────────────────
st.subheader("🌍 Network Map")

lines = []
for _, row in df.iterrows():
    f_lat, f_lon = CITIES[row["from"]]
    t_lat, t_lon = CITIES[row["to"]]

    color = (
        [255, 75, 75, 200] if row["status"] == "CRITICAL" else
        [255, 165, 0, 180] if row["status"] == "AT RISK" else
        [0, 200, 130, 150]
    )

    lines.append({
        "from": [f_lon, f_lat],
        "to": [t_lon, t_lat],
        "color": color
    })

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/dark-v10",
    initial_view_state=pdk.ViewState(latitude=20, longitude=78, zoom=4),
    layers=[
        pdk.Layer(
            "LineLayer",
            data=lines,
            get_source_position="from",
            get_target_position="to",
            get_color="color",
            get_width=3
        )
    ]
))

st.divider()

# ── SHIPMENTS ──────────────────────────────────
st.subheader("📦 Shipment Insights")

cost_saved_demo = 5000  # demo value

for i, row in df.iterrows():
    cols = st.columns([1.5, 2.5, 1, 1, 1.5])

    cols[0].write(f"**{row['id']}**")
    cols[1].write(f"{row['from']} → {row['to']}")
    cols[2].write(row["status"])
    cols[3].write(f"{row['risk']}%")

    if cols[4].button("🧠 AI Insight", key=i):
        st.info("🧠 AI Insight (Hybrid Engine)")
        st.write(ai_insight(row, cost_saved_demo))

st.divider()

# ── CHART ──────────────────────────────────────
st.subheader("📊 Risk Distribution")

fig, ax = plt.subplots()
ax.hist(df["risk"], bins=10)
st.pyplot(fig)

# ── AUTO REFRESH (optional demo) ───────────────
if st.toggle("🔄 Live Simulation"):
    time.sleep(3)
    st.session_state.df = build_dataframe()
    st.rerun()
