# 🛡️ ChainGuard AI

### AI-Powered Supply Chain Optimization & Risk Monitoring Dashboard

---

## 🚀 Overview

ChainGuard AI is an **interactive Streamlit-based working prototype and MVP** that monitors shipment risks, predicts disruptions, and provides optimized logistics decisions using AI.

It delivers a **real-time simulation dashboard** with:

* 📊 Risk scoring
* ⚡ Route optimization
* 🤖 AI-powered insights
* 📈 Demand forecasting

---

## 🔗 Project Links

* **Working Prototype (Code + Documentation):**
   (https://github.com/sonyvakode/Supply_chain)

* **MVP (Deployed Application):**
  https://smartsupplychain.streamlit.app/

* **Demo Video (3 Minutes):**
  https://youtube.com/smartflow-ai-demo

---

## 🎯 Problem Statement

Modern supply chains are highly vulnerable to disruptions such as:

* Port congestion
* Weather conditions
* Operational delays

Most systems are **reactive**, identifying issues only after disruptions occur, leading to:

* Increased logistics cost
* Delivery delays
* Inefficient decision-making

---

## 💡 Solution

ChainGuard AI enables **proactive supply chain management** by:

* 📊 Monitoring shipment risk scores (0–100)
* 🚨 Detecting critical shipments in real-time
* ⚡ Optimizing routes dynamically
* 🤖 Providing AI-driven recommendations using Gemini API
* 📈 Forecasting demand trends

---

## ⚙️ Key Features

### 🔹 Smart Dashboard

* KPI Cards:

  * Total Shipments
  * Critical Shipments
  * At Risk Shipments
  * Total Logistics Cost
* Clean and interactive UI

---

### 🔹 Live Simulation Mode

* Toggle-based auto-refresh system
* Updates data every 3 seconds
* Simulates real-time logistics environment

---

### 🔹 Network Flow Map

* Built using PyDeck
* Visualizes routes between cities
* Color-coded status:

  * 🔴 Critical
  * 🟡 At Risk
  * 🟢 On Track

---

### 🔹 Smart Optimization Engine

* Identifies high-risk shipments
* Suggests alternative routing strategies
* Reduces cost and risk

---

### 🔹 AI Insights (Gemini API)

* Generates actionable recommendations
* Analyzes:

  * Risk
  * Delay
  * Route
  * Cost

---

### 🔹 Shipment Insights Panel

* Displays:

  * Route
  * Status
  * Risk
  * ETA
* On-demand AI recommendations

---

### 🔹 Demand Forecasting

* Uses Linear Regression
* Predicts future shipment demand trends

---

### 🔹 Risk Distribution Analysis

* Histogram visualization
* Threshold markers:

  * AT RISK (30)
  * CRITICAL (60)

---

## 🧠 AI Integration

ChainGuard AI integrates with **Google Gemini API** to:

* Analyze shipment conditions
* Generate decision-support insights
* Recommend mitigation strategies

---

## 📂 Input Data Format

```csv id="csv1"
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
* **Visualization:** PyDeck, Matplotlib
* **ML Model:** Linear Regression

---

## ▶️ How to Run

### 1. Clone the Repository

```bash id="cmd1"
git clone https://github.com/sonyvakoode/Supply_chain.git
cd Supply_chain
```

---

### 2. Install Dependencies

```bash id="cmd2"
pip install streamlit pandas numpy matplotlib scikit-learn pydeck google-generativeai
```

---

### 3. Configure Gemini API Key

Create folder:

```
.streamlit
```

Inside it create file:

```
secrets.toml
```

Add:

```id="cmd3"
GEMINI_API_KEY = "your_api_key_here"
```

---

### 4. Run the Application

```bash id="cmd4"
streamlit run app.py
```

---

### 5. Open in Browser

```
http://localhost:8501/
```

---

### 6. Using the App

* View KPIs and dashboard
* Explore shipment routes on map
* Click **AI button** for insights
* Use **Optimize Network**
* Enable **Live Simulation Mode**

---

## 📊 Prototype Capabilities

✔ Real-time simulation dashboard
✔ AI-driven insights
✔ Interactive geospatial visualization
✔ Cost optimization engine
✔ Predictive analytics

---

## ⚠️ Limitations

* Uses simulated data (not real-time APIs)
* Depends on Gemini API quota availability
* Prototype-level scalability

---

## 🔮 Future Scope

* Integration with real logistics APIs
* Weather-based disruption prediction
* Advanced ML models (time-series, deep learning)
* Real-time GPS tracking
* Full SaaS deployment

---

## 👥 Team

**Team Name:** Navdashi

* 👨‍💻 Sony Vakode — Team Leader
* 👩‍💻 Meddipally Shruthi — Team Member

---
