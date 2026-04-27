"""
ChainGuard AI — Smart Supply Chain Optimizer
Clean, readable, hackathon-ready prototype
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.linear_model import LinearRegression
import random
from google import genai

# ── Gemini ──────────────────────────────────────────────────────────────
client = genai.Client(api_key="YOUR_GEMINI_API_KEY_HERE")

# ── Page config ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ChainGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Clean, readable CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Nunito+Sans:wght@300;400;600&display=swap');

/* Reset & base */
html, body, [class*="css"], .stApp { 
    font-family: 'Nunito Sans', sans-serif;
    background-color: #f8f9fc !important;
    color: #1a202c;
}
.block-container { padding: 2rem 2.5rem !important; max-width: 1200px; }

/* Top nav bar */
.topbar {
    background: #0f172a;
    border-radius: 16px;
    padding: 22px 32px;
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 28px;
}
.topbar-logo { font-size: 2rem; }
.topbar-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: #38bdf8;
    margin: 0;
    line-height: 1.2;
}
.topbar-sub { color: #94a3b8; font-size: 0.85rem; margin: 0; font-weight: 300; }

/* KPI strip */
.kpi-row { display: flex; gap: 16px; margin-bottom: 28px; }
.kpi-card {
    flex: 1;
    background: white;
    border-radius: 14px;
    padding: 22px 20px;
    text-align: center;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.kpi-num  { font-family: 'Syne', sans-serif; font-size: 2.2rem; font-weight: 800; line-height: 1; }
.kpi-lbl  { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1.2px; color: #64748b; margin-top: 6px; font-weight: 600; }
.kpi-blue  { color: #0ea5e9; }
.kpi-red   { color: #ef4444; }
.kpi-amber { color: #f59e0b; }
.kpi-green { color: #22c55e; }
.kpi-slate { color: #475569; }

/* Section title */
.sec-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0 0 14px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #e2e8f0;
}

/* Alert cards */
.alert-card {
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    border-left: 5px solid;
}
.alert-critical { background: #fff1f2; border-color: #ef4444; }
.alert-warning  { background: #fffbeb; border-color: #f59e0b; }
.alert-ok       { background: #f0fdf4; border-color: #22c55e; }

.alert-head { font-weight: 700; font-size: 0.95rem; color: #0f172a; margin-bottom: 4px; }
.alert-body { font-size: 0.83rem; color: #475569; line-height: 1.6; }
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
    margin-left: 8px;
    vertical-align: middle;
}
.badge-red   { background: #fee2e2; color: #dc2626; }
.badge-amber { background: #fef3c7; color: #d97706; }
.badge-green { background: #dcfce7; color: #16a34a; }

/* Route card */
.route-card {
    background: white;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.route-head { font-weight: 700; font-size: 0.95rem; color: #0f172a; margin-bottom: 6px; }
.route-meta { font-size: 0.82rem; color: #64748b; line-height: 1.7; }
.route-highlight { color: #0ea5e9; font-weight: 600; }
.route-warn      { color: #ef4444; font-weight: 600; }

/* Gemini response box */
.gemini-box {
    background: #0f172a;
    border-radius: 14px;
    padding: 22px 26px;
    color: #e2e8f0;
    font-size: 0.88rem;
    line-height: 1.8;
    white-space: pre-wrap;
    border-left: 4px solid #38bdf8;
    margin-top: 12px;
}

/* Sidebar cleanup */
[data-testid="stSidebar"] {
    background: #0f172a !important;
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] h3 { color: #38bdf8 !important; font-family: 'Syne', sans-serif; }
[data-testid="stSidebar"] .stSlider > div > div > div { background: #38bdf8 !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  DATA SIMULATION
# ════════════════════════════════════════════════════════════

ROUTES = [
    {"id":"R001","from":"Shanghai",  "to":"Rotterdam",   "mode":"Sea", "days":32,"cost":4200, "wp":["Suez Canal","Med Sea"]},
    {"id":"R002","from":"Shanghai",  "to":"Los Angeles", "mode":"Sea", "days":14,"cost":2800, "wp":["Pacific"]},
    {"id":"R003","from":"Mumbai",    "to":"Hamburg",     "mode":"Sea", "days":22,"cost":3500, "wp":["Suez Canal"]},
    {"id":"R004","from":"Singapore", "to":"Felixstowe",  "mode":"Sea", "days":28,"cost":3900, "wp":["Cape Horn"]},
    {"id":"R005","from":"Shenzhen",  "to":"Long Beach",  "mode":"Sea", "days":16,"cost":3100, "wp":["Pacific"]},
    {"id":"R006","from":"Hong Kong", "to":"Jeddah",      "mode":"Sea", "days":18,"cost":2600, "wp":["Malacca","Red Sea"]},
    {"id":"R007","from":"Busan",     "to":"Vancouver",   "mode":"Sea", "days":11,"cost":2200, "wp":["N. Pacific"]},
    {"id":"R008","from":"Chennai",   "to":"Antwerp",     "mode":"Sea", "days":25,"cost":3700, "wp":["Suez Canal"]},
]

DISRUPTIONS = [
    {"name":"Port Congestion",   "icon":"⚓","sev":"critical","delay":(5,15)},
    {"name":"Severe Weather",    "icon":"🌪️","sev":"critical","delay":(3,10)},
    {"name":"Canal Blockage",    "icon":"🚧","sev":"critical","delay":(7,21)},
    {"name":"Customs Delay",     "icon":"🛃","sev":"warning", "delay":(1,5)},
    {"name":"Labor Strike",      "icon":"✊","sev":"warning", "delay":(2,8)},
    {"name":"Equipment Failure", "icon":"⚙️","sev":"warning", "delay":(1,4)},
]

ALTS = {
    "Sea":[
        {"name":"✈️  Air Freight (Express)",     "cost_pct":+280,"days_saved":20,"rel":96},
        {"name":"🚂  Trans-Siberian Rail",        "cost_pct":+60, "days_saved":8, "rel":78},
        {"name":"🚢  Cape of Good Hope Bypass",   "cost_pct":+15, "days_saved":-4,"rel":88},
    ],
}

@st.cache_data
def sim_shipments(n, seed=42):
    random.seed(seed); np.random.seed(seed)
    rows = []
    for i in range(n):
        r   = random.choice(ROUTES)
        dis = random.sample(DISRUPTIONS, k=random.randint(0,3))
        delay = sum(random.randint(*d["delay"]) for d in dis)
        risk  = min(100, sum({"critical":40,"warning":20}[d["sev"]] for d in dis) + random.randint(0,20))
        rows.append({
            "id":       f"SHP-{1000+i}",
            "route":    r["id"],
            "frm":      r["from"],
            "to":       r["to"],
            "mode":     r["mode"],
            "cargo":    random.choice(["Electronics","Auto Parts","Textiles","Pharma","FMCG","Machinery"]),
            "base":     r["days"],
            "delay":    delay,
            "eta":      r["days"]+delay,
            "cost":     r["cost"],
            "risk":     risk,
            "dis":      dis,
            "wp":       r["wp"],
            "status":   "CRITICAL" if risk>=60 else ("AT RISK" if risk>=30 else "ON TRACK"),
        })
    return rows

@st.cache_data
def sim_demand(days=30):
    np.random.seed(7)
    x = np.arange(1, days+1)
    y = 200 + x*4.5 + np.random.normal(0,25,days)
    return pd.DataFrame({"Day":x,"Sales":np.clip(y,80,None).astype(int)})


# ════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🛡️ ChainGuard AI")
    st.markdown("---")
    st.markdown("**Fleet Settings**")
    n_ships   = st.slider("Active shipments",    4, 20, 12)
    threshold = st.slider("Risk alert threshold",20, 80, 50)
    show_all  = st.checkbox("Show all shipments", False)
    st.markdown("---")
    st.markdown("**Demand Forecast**")
    horizon   = st.slider("Forecast horizon (days)", 7, 30, 14)
    csv_file  = st.file_uploader("Upload your sales CSV", type=["csv"])
    st.markdown("---")
    st.caption("Build with AI 🚀 · GDG · Powered by Gemini")


# ════════════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="topbar">
  <div class="topbar-logo">🛡️</div>
  <div>
    <p class="topbar-title">ChainGuard AI</p>
    <p class="topbar-sub">Resilient Logistics &amp; Dynamic Supply Chain Optimization · Disruption detection powered by Gemini</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  KPI STRIP
# ════════════════════════════════════════════════════════════
ships   = sim_shipments(n_ships)
df      = pd.DataFrame(ships)
n_crit  = sum(1 for s in ships if s["status"]=="CRITICAL")
n_risk  = sum(1 for s in ships if s["status"]=="AT RISK")
n_ok    = sum(1 for s in ships if s["status"]=="ON TRACK")
avg_dly = df["delay"].mean()

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-num kpi-blue">{n_ships}</div>
    <div class="kpi-lbl">Active Shipments</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-num kpi-red">{n_crit}</div>
    <div class="kpi-lbl">Critical</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-num kpi-amber">{n_risk}</div>
    <div class="kpi-lbl">At Risk</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-num kpi-green">{n_ok}</div>
    <div class="kpi-lbl">On Track</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-num kpi-{"red" if avg_dly>6 else "amber" if avg_dly>3 else "green"}">{avg_dly:.1f}d</div>
    <div class="kpi-lbl">Avg Delay</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  TABS
# ════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "🚨  Disruption Alerts",
    "🗺️  Route Optimizer",
    "📈  Demand Forecast",
])


# ──────────────────────────────────────────────────────────
#  TAB 1 — DISRUPTION ALERTS
# ──────────────────────────────────────────────────────────
with tab1:
    left, right = st.columns([1.1, 1], gap="large")

    # ── Alert list ──
    with left:
        st.markdown('<p class="sec-title">Flagged Shipments</p>', unsafe_allow_html=True)

        flagged = [s for s in ships if s["risk"] >= threshold]
        if show_all:
            flagged = ships
        flagged = sorted(flagged, key=lambda x: -x["risk"])

        if not flagged:
            st.markdown('<div class="alert-card alert-ok"><div class="alert-head">✅ All shipments are within the safe threshold</div><div class="alert-body">Try lowering the alert threshold in the sidebar.</div></div>', unsafe_allow_html=True)
        else:
            for s in flagged:
                css   = "alert-critical" if s["status"]=="CRITICAL" else "alert-warning"
                badge = f'<span class="badge badge-red">CRITICAL</span>' if s["status"]=="CRITICAL" else f'<span class="badge badge-amber">AT RISK</span>'
                dnames = " · ".join(f"{d['icon']} {d['name']}" for d in s["dis"]) or "No disruptions flagged"
                st.markdown(f"""
                <div class="alert-card {css}">
                  <div class="alert-head">
                    {s['id']} — {s['frm']} → {s['to']} ({s['mode']}) {badge}
                  </div>
                  <div class="alert-body">
                    📦 <b>{s['cargo']}</b> &nbsp;|&nbsp;
                    ⏱ ETA <b>{s['eta']}d</b> (base {s['base']}d + <b>+{s['delay']}d delay</b>) &nbsp;|&nbsp;
                    ⚠️ Risk <b>{s['risk']}/100</b><br>
                    🔍 {dnames}
                  </div>
                </div>""", unsafe_allow_html=True)

    # ── Charts ──
    with right:
        st.markdown('<p class="sec-title">Risk Distribution</p>', unsafe_allow_html=True)

        # --- Risk bar chart ---
        fig, axes = plt.subplots(1, 2, figsize=(8, 3.2))
        fig.patch.set_facecolor("white")

        # bar: risk per shipment
        ax1 = axes[0]
        ax1.set_facecolor("#f8f9fc")
        colors = ["#ef4444" if s["risk"]>=60 else "#f59e0b" if s["risk"]>=30 else "#22c55e" for s in ships]
        ax1.bar([s["id"].replace("SHP-","") for s in ships], [s["risk"] for s in ships],
                color=colors, width=0.6, edgecolor="white", linewidth=0.5)
        ax1.axhline(threshold, color="#0ea5e9", linestyle="--", linewidth=1.2, label=f"Threshold ({threshold})")
        ax1.set_xlabel("Shipment #", fontsize=8, color="#475569")
        ax1.set_ylabel("Risk Score",  fontsize=8, color="#475569")
        ax1.tick_params(colors="#64748b", labelsize=7)
        ax1.legend(fontsize=7, framealpha=0.9)
        for sp in ax1.spines.values(): sp.set_color("#e2e8f0")
        ax1.set_title("Risk Scores by Shipment", fontsize=9, color="#0f172a", pad=8)

        # pie: status mix
        ax2 = axes[1]
        ax2.set_facecolor("#f8f9fc")
        slices = [(n_crit,"Critical","#ef4444"), (n_risk,"At Risk","#f59e0b"), (n_ok,"On Track","#22c55e")]
        slices = [(v,l,c) for v,l,c in slices if v>0]
        vals,lbls,clrs = zip(*slices)
        wedges, texts, auto = ax2.pie(vals, labels=lbls, colors=clrs, autopct="%1.0f%%",
                                       startangle=90, pctdistance=0.78,
                                       textprops={"fontsize":8,"color":"#0f172a"})
        for a in auto: a.set_fontsize(7)
        ax2.set_title("Fleet Status", fontsize=9, color="#0f172a", pad=8)

        plt.tight_layout(pad=1.8)
        st.pyplot(fig, use_container_width=True)
        plt.close()

        # --- Delay by disruption type ---
        st.markdown('<p class="sec-title" style="margin-top:20px">Average Delay by Disruption Type</p>', unsafe_allow_html=True)
        dtype_d = {}
        for s in ships:
            for d in s["dis"]:
                dtype_d.setdefault(d["name"],[]).append(s["delay"])
        if dtype_d:
            names = list(dtype_d.keys())
            avgs  = [np.mean(v) for v in dtype_d.values()]
            order = np.argsort(avgs)[::-1]
            fig2, ax = plt.subplots(figsize=(7, max(2.2, len(names)*0.5)))
            fig2.patch.set_facecolor("white")
            ax.set_facecolor("#f8f9fc")
            ax.barh([names[i] for i in order], [avgs[i] for i in order],
                    color="#0ea5e9", edgecolor="white", height=0.55)
            ax.tick_params(colors="#64748b", labelsize=8)
            ax.set_xlabel("Avg delay (days)", fontsize=8, color="#475569")
            for sp in ax.spines.values(): sp.set_color("#e2e8f0")
            plt.tight_layout()
            st.pyplot(fig2, use_container_width=True)
            plt.close()

    # ── Gemini disruption plan ──
    st.markdown("---")
    st.markdown('<p class="sec-title">🤖 AI Disruption Response Plan</p>', unsafe_allow_html=True)
    crit_ships = [s for s in ships if s["status"]=="CRITICAL"]

    if st.button("✨ Generate Response Plan with Gemini", key="b1", type="primary"):
        if not crit_ships:
            st.info("No critical shipments. Lower the threshold to generate a plan.")
        else:
            lines = []
            for s in crit_ships:
                dnames = ", ".join(f"{d['icon']} {d['name']} ({d['sev']})" for d in s["dis"])
                lines.append(f"- {s['id']}: {s['frm']}→{s['to']} | Cargo: {s['cargo']} | Delay: +{s['delay']}d | Risk: {s['risk']}/100 | Issues: {dnames or 'Unknown'}")

            prompt = f"""You are a senior supply chain risk analyst.

CRITICAL SHIPMENTS REQUIRING IMMEDIATE ACTION:
{chr(10).join(lines)}

For EACH shipment provide exactly:
1. Root cause (1 sentence)
2. Immediate action (specific and actionable)
3. Rerouting recommendation (mode/path)
4. Estimated cost impact

Format clearly. Be decisive and concise."""

            with st.spinner("Gemini is analyzing..."):
                try:
                    r = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                    st.markdown(f'<div class="gemini-box">{r.text}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Gemini error: {e}")


# ──────────────────────────────────────────────────────────
#  TAB 2 — ROUTE OPTIMIZER
# ──────────────────────────────────────────────────────────
with tab2:
    st.markdown('<p class="sec-title">Dynamic Route Optimizer</p>', unsafe_allow_html=True)

    at_risk_ids = [s["id"] for s in ships if s["status"] in ("CRITICAL","AT RISK")]
    if not at_risk_ids:
        st.info("No disrupted shipments. Lower the alert threshold to see options.")
    else:
        sel_id  = st.selectbox("Select a disrupted shipment to optimize", at_risk_ids)
        sel     = next(s for s in ships if s["id"]==sel_id)
        alts    = ALTS.get(sel["mode"], ALTS["Sea"])

        c1, c2 = st.columns([1, 1.2], gap="large")

        with c1:
            st.markdown('<p class="sec-title">Current Route (Disrupted)</p>', unsafe_allow_html=True)
            dnames = " · ".join(f"{d['icon']} {d['name']}" for d in sel["dis"]) or "None"
            st.markdown(f"""
            <div class="route-card">
              <div class="route-head">🔴 {sel['id']} — {sel['frm']} → {sel['to']}</div>
              <div class="route-meta">
                Mode: <b>{sel['mode']}</b> &nbsp;|&nbsp; Cargo: <b>{sel['cargo']}</b><br>
                Base ETA: {sel['base']}d &nbsp;→&nbsp; <span class="route-warn">Current ETA: {sel['eta']}d (+{sel['delay']}d delay)</span><br>
                Cost: <b>${sel['cost']:,}</b> &nbsp;|&nbsp; Risk Score: <span class="route-warn">{sel['risk']}/100</span><br>
                Via: {' → '.join(sel['wp'])}<br>
                Disruptions: {dnames}
              </div>
            </div>""", unsafe_allow_html=True)

            st.markdown('<p class="sec-title" style="margin-top:20px">Alternate Routes</p>', unsafe_allow_html=True)
            for alt in alts:
                new_cost = int(sel["cost"] * (1 + alt["cost_pct"]/100))
                new_eta  = max(1, sel["eta"] - alt["days_saved"])
                delta_c  = new_cost - sel["cost"]
                sign_c   = "+" if delta_c >= 0 else ""
                time_txt = f"-{alt['days_saved']}d faster" if alt["days_saved"]>0 else f"+{abs(alt['days_saved'])}d slower"
                rel_col  = "#22c55e" if alt["rel"]>=90 else "#f59e0b"
                st.markdown(f"""
                <div class="route-card">
                  <div class="route-head">🔀 {alt['name']}</div>
                  <div class="route-meta">
                    New ETA: <span class="route-highlight">{new_eta}d</span> ({time_txt})<br>
                    New Cost: <b>${new_cost:,}</b> ({sign_c}${delta_c:,})<br>
                    Reliability: <b style="color:{rel_col}">{alt['rel']}%</b>
                  </div>
                </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown('<p class="sec-title">Route Comparison</p>', unsafe_allow_html=True)

            route_labels = ["Current\n(disrupted)"] + [a["name"].split("  ")[1] for a in alts]
            etas  = [sel["eta"]]  + [max(1, sel["eta"]  - a["days_saved"]) for a in alts]
            costs = [sel["cost"]] + [int(sel["cost"] * (1 + a["cost_pct"]/100)) for a in alts]
            rels  = [max(0, 100-sel["risk"])] + [a["rel"] for a in alts]
            bar_c = ["#ef4444"] + ["#0ea5e9"]*len(alts)

            fig3, (ax_e, ax_c) = plt.subplots(2, 1, figsize=(7, 5), facecolor="white")

            for ax, vals, ylabel, title in [
                (ax_e, etas,  "Days",     "ETA Comparison (days)"),
                (ax_c, costs, "Cost ($)", "Cost Comparison ($)"),
            ]:
                ax.set_facecolor("#f8f9fc")
                bars = ax.bar(route_labels, vals, color=bar_c, width=0.5, edgecolor="white", linewidth=0.5)
                ax.set_ylabel(ylabel, fontsize=8, color="#475569")
                ax.set_title(title, fontsize=9, color="#0f172a", pad=6)
                ax.tick_params(colors="#64748b", labelsize=7.5)
                for sp in ax.spines.values(): sp.set_color("#e2e8f0")
                for bar, val in zip(bars, vals):
                    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*0.5,
                            f"{val:,}", ha="center", va="center",
                            color="white", fontsize=8, fontweight="bold")

            plt.tight_layout(pad=2)
            st.pyplot(fig3, use_container_width=True)
            plt.close()

        # Gemini rerouting
        st.markdown("---")
        st.markdown('<p class="sec-title">🤖 AI Rerouting Recommendation</p>', unsafe_allow_html=True)
        if st.button("✨ Get Gemini Rerouting Advice", key="b2", type="primary"):
            alts_txt = "\n".join([
                f"  • {a['name']}: ETA {max(1,sel['eta']-a['days_saved'])}d, "
                f"Cost ${int(sel['cost']*(1+a['cost_pct']/100)):,}, Reliability {a['rel']}%"
                for a in alts
            ])
            dnames = ", ".join(f"{d['name']} ({d['sev']})" for d in sel["dis"])
            prompt = f"""You are a logistics consultant. A shipment needs rerouting.

DISRUPTED SHIPMENT:
- {sel['id']}: {sel['frm']} → {sel['to']} via {sel['mode']}
- Cargo: {sel['cargo']} | ETA: {sel['eta']}d | Delay: +{sel['delay']}d
- Risk: {sel['risk']}/100 | Disruptions: {dnames or 'Unknown'}

AVAILABLE ALTERNATIVES:
{alts_txt}

Provide:
1. RECOMMENDED route (pick one, explain why)
2. Step-by-step transition (3–4 steps)
3. Key risks of your recommendation
4. Expected outcome vs staying on current route

Be decisive and concise."""

            with st.spinner("Gemini is optimizing your route..."):
                try:
                    r = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                    st.markdown(f'<div class="gemini-box">{r.text}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Gemini error: {e}")


# ──────────────────────────────────────────────────────────
#  TAB 3 — DEMAND FORECAST
# ──────────────────────────────────────────────────────────
with tab3:
    st.markdown('<p class="sec-title">Demand Forecasting & Inventory Planning</p>', unsafe_allow_html=True)

    # Load data
    if csv_file:
        try:
            raw = pd.read_csv(csv_file)
            if "Day" not in raw.columns or "Sales" not in raw.columns:
                st.warning("CSV must have 'Day' and 'Sales' columns. Using simulated data.")
                data = sim_demand()
            else:
                data = raw
        except:
            st.error("Invalid CSV. Using simulated data.")
            data = sim_demand()
    else:
        data = sim_demand()
        st.info("ℹ️ Using simulated sales data. Upload your CSV in the sidebar for real data.")

    # Model
    X = data[["Day"]]; y = data["Sales"]
    mdl = LinearRegression(); mdl.fit(X, y)
    fut  = pd.DataFrame({"Day": range(int(data["Day"].max())+1, int(data["Day"].max())+horizon+1)})
    pred = mdl.predict(fut)

    avg_pred   = round(pred.mean(), 1)
    peak_pred  = round(pred.max(), 1)
    growth_pct = round(((pred[-1] - data["Sales"].mean()) / data["Sales"].mean())*100, 1)
    reorder    = int(avg_pred * 1.3)

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    for col, val, lbl, color in [
        (k1, avg_pred,         "Avg Forecast (units/day)", "kpi-blue"),
        (k2, peak_pred,        "Peak Forecast",             "kpi-amber"),
        (k3, f"+{growth_pct}%","Demand Growth",             "kpi-green"),
        (k4, reorder,          "Reorder Point (×1.3 buffer)","kpi-blue"),
    ]:
        with col:
            st.markdown(f"""<div class="kpi-card">
                <div class="kpi-num {color}">{val}</div>
                <div class="kpi-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Chart — full width, large, clean
    fig4, ax = plt.subplots(figsize=(11, 4), facecolor="white")
    ax.set_facecolor("#f8f9fc")

    ax.plot(data["Day"], data["Sales"],
            color="#0ea5e9", lw=2.2, marker="o", ms=4, label="Actual Sales", zorder=3)
    ax.fill_between(data["Day"], data["Sales"], alpha=0.08, color="#0ea5e9")

    ax.plot(fut["Day"], pred,
            color="#f59e0b", lw=2.2, ls="--", marker="s", ms=3.5, label=f"Forecast (+{horizon}d)", zorder=3)
    ax.fill_between(fut["Day"], pred*0.9, pred*1.1, alpha=0.12, color="#f59e0b", label="±10% band")

    ax.axvline(data["Day"].max(), color="#cbd5e1", ls=":", lw=1.2)
    ax.text(data["Day"].max()+0.4, ax.get_ylim()[0]+10, "→ Forecast zone",
            color="#94a3b8", fontsize=8.5)

    ax.set_xlabel("Day", fontsize=9, color="#475569")
    ax.set_ylabel("Units", fontsize=9, color="#475569")
    ax.tick_params(colors="#64748b", labelsize=8.5)
    ax.legend(fontsize=8.5, framealpha=0.95, edgecolor="#e2e8f0")
    for sp in ax.spines.values(): sp.set_color("#e2e8f0")
    ax.set_title("Sales Trend & Demand Forecast", fontsize=11, color="#0f172a", pad=12, fontweight="bold")

    plt.tight_layout()
    st.pyplot(fig4, use_container_width=True)
    plt.close()

    # Gemini inventory advice
    st.markdown("---")
    st.markdown('<p class="sec-title">🤖 AI Inventory & Procurement Plan</p>', unsafe_allow_html=True)
    if st.button("✨ Generate Inventory Plan with Gemini", key="b3", type="primary"):
        prompt = f"""You are a supply chain inventory planner.

FORECAST DATA:
- Horizon: {horizon} days
- Average daily demand (forecast): {avg_pred} units
- Peak demand forecast: {peak_pred} units
- Demand growth vs historical: +{growth_pct}%
- Recommended reorder point (30% buffer): {reorder} units/day
- Fleet context: {n_crit} critical disruptions, {n_risk} at-risk shipments active

Provide:
1. Stocking strategy (how many units to hold and why)
2. Procurement timing (when to order, lead time buffer)
3. Supplier diversification advice given active disruptions
4. One specific cost optimization tip

Short, specific, professional."""

        with st.spinner("Gemini is generating your inventory plan..."):
            try:
                r = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                st.markdown(f'<div class="gemini-box">{r.text}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Gemini error: {e}")


# ── Footer ───────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("ChainGuard AI · Built for Build with AI 🚀 · GDG · Powered by Gemini 2.5 Flash · Streamlit · Scikit-learn")
