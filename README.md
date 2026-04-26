# 🛡️ ChainGuard AI

### AI-Powered Supply Chain Optimization & Risk Monitoring Dashboard

---

## 🚀 Overview

ChainGuard AI is an **interactive Streamlit-based prototype** that monitors shipment risks, predicts disruptions, and recommends optimized logistics decisions using AI.

It provides a **real-time simulation dashboard** with:

* Risk scoring
* Route optimization
* AI insights
* Demand forecasting

---

## 🎯 Problem Statement

Supply chains are highly vulnerable to disruptions such as:

* Port congestion
* Weather conditions
* Operational delays

Most systems are **reactive**, identifying issues only after delays occur, leading to:

* Increased logistics cost
* Missed delivery timelines
* Poor decision-making

---

## 💡 Solution

ChainGuard AI enables **proactive decision-making** by:

* 📊 Monitoring shipment risk scores (0–100)
* 🚨 Detecting critical shipments in real-time
* ⚡ Optimizing routes dynamically
* 🤖 Providing AI-driven insights using Gemini API
* 📈 Forecasting demand trends

---

## ⚙️ Key Features

### 🔹 1. Smart Dashboard

* KPI Cards:

  * Total Shipments
  * Critical Shipments
  * At Risk Shipments
  * Total Logistics Cost
* Clean and interactive UI

---

### 🔹 2. Live Simulation Mode

* Toggle-based **auto-refresh system**
* Updates shipment data every 3 seconds
* Simulates real-time logistics environment

---

### 🔹 3. Network Flow Map

* Built using **PyDeck**
* Visualizes routes between cities
* Color-coded status:

  * 🔴 Critical
  * 🟡 At Risk
  * 🟢 On Track

---

### 🔹 4. Smart Optimization Engine

* Detects high-risk shipments
* Suggests better rerouting options
* Reduces:

  * Cost
  * Risk

---

### 🔹 5. AI Insights (Gemini API)

* Generates actionable business insights
* Analyzes:

  * Risk level
  * Delay
  * Route
  * Cost

---

### 🔹 6. Shipment Insights Panel

* Displays shipment-level details:

  * Route
  * Status
  * Risk
  * ETA
* On-demand AI recommendations

---

### 🔹 7. Demand Forecasting

* Uses **Linear Regression**
* Predicts future shipment demand
* Displays:

  * Historical trend
  * Forecast curve
  * Confidence band

---

### 🔹 8. Risk Distribution Analysis

* Histogram visualization
* Threshold markers:

  * AT RISK (30)
  * CRITICAL (60)

---

## 🧠 AI Integration

ChainGuard uses **Google Gemini API** to:

* Analyze shipment conditions
* Generate decision-support insights
* Suggest optimization strategies

---

## 📂 Input Data Format

Upload CSV file with:

```csv
id,from,to,risk
SHP-001,mumbai,delhi,72
SHP-002,hyderabad,pune,45
```

✔ Automatically validates:

* Required columns
* Valid cities

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **AI:** Google Gemini API
* **Data Processing:** Pandas, NumPy
* **Visualization:**

  * PyDeck (Map)
  * Matplotlib (Charts)
* **ML Model:** Linear Regression

---

## ▶️ How to Run

### 1. Install Dependencies

```bash
pip install streamlit pandas numpy matplotlib scikit-learn pydeck google-generativeai
```

---

### 2. Add Gemini API Key

Create file:

```
.streamlit/secrets.toml
```

Add:

```
GEMINI_API_KEY = "your_api_key_here"
```

---

### 3. Run the App

```bash
streamlit run app.py
```

---

## 📊 Prototype Capabilities

✔ Real-time simulation dashboard
✔ AI-driven insights
✔ Interactive geospatial visualization
✔ Cost optimization engine
✔ Predictive analytics

---

## ⚠️ Limitations

* Uses **simulated data (not real-time APIs)**
* Risk scoring includes synthetic variation
* Route optimization is heuristic-based

---

## 🔮 Future Scope

* Integration with real logistics APIs
* Weather-based disruption prediction
* Advanced ML models (time series, deep learning)
* Real-time GPS shipment tracking
* SaaS deployment

---

## 👥 Team

**Team Name:** Navdashi

* 👨‍💻 **Sony Vakode** — Team Leader
* 👩‍💻 **Meddipally Shruthi** — Team Member

---
