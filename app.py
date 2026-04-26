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

st.set_page_config(page_title="ChainGuard", layout="wide", page_icon="ðŸšš")

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
    """Rich Gemini prompt with full shipment context."""
    if not GEMINI_OK:
        return (
            f"â€¢ Route {row['from'].title()} â†’ {row['to'].title()} carries a "
            f"{row['risk']}% risk score. Consider priority handling.\n"
            f"â€¢ Optimizing this route could save â‚¹{cost_saved:.0f} in logistics cost."
        )
    prompt = (
        f"You are a supply chain analyst. Analyze this shipment and give exactly 2 "
        f"short, specific, actionable business insights (bullet points).\n\n"
        f"Shipment ID: {row['id']}\n"
        f"Route: {row['from'].title()} â†’ {row['to'].title()}\n"
        f"Risk Score: {row['risk']}/100\n"
        f"Status: {row['status']}\n"
        f"Estimated Delay: {row['delay']} days\n"
        f"ETA: {row['eta']} days\n"
        f"Logistics Cost: â‚¹{row['cost']:.0f}\n"
        f"Network Cost Saved After Optimization: â‚¹{cost_saved:.0f}\n\n"
        f"Be specific about this route and risk level. No generic advice."
    )
    try:
        res = gemini.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"â€¢ AI temporarily unavailable: {e}"

# (rest of your code EXACTLY SAME — not touching anything)
