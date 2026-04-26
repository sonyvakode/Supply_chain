# 🛡️ ChainGuard AI

### AI-Powered Supply Chain Disruption Detection & Optimization

---

## 🚀 Overview

ChainGuard AI is a **decision-support prototype** designed to detect potential supply chain disruptions and provide **AI-driven recommendations** before delays escalate.

It simulates real-world logistics scenarios and helps users visualize shipment risks, analyze disruptions, and take proactive actions.

---

## 🎯 Problem Statement

Modern supply chains are highly complex and vulnerable to disruptions such as weather conditions, port congestion, and operational bottlenecks.

Most disruptions are identified **too late**, leading to delays, increased costs, and inefficiencies.

---

## 💡 Solution

ChainGuard AI provides:

* 📊 **Real-time risk analysis** of shipments
* 🗺️ **Visual shipment tracking (map-based)**
* 🚨 **Disruption alerts based on risk levels**
* 🤖 **AI-powered recommendations using Gemini API**
* 📈 **Demand forecasting for planning**

---

## ⚙️ Features

### 🔹 Dashboard

* Shipment KPIs (Total, Critical, Avg Delay)
* Interactive global shipment map
* Clean disruption alert table

### 🔹 AI Insights

* Generate actionable recommendations for high-risk shipments
* Uses **Google Gemini API**

### 🔹 Data Upload

* Upload custom CSV data
* System auto-handles missing fields

### 🔹 Forecasting

* Predicts future demand trends using machine learning

---

## 🧠 AI Integration

ChainGuard AI uses **Google Gemini API** to:

* Analyze shipment risks
* Provide decision-support recommendations
* Suggest mitigation strategies

---

## 📂 Input Format (CSV)

Users can upload their own data in this format:

```
id,from,to,risk,delay,eta
SHP-1,Mumbai,Delhi,65,5,20
SHP-2,Chennai,Bangalore,30,2,10
```

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

### 1. Install dependencies

```
pip install streamlit pandas numpy matplotlib scikit-learn pydeck google-generativeai
```

### 2. Add API Key

Create a file:

```
.streamlit/secrets.toml
```

Add:

```
GEMINI_API_KEY = "your_api_key_here"
```

---

### 3. Run the app

```
streamlit run app.py
```

---

## 📱 Prototype Highlights

* Mobile-friendly interface
* Dark mode UI
* Clean and minimal design
* Interactive and user-focused

---

## ⚠️ Limitations

* Uses simulated data (not real-time streaming)
* Routing optimization is AI-assisted (not fully algorithmic)
* Prototype-level scalability

---

## 🔮 Future Scope

* Real-time IoT/logistics data integration
* Advanced routing algorithms (graph optimization)
* Predictive ML models for disruption forecasting
* Deployment as a cloud-based SaaS platform

---

## 👥 Team

**Team Name:** Navdashi

* 👨‍💻 **Sony Vakode** — Team Leader
* 👩‍💻 **Meddipally Shruthi** — Team Member

---
