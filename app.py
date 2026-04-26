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

# ── GEMINI SETUP ───────────────────────────────────────────────────────────────
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    gemini = genai.GenerativeModel("gemini-2.0-flash")  # ✅ ONLY CHANGE
    GEMINI_OK = True
except Exception:
    GEMINI_OK = False

def ai_insight(row: pd.Series, cost_saved: float) -> str:
    if not GEMINI_OK:
        return (
            f"• Route {row['from'].title()} → {row['to'].title()} carries a "
            f"{row['risk']}% risk score. Consider priority handling.\n"
            f"• Optimizing this route could save ₹{cost_saved:.0f} in logistics cost."
        )
    prompt = (
        f"You are a supply chain analyst. Analyze this shipment and give exactly 2 "
        f"short, specific, actionable business insights (bullet points).\n\n"
        f"Shipment ID: {row['id']}\n"
        f"Route: {row['from'].title()} → {row['to'].title()}\n"
        f"Risk Score: {row['risk']}/100\n"
        f"Status: {row['status']}\n"
        f"Estimated Delay: {row['delay']} days\n"
        f"ETA: {row['eta']} days\n"
        f"Logistics Cost: ₹{row['cost']:.0f}\n"
        f"Network Cost Saved After Optimization: ₹{cost_saved:.0f}\n\n"
        f"Be specific about this route and risk level. No generic advice."
    )
    try:
        res = gemini.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"• AI temporarily unavailable: {e}"

# ── CITY COORDINATES ───────────────────────────────────────────────────────────
CITIES = {
    "mumbai":    [19.07, 72.87],
    "delhi":     [28.61, 77.20],
    "chennai":   [13.08, 80.27],
    "bangalore": [12.97, 77.59],
    "hyderabad": [17.38, 78.48],
    "pune":      [18.52, 73.85],
    "kolkata":   [22.57, 88.36],
    "jaipur":    [26.91, 75.79],
    "ahmedabad": [23.02, 72.57],
}

ROUTES = [
    ("mumbai", "delhi"),
    ("chennai", "bangalore"),
    ("hyderabad", "pune"),
    ("kolkata", "delhi"),
    ("mumbai", "ahmedabad"),
    ("jaipur", "delhi"),
    ("bangalore", "hyderabad"),
]

def haversine(c1: str, c2: str) -> float:
    lat1, lon1 = CITIES[c1]
    lat2, lon2 = CITIES[c2]
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def route_cost(frm: str, to: str) -> float:
    return haversine(frm, to) * 12

def score_risk(base_risk: int) -> int:
    return int(np.clip(base_risk + np.random.normal(0, 6), 0, 100))

# ── OPTIMIZATION ENGINE ────────────────────────────────────────────────────────
def find_best_reroute(frm: str, current_to: str) -> tuple[str, int]:
    candidates = [c for c in CITIES if c != frm]
    best_city, best_score = current_to, float("inf")
    for city in candidates:
        dist_score  = route_cost(frm, city) / 20_000
        risk_proxy  = abs(hash(frm + city)) % 40 / 100
        score = 0.4 * dist_score + 0.6 * risk_proxy
        if score < best_score:
            best_score, best_city = score, city
    new_risk = max(15, int(abs(hash(frm + best_city)) % 35) + 10)
    return best_city, new_risk

# ── SIMULATED DATA ─────────────────────────────────────────────────────────────
def build_dataframe(n: int = 15) -> pd.DataFrame:
    rows = []
    for i in range(n):
        frm, to = random.choice(ROUTES)
        risk = int(np.clip(np.random.normal(52, 22), 0, 100))
        rows.append({"id": f"SHP-{1000 + i}", "from": frm, "to": to, "risk": risk})
    return pd.DataFrame(rows)

def enrich(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["risk"]   = df["risk"].apply(score_risk)
    df["delay"]  = (df["risk"] // 8).astype(int)
    df["eta"]    = df["delay"] + 10
    df["cost"]   = df.apply(lambda r: route_cost(r["from"], r["to"]), axis=1)
    df["status"] = np.where(df["risk"] >= 60, "CRITICAL",
                   np.where(df["risk"] >= 30, "AT RISK", "ON TRACK"))
    return df

def validate_upload(df: pd.DataFrame) -> tuple[bool, str]:
    df.columns = df.columns.str.lower().str.strip()
    required = {"id", "from", "to", "risk"}
    missing = required - set(df.columns)
    if missing:
        return False, f"Missing columns: {missing}. Your CSV needs: id, from, to, risk"
    df["from"] = df["from"].str.lower().str.strip()
    df["to"]   = df["to"].str.lower().str.strip()
    bad_from = set(df["from"]) - set(CITIES)
    bad_to   = set(df["to"])   - set(CITIES)
    if bad_from | bad_to:
        return False, f"Unknown cities: {bad_from | bad_to}. Valid: {set(CITIES.keys())}"
    return True, ""

# ── SESSION STATE INIT ─────────────────────────────────────────────────────────
if "df_base" not in st.session_state:
    st.session_state.df_base  = build_dataframe()
    st.session_state.optimized = False
    st.session_state.before_cost = 0.0
    st.session_state.after_cost  = 0.0

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ ChainGuard Controls")
    st.divider()

    uploaded = st.file_uploader("📁 Upload Shipment CSV", type=["csv"])
    if uploaded:
        try:
            raw = pd.read_csv(uploaded)
            ok, err = validate_upload(raw)
            if ok:
                st.session_state.df_base  = raw
                st.session_state.optimized = False
                st.success("✅ Data loaded!")
            else:
                st.error(err)
        except Exception as e:
            st.error(f"Parse error: {e}")

    if st.button("🔄 Reset to Demo Data"):
        st.session_state.df_base   = build_dataframe()
        st.session_state.optimized = False

    st.divider()
    status_filter = st.multiselect(
        "Filter by Status",
        ["CRITICAL", "AT RISK", "ON TRACK"],
        default=["CRITICAL", "AT RISK", "ON TRACK"]
    )
    auto_mode = st.toggle("Live Simulation (auto-refresh)", value=False)
    st.caption("Simulates real-time data updates every 3s")

    st.divider()
    st.markdown("**CSV Format:**")
    st.code("id,from,to,risk\nSHP-001,mumbai,delhi,72", language="text")
    st.caption(f"Valid cities: {', '.join(sorted(CITIES.keys()))}")

# ── AUTO REFRESH ───────────────────────────────────────────────────────────────
if auto_mode:
    if "last_update" not in st.session_state:
        st.session_state.last_update = time.time()

    if time.time() - st.session_state.last_update > 3:
        st.session_state.df_base = build_dataframe()
        st.session_state.optimized = False
        st.session_state.last_update = time.time()
        st.rerun()

# ── ENRICH DATA ────────────────────────────────────────────────────────────────
df = enrich(st.session_state.df_base)
df_view = df[df["status"].isin(status_filter)]

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.title("🚚 ChainGuard")
st.caption("AI-Powered Supply Chain Optimization · Powered by Google Gemini")
st.divider()

# ── KPI CARDS ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric(" Total Shipments", len(df_view))
k2.metric(" Critical",        int((df_view["risk"] >= 60).sum()))
k3.metric(" At Risk",         int(((df_view["risk"] >= 30) & (df_view["risk"] < 60)).sum()))
k4.metric(" Total Cost",      f"₹{df_view['cost'].sum():,.0f}")

st.divider()

# ── OPTIMIZATION PANEL ─────────────────────────────────────────────────────────
st.subheader("Smart Network Optimization")

before_cost = df["cost"].sum()
before_risk = df["risk"].mean()

col_btn, col_info = st.columns([1, 3])
with col_btn:
    optimize = st.button(" Optimize Network", type="primary", use_container_width=True)

with col_info:
    if not st.session_state.optimized:
        crit_count = int((df["risk"] >= 60).sum())
        st.info(f"**{crit_count} critical shipments** detected. Click Optimize to reroute them and reduce cost + risk.")

if optimize:
    df_opt = df.copy()
    for idx in df_opt.index:
        if df_opt.loc[idx, "risk"] >= 60:
            frm = df_opt.loc[idx, "from"]
            best_city, new_risk = find_best_reroute(frm, df_opt.loc[idx, "to"])
            df_opt.loc[idx, "to"]   = best_city
            df_opt.loc[idx, "risk"] = new_risk

    df_opt["delay"]  = (df_opt["risk"] // 8).astype(int)
    df_opt["eta"]    = df_opt["delay"] + 10
    df_opt["cost"]   = df_opt.apply(lambda r: route_cost(r["from"], r["to"]), axis=1)
    df_opt["status"] = np.where(df_opt["risk"] >= 60, "CRITICAL",
                       np.where(df_opt["risk"] >= 30, "AT RISK", "ON TRACK"))

    after_cost = df_opt["cost"].sum()
    after_risk = df_opt["risk"].mean()

    st.session_state.before_cost = before_cost
    st.session_state.after_cost  = after_cost
    st.session_state.df_base     = df_opt[["id", "from", "to", "risk"]]
    st.session_state.optimized   = True

    df     = enrich(st.session_state.df_base)
    df_view = df[df["status"].isin(status_filter)]

if st.session_state.optimized:
    saved_cost = st.session_state.before_cost - st.session_state.after_cost
    saved_risk = before_risk - df["risk"].mean()

    r1, r2 = st.columns(2)
    r1.success(f"💰 Cost Saved: **₹{saved_cost:,.0f}**")
    r2.success(f"📉 Avg Risk Reduced: **{saved_risk:.1f} points**")

    st.subheader("📊 Cost Impact Visualization")
    fig, ax = plt.subplots(figsize=(6, 3))
    bars = ax.bar(["Before Optimization", "After Optimization"],
                  [st.session_state.before_cost, st.session_state.after_cost])
    ax.bar_label(bars, fmt="₹{:,.0f}")
    st.pyplot(fig)
    plt.close(fig)

st.divider()

# ── MAP ───────────────────────────────────────────────────────────────────────
st.subheader("🌍 Network Flow Map")

lines=[]
for _,row in df_view.iterrows():
    f=CITIES[row["from"]]; t=CITIES[row["to"]]
    color=[255,75,75] if row["status"]=="CRITICAL" else [0,200,130]
    lines.append({"from":[f[1],f[0]],"to":[t[1],t[0]],"color":color})

st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(latitude=20,longitude=78,zoom=4),
    layers=[pdk.Layer("LineLayer",data=lines,
                      get_source_position="from",
                      get_target_position="to",
                      get_color="color",
                      get_width=3)]
))

st.subheader("📦 Shipment Insights")
st.dataframe(df_view)
