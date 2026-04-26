"""
Update SmartFlowAI PPT - fix text alignment, update live URL, add flowcharts.
Works by editing the unpacked XML directly, preserving all template design.
"""
import re, os

BASE = "/home/claude/unpacked2/ppt/slides/"

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def read(n): return open(f"{BASE}slide{n}.xml", encoding="utf-8").read()
def write(n, txt): open(f"{BASE}slide{n}.xml", "w", encoding="utf-8").write(txt)

def replace_text(xml, old, new):
    return xml.replace(f"<a:t>{old}</a:t>", f"<a:t>{new}</a:t>")

# Build a bullet paragraph using the template's exact font/spacing pattern
def bullet_para(text, sz="1450", color="000000", bold="0", indent=True):
    if indent:
        ppr = f'''<a:pPr lvl="0" marL="457200" indent="-228600" marR="0" rtl="0" algn="l">
              <a:lnSpc><a:spcPct val="115000"/></a:lnSpc>
              <a:spcBef><a:spcPts val="0"/></a:spcBef>
              <a:spcAft><a:spcPts val="150"/></a:spcAft>
              <a:buSzPts val="{sz}"/>
              <a:buFont typeface="Arial"/>
              <a:buChar char="&#x2022;"/>
            </a:pPr>'''
    else:
        ppr = f'''<a:pPr lvl="0" marL="0" marR="0" rtl="0" algn="l">
              <a:lnSpc><a:spcPct val="115000"/></a:lnSpc>
              <a:spcBef><a:spcPts val="0"/></a:spcBef>
              <a:spcAft><a:spcPts val="150"/></a:spcAft>
              <a:buSzPts val="{sz}"/>
              <a:buNone/>
            </a:pPr>'''
    return f'''          <a:p>
            {ppr}
            <a:r>
              <a:rPr b="{bold}" i="0" lang="en-GB" sz="{sz}" u="none" cap="none" strike="noStrike">
                <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
                <a:latin typeface="Google Sans"/>
                <a:ea typeface="Google Sans"/>
                <a:cs typeface="Google Sans"/>
                <a:sym typeface="Google Sans"/>
              </a:rPr>
              <a:t>{text}</a:t>
            </a:r>
            <a:endParaRPr b="{bold}" i="0" sz="{sz}" u="none" cap="none" strike="noStrike">
              <a:solidFill><a:srgbClr val="000000"/></a:solidFill>
              <a:latin typeface="Google Sans"/>
            </a:endParaRPr>
          </a:p>'''

def spacer(sz="300"):
    return f'''          <a:p>
            <a:pPr><a:lnSpc><a:spcPct val="100000"/></a:lnSpc>
              <a:spcBef><a:spcPts val="0"/></a:spcBef>
              <a:spcAft><a:spcPts val="0"/></a:spcAft>
              <a:buNone/>
            </a:pPr>
            <a:r><a:rPr b="0" sz="{sz}" strike="noStrike">
              <a:solidFill><a:srgbClr val="000000"/></a:solidFill>
              </a:rPr><a:t/></a:r>
          </a:p>'''

def heading_para(text, sz="2200", color="1A73E8"):
    return f'''          <a:p>
            <a:pPr lvl="0" marL="0" marR="0" rtl="0" algn="l">
              <a:lnSpc><a:spcPct val="115000"/></a:lnSpc>
              <a:spcBef><a:spcPts val="0"/></a:spcBef>
              <a:spcAft><a:spcPts val="150"/></a:spcAft>
              <a:buSzPts val="{sz}"/><a:buNone/>
            </a:pPr>
            <a:r>
              <a:rPr b="1" i="0" lang="en-GB" sz="{sz}" u="none" cap="none" strike="noStrike">
                <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
                <a:latin typeface="Google Sans"/>
                <a:ea typeface="Google Sans"/>
                <a:cs typeface="Google Sans"/>
                <a:sym typeface="Google Sans"/>
              </a:rPr>
              <a:t>{text}</a:t>
            </a:r>
            <a:endParaRPr b="1" i="0" sz="{sz}" u="none" cap="none" strike="noStrike">
              <a:solidFill><a:srgbClr val="000000"/></a:solidFill>
              <a:latin typeface="Google Sans"/>
            </a:endParaRPr>
          </a:p>'''

def build_txbody(paras_xml):
    return f'''        <p:txBody>
          <a:bodyPr anchorCtr="0" anchor="t" bIns="91425" lIns="91425" spcFirstLastPara="1" rIns="91425" wrap="square" tIns="91425">
            <a:normAutofit/>
          </a:bodyPr>
          <a:lstStyle/>
{paras_xml}
        </p:txBody>'''

# Shape XML for flowchart boxes
def rect_shape(id_, x, y, w, h, fill, text, sz="1100", text_color="FFFFFF", bold="1", border_color=None):
    bc = border_color or fill
    return f'''      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="{id_}" name="FlowBox{id_}"/>
          <p:cNvSpPr txBox="0"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
          <a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 20000"/></a:avLst></a:prstGeom>
          <a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>
          <a:ln w="19050"><a:solidFill><a:srgbClr val="{bc}"/></a:solidFill></a:ln>
        </p:spPr>
        <p:txBody>
          <a:bodyPr anchor="ctr" wrap="square" lIns="91425" rIns="91425" tIns="45720" bIns="45720"/>
          <a:lstStyle/>
          <a:p>
            <a:pPr algn="ctr"><a:buNone/></a:pPr>
            <a:r>
              <a:rPr b="{bold}" sz="{sz}" lang="en-GB" dirty="0">
                <a:solidFill><a:srgbClr val="{text_color}"/></a:solidFill>
                <a:latin typeface="Google Sans"/>
              </a:rPr>
              <a:t>{text}</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>'''

def arrow_shape(id_, x, y, w, h, vertical=False):
    if vertical:
        prst = "downArrow"
    else:
        prst = "rightArrow"
    return f'''      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="{id_}" name="Arrow{id_}"/>
          <p:cNvSpPr/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
          <a:prstGeom prst="{prst}"><a:avLst/></a:prstGeom>
          <a:solidFill><a:srgbClr val="1A73E8"/></a:solidFill>
          <a:ln><a:noFill/></a:ln>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/><a:lstStyle/>
          <a:p><a:endParaRPr/></a:p>
        </p:txBody>
      </p:sp>'''

def label_shape(id_, x, y, w, h, text, sz="900", color="444444", bold="0"):
    return f'''      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="{id_}" name="Label{id_}"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/><a:ln><a:noFill/></a:ln>
        </p:spPr>
        <p:txBody>
          <a:bodyPr anchor="ctr" wrap="square" lIns="45720" rIns="45720" tIns="45720" bIns="45720"/>
          <a:lstStyle/>
          <a:p>
            <a:pPr algn="ctr"><a:buNone/></a:pPr>
            <a:r>
              <a:rPr b="{bold}" sz="{sz}" lang="en-GB">
                <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
                <a:latin typeface="Google Sans"/>
              </a:rPr>
              <a:t>{text}</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>'''

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3 — Brief About Our Solution (fix spacing, update to match live app)
# ─────────────────────────────────────────────────────────────────────────────
xml3 = read(3)
paras = "\n".join([
    heading_para("Brief About Our Solution"),
    spacer("400"),
    bullet_para("SmartFlow AI is an AI-powered supply chain optimization platform that predicts disruptions, detects logistics risks in real time, and recommends optimized alternate routes — preventing costly delays before they happen.", sz="1500", indent=False),
    spacer("300"),
    bullet_para("Key capabilities:", sz="1500", bold="1", indent=False),
    bullet_para("Continuous disruption monitoring — every active shipment scored 0–100 for risk using ML models"),
    bullet_para("Preemptive flagging — port congestion, severe weather, canal blockages, and labor strikes"),
    bullet_para("Dynamic route optimization powered by Gemini 2.5 Flash with cost and ETA tradeoff analysis"),
    bullet_para("Demand forecasting — Linear Regression model with configurable horizon and confidence bands"),
    spacer("300"),
    bullet_para("Live at: https://smartsupplychain.streamlit.app/", sz="1350", color="1A73E8", indent=False),
])
new_txbody = build_txbody(paras)
# Replace the entire txBody of the main text shape
xml3 = re.sub(r'(<p:txBody>.*?</p:txBody>)', new_txbody, xml3, count=1, flags=re.DOTALL)
write(3, xml3)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4 — Opportunities & USP (fix spacing)
# ─────────────────────────────────────────────────────────────────────────────
xml4 = read(4)
paras = "\n".join([
    heading_para("Opportunities"),
    spacer("300"),
    bullet_para("Most logistics systems are reactive — delays, penalties, and failures are detected only after they occur.", sz="1450", indent=False),
    bullet_para("SmartFlow AI is proactive:", sz="1450", bold="1", indent=False),
    bullet_para("Predicts disruptions before they happen using scikit-learn ML risk scoring (0–100 per shipment)"),
    bullet_para("Detects risky shipments in advance with real-time severity classification (Critical / At Risk / On Track)"),
    bullet_para("Suggests optimized alternate routes instantly with cost + ETA tradeoff analysis"),
    bullet_para("Reduces cascading supply chain failures through early AI-driven intervention"),
    spacer("300"),
    bullet_para("USP of the Proposed Solution", sz="1500", bold="1", color="1A73E8", indent=False),
    bullet_para("AI-powered disruption prediction using scikit-learn ML — not rule-based, learns from data"),
    bullet_para("Real-time route optimization with Gemini 2.5 Flash — compares air, sea, rail alternatives"),
    bullet_para("Zero-infrastructure cloud dashboard — accessible from any browser, deployed on Streamlit Cloud"),
    bullet_para("Faster decisions — on-demand Gemini AI response plans with root cause + immediate action steps"),
    bullet_para("Scalable architecture for global logistics handling millions of shipments daily"),
])
new_txbody = build_txbody(paras)
xml4 = re.sub(r'(<p:txBody>.*?</p:txBody>)', new_txbody, xml4, count=1, flags=re.DOTALL)
write(4, xml4)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5 — Features (fix spacing, tighten wording)
# ─────────────────────────────────────────────────────────────────────────────
xml5 = read(5)
paras = "\n".join([
    heading_para("Features Offered by the Solution"),
    spacer("300"),
    bullet_para("Real-time shipment monitoring — all active shipments tracked continuously with live status refresh"),
    bullet_para("ML-based risk scoring — each shipment scored 0–100; classified Critical / At Risk / On Track"),
    bullet_para("Delay prediction — estimates disruption impact: port congestion, weather, strikes, equipment failures"),
    bullet_para("Smart route optimization — identifies optimal or alternate routes (air / sea / rail) dynamically"),
    bullet_para("Alternate route comparison — ETA and cost tradeoff charts for up to 3 alternate routes"),
    bullet_para("Disruption alert system — instant flagging of Critical and At-Risk shipments with severity badges"),
    bullet_para("Live dashboard analytics — KPI cards, risk bar charts, delay heatmaps, fleet status pie chart"),
    bullet_para("Gemini AI decision support — Gemini 2.5 Flash generates response plans per disrupted shipment"),
    bullet_para("Demand forecasting — Linear Regression with configurable horizon, ±10% confidence band, reorder alerts"),
    bullet_para("Cloud deployment — Streamlit Cloud, zero-infrastructure, browser-accessible from any device"),
])
new_txbody = build_txbody(paras)
xml5 = re.sub(r'(<p:txBody>.*?</p:txBody>)', new_txbody, xml5, count=1, flags=re.DOTALL)
write(5, xml5)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6 — Process Flow (text header + visual flowchart shapes injected)
# ─────────────────────────────────────────────────────────────────────────────
xml6 = read(6)
# Replace text box with just the header + footer note; flowchart will be shapes
paras = "\n".join([
    heading_para("Process Flow — SmartFlow AI 7-Step Pipeline"),
    spacer("200"),
    bullet_para("Data flows from raw shipment input through ML risk scoring, disruption detection, Gemini AI decision support, and live dashboard output.", sz="1300", color="444444", indent=False),
    spacer("3500"),   # large spacer to leave room for the visual flowchart shapes below
    bullet_para("Actors: Logistics Manager (primary) | External: Weather APIs, Vessel Tracking, Maps APIs, Port Feeds", sz="1100", color="666666", indent=False),
])
new_txbody = build_txbody(paras)
xml6 = re.sub(r'(<p:txBody>.*?</p:txBody>)', new_txbody, xml6, count=1, flags=re.DOTALL)

# Now inject flowchart shapes before </p:spTree>
# Slide is 9144000 x 5143500 EMUs (approx standard 10"x5.63")
# 7 boxes in a row: y=1700000, box w=1050000 h=650000, gap arrows w=200000
# Total = 7*1050000 + 6*200000 = 7350000 + 1200000 = 8550000 (fits in 9144000)
# Start x = (9144000 - 8550000)/2 = 297000

steps = [
    ("1. Data\nInput",       "34A853"),  # Google green
    ("2. Shipment\nMonitor", "1A73E8"),  # Google blue
    ("3. Risk\nDetection",   "EA4335"),  # Google red
    ("4. Delay\nPrediction", "FBBC04"),  # Google yellow — text dark
    ("5. Route\nOptimize",   "1A73E8"),
    ("6. Gemini AI\nEngine", "34A853"),
    ("7. Dashboard\nOutput", "EA4335"),
]
BOX_W = 1050000
BOX_H = 700000
ARROW_W = 200000
ARROW_H = 200000
BOX_Y = 1850000
START_X = 228600
shapes_xml = ""
shape_id = 200

for i, (label, color) in enumerate(steps):
    x = START_X + i * (BOX_W + ARROW_W)
    text_color = "333333" if color == "FBBC04" else "FFFFFF"
    shapes_xml += rect_shape(shape_id, x, BOX_Y, BOX_W, BOX_H, color, label, sz="1000", text_color=text_color) + "\n"
    shape_id += 1
    if i < len(steps) - 1:
        ax = x + BOX_W
        ay = BOX_Y + (BOX_H - ARROW_H) // 2
        shapes_xml += arrow_shape(shape_id, ax, ay, ARROW_W, ARROW_H) + "\n"
        shape_id += 1

# Second row: sub-labels under each box
sub_labels = [
    "CSV / live\nsimulation",
    "Status &\nroute checks",
    "ML scores\n0–100",
    "Delay %\nper shipment",
    "Air/Sea/Rail\nalternates",
    "Gemini 2.5\nFlash API",
    "Charts,\nalerts, KPIs",
]
for i, sub in enumerate(sub_labels):
    x = START_X + i * (BOX_W + ARROW_W)
    y = BOX_Y + BOX_H + 80000
    shapes_xml += label_shape(shape_id, x, y, BOX_W, 500000, sub, sz="900", color="555555") + "\n"
    shape_id += 1

xml6 = xml6.replace("</p:spTree>", shapes_xml + "</p:spTree>")
write(6, xml6)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7 — Wireframes (text only, fix spacing)
# ─────────────────────────────────────────────────────────────────────────────
xml7 = read(7)
paras = "\n".join([
    heading_para("Wireframes / Mock Diagrams of the Proposed Solution"),
    spacer("200"),
    bullet_para("Screen 1 — Live Fleet Dashboard", sz="1500", bold="1", color="1A73E8", indent=False),
    bullet_para("KPI strip: Active Shipments | Critical | At Risk | On Track | Avg Delay (days)"),
    bullet_para("Risk score bar chart per shipment + Fleet status mix pie chart"),
    spacer("200"),
    bullet_para("Screen 2 — Disruption Alerts Tab", sz="1500", bold="1", color="EA4335", indent=False),
    bullet_para("Flagged shipments sorted by risk score with disruption type and severity badges"),
    bullet_para("Gemini AI: root cause analysis + immediate action steps + rerouting recommendation"),
    spacer("200"),
    bullet_para("Screen 3 — Route Optimizer Tab", sz="1500", bold="1", color="34A853", indent=False),
    bullet_para("Select disrupted shipment — compare current route vs 3 alternates (ETA + cost charts)"),
    bullet_para("ETA and Cost bar charts side by side | Gemini rerouting advice on demand"),
    spacer("200"),
    bullet_para("Screen 4 — Demand Forecast Tab", sz="1500", bold="1", color="FBBC04", indent=False),
    bullet_para("Actual sales + forecast trend with ±10% confidence band | Reorder point KPIs"),
    bullet_para("Gemini AI inventory plan — procurement recommendations based on forecast trend"),
])
new_txbody = build_txbody(paras)
xml7 = re.sub(r'(<p:txBody>.*?</p:txBody>)', new_txbody, xml7, count=1, flags=re.DOTALL)
write(7, xml7)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 8 — Architecture Diagram (text header + visual layer shapes)
# ─────────────────────────────────────────────────────────────────────────────
xml8 = read(8)
paras = "\n".join([
    heading_para("Architecture Diagram — SmartFlow AI"),
    spacer("200"),
    bullet_para("Stack: Python 3.11 | Streamlit Cloud | Google Gemini 2.5 Flash | scikit-learn | Pandas | NumPy | Matplotlib | PyDeck | GitHub", sz="1200", color="444444", indent=False),
    spacer("4200"),
])
new_txbody = build_txbody(paras)
xml8 = re.sub(r'(<p:txBody>.*?</p:txBody>)', new_txbody, xml8, count=1, flags=re.DOTALL)

# Architecture: 3 horizontal layers stacked vertically
# Layer 1: Input — y=1500000
# Layer 2: Core AI — y=2500000
# Layer 3: Output — y=3500000
# Each layer has a label box on left (w=1800000) and component boxes on right

arch_shapes = ""
shape_id = 300

layers = [
    {
        "label": "INPUT LAYER",
        "label_color": "1A73E8",
        "y": 1500000,
        "boxes": [
            ("CSV Upload", "E8F0FE", "1A73E8"),
            ("Live Simulation", "E8F0FE", "1A73E8"),
            ("Shipment Data", "E8F0FE", "1A73E8"),
        ]
    },
    {
        "label": "AI / ML LAYER",
        "label_color": "EA4335",
        "y": 2480000,
        "boxes": [
            ("ML Risk Scorer\n(scikit-learn)", "FCE8E6", "EA4335"),
            ("Delay Predictor\n(Linear Reg.)", "FCE8E6", "EA4335"),
            ("Gemini 2.5 Flash\nDecision Engine", "FCE8E6", "EA4335"),
        ]
    },
    {
        "label": "OUTPUT LAYER",
        "label_color": "34A853",
        "y": 3460000,
        "boxes": [
            ("Streamlit\nDashboard UI", "E6F4EA", "34A853"),
            ("Disruption\nAlerts + Charts", "E6F4EA", "34A853"),
            ("Route Optimizer\n+ Forecast", "E6F4EA", "34A853"),
        ]
    }
]

LAYER_H = 800000
BOX_H2 = 680000
LABEL_W = 1600000
BOX_W2 = 2050000
BOX_GAP = 150000
BOX_START_X = LABEL_W + 400000

for layer in layers:
    ly = layer["y"]
    # Label box
    arch_shapes += rect_shape(shape_id, 228600, ly, LABEL_W, LAYER_H,
                              layer["label_color"], layer["label"], sz="1100",
                              text_color="FFFFFF", bold="1") + "\n"
    shape_id += 1
    # Down arrows between layers (except last)
    if layer != layers[-1]:
        ax = 228600 + LABEL_W // 2 - 100000
        ay = ly + LAYER_H + 50000
        arch_shapes += arrow_shape(shape_id, ax, ay, 200000, 280000, vertical=True) + "\n"
        shape_id += 1

    # Component boxes
    for j, (label, fill, border) in enumerate(layer["boxes"]):
        bx = BOX_START_X + j * (BOX_W2 + BOX_GAP)
        by = ly + (LAYER_H - BOX_H2) // 2
        arch_shapes += rect_shape(shape_id, bx, by, BOX_W2, BOX_H2,
                                  fill, label, sz="1050",
                                  text_color="333333", bold="0", border_color=border) + "\n"
        shape_id += 1
        # Arrows between component boxes
        if j < len(layer["boxes"]) - 1:
            ax2 = bx + BOX_W2
            ay2 = by + BOX_H2 // 2 - 100000
            arch_shapes += arrow_shape(shape_id, ax2, ay2, BOX_GAP, 200000) + "\n"
            shape_id += 1

xml8 = xml8.replace("</p:spTree>", arch_shapes + "</p:spTree>")
write(8, xml8)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 9 — Technologies (fix spacing)
# ─────────────────────────────────────────────────────────────────────────────
xml9 = read(9)
paras = "\n".join([
    heading_para("Technologies Used in the Solution"),
    spacer("300"),
    bullet_para("Frontend and Deployment", sz="1500", bold="1", color="1A73E8", indent=False),
    bullet_para("Streamlit — Python web app framework powering the interactive dashboard UI"),
    bullet_para("Streamlit Cloud — free-tier cloud deployment, zero-infrastructure, browser-accessible"),
    spacer("200"),
    bullet_para("AI and Machine Learning", sz="1500", bold="1", color="EA4335", indent=False),
    bullet_para("Google Gemini 2.5 Flash (Google AI API) — disruption response plans, route recommendations, inventory advice"),
    bullet_para("scikit-learn Linear Regression — demand forecasting and shipment delay prediction"),
    spacer("200"),
    bullet_para("Data and Visualization", sz="1500", bold="1", color="34A853", indent=False),
    bullet_para("Pandas and NumPy — data processing, simulation, cleaning, and transformation"),
    bullet_para("Matplotlib — risk charts, demand forecast lines, route ETA and cost comparison bar charts"),
    bullet_para("PyDeck — geospatial live shipment map visualization"),
    spacer("200"),
    bullet_para("Language and Version Control", sz="1500", bold="1", color="444444", indent=False),
    bullet_para("Python 3.11 | GitHub public repository | requirements.txt for full reproducibility"),
])
new_txbody = build_txbody(paras)
xml9 = re.sub(r'(<p:txBody>.*?</p:txBody>)', new_txbody, xml9, count=1, flags=re.DOTALL)
write(9, xml9)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 10 — Cost (fix spacing)
# ─────────────────────────────────────────────────────────────────────────────
xml10 = read(10)
paras = "\n".join([
    heading_para("Estimated Implementation Cost"),
    spacer("300"),
    bullet_para("Current Prototype (MVP) — Zero Cost", sz="1500", bold="1", color="34A853", indent=False),
    bullet_para("Streamlit Cloud free tier: $0 / month"),
    bullet_para("Google Gemini API free tier (60 requests/min): $0 / month for hackathon"),
    bullet_para("GitHub free public repository: $0 / month"),
    spacer("300"),
    bullet_para("Scale-Up Estimate (Production — 1,000 shipments / day)", sz="1500", bold="1", color="1A73E8", indent=False),
    bullet_para("Streamlit Teams or Google Cloud Run: ~$50–150 / month"),
    bullet_para("Google Gemini API paid tier (~10K calls / day): ~$30–80 / month"),
    bullet_para("Google Cloud Storage for shipment data: ~$5–20 / month"),
    bullet_para("Vertex AI (optional ML upgrade): ~$50–200 / month depending on usage"),
    spacer("200"),
    bullet_para("Estimated Total (production scale): $135–$450 / month", sz="1400", bold="1", color="EA4335", indent=False),
    bullet_para("ROI: A single rerouted critical shipment avoiding a 15-day delay saves $10,000–$50,000 in penalties — making SmartFlow AI ROI-positive from day one.", sz="1300", color="444444", indent=False),
])
new_txbody = build_txbody(paras)
xml10 = re.sub(r'(<p:txBody>.*?</p:txBody>)', new_txbody, xml10, count=1, flags=re.DOTALL)
write(10, xml10)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 11 — MVP Snapshots (fix spacing, add live URL)
# ─────────────────────────────────────────────────────────────────────────────
xml11 = read(11)
paras = "\n".join([
    heading_para("Snapshots of the MVP"),
    spacer("200"),
    bullet_para("Live prototype deployed and running at: https://smartsupplychain.streamlit.app/", sz="1400", color="1A73E8", indent=False),
    spacer("200"),
    bullet_para("Dashboard — KPI strip: Active Shipments, Critical count, At Risk, On Track, Avg Delay in days"),
    bullet_para("Disruption Alerts — shipments sorted by risk score with disruption type and severity badges"),
    bullet_para("Risk Distribution — bar chart (risk score per shipment) + pie chart (fleet status mix)"),
    bullet_para("Route Optimizer — current disrupted route vs 3 alternate routes; ETA and cost comparison charts"),
    bullet_para("Gemini AI Response — root cause analysis, immediate action steps, rerouting recommendation"),
    bullet_para("Demand Forecast — actual sales trend + Linear Regression forecast with ±10% confidence band"),
    spacer("300"),
    bullet_para("Demo video (3 minutes) covers all screens end-to-end — link provided in slide 13.", sz="1300", color="444444", indent=False),
])
new_txbody = build_txbody(paras)
xml11 = re.sub(r'(<p:txBody>.*?</p:txBody>)', new_txbody, xml11, count=1, flags=re.DOTALL)
write(11, xml11)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 12 — Future Roadmap (fix spacing)
# ─────────────────────────────────────────────────────────────────────────────
xml12 = read(12)
paras = "\n".join([
    heading_para("Future Development Roadmap"),
    spacer("300"),
    bullet_para("Phase 2 — Real-Time Data Integration (3–6 months)", sz="1500", bold="1", color="1A73E8", indent=False),
    bullet_para("Integrate live APIs: MarineTraffic (vessel tracking), OpenWeatherMap (weather), port congestion feeds"),
    bullet_para("Replace simulated data with real shipment streams from ERP and WMS systems"),
    spacer("200"),
    bullet_para("Phase 3 — Advanced ML and Google Cloud (6–12 months)", sz="1500", bold="1", color="34A853", indent=False),
    bullet_para("Upgrade to Vertex AI AutoML for higher-accuracy disruption prediction"),
    bullet_para("Google Maps Platform for live interactive route visualization on a real map"),
    bullet_para("Multi-tenant SaaS architecture supporting multiple logistics companies"),
    spacer("200"),
    bullet_para("Phase 4 — Enterprise Features (12+ months)", sz="1500", bold="1", color="EA4335", indent=False),
    bullet_para("Supplier risk profiling, carbon footprint tracking, and ESG compliance reporting"),
    bullet_para("Mobile app (Flutter) with push alerts for on-the-go logistics decisions"),
    bullet_para("Integration with SAP, Oracle SCM, and other enterprise logistics platforms"),
])
new_txbody = build_txbody(paras)
xml12 = re.sub(r'(<p:txBody>.*?</p:txBody>)', new_txbody, xml12, count=1, flags=re.DOTALL)
write(12, xml12)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 13 — Project Links (fix placeholder URLs, add live URL)
# ─────────────────────────────────────────────────────────────────────────────
xml13 = read(13)
paras = "\n".join([
    heading_para("Project Links"),
    spacer("300"),
    bullet_para("Provide the following links in your final submission:", sz="1400", indent=False),
    bullet_para("GitHub Public Repository: https://github.com/YOUR_USERNAME/smartflow-ai", sz="1400", color="1A73E8"),
    bullet_para("Demo Video Link (3 Minutes): https://youtube.com/YOUR_DEMO_LINK", sz="1400", color="1A73E8"),
    bullet_para("MVP / Live App Link: https://smartsupplychain.streamlit.app/", sz="1400", color="1A73E8"),
    bullet_para("Working Prototype Link: https://smartsupplychain.streamlit.app/", sz="1400", color="1A73E8"),
    spacer("400"),
    bullet_para("Note: Replace GitHub and YouTube links above with your actual deployed repository and demo video before final submission.", sz="1300", color="EA4335", indent=False),
])
new_txbody = build_txbody(paras)
xml13 = re.sub(r'(<p:txBody>.*?</p:txBody>)', new_txbody, xml13, count=1, flags=re.DOTALL)
write(13, xml13)

print("All slides updated successfully.")
