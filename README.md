# 🛡️ Social Media Defense & Botnet Neutralization Platform

### Detect. Analyze. Defend.
A comprehensive full-stack security infrastructure designed to identify, track, and neutralize coordinated misinformation campaigns and automated bot networks in real-time.

---

## 📌 Project Overview
This platform is a sophisticated defense engine that simulates real-world cybersecurity operations. It moves beyond simple text analysis to provide a multi-layered security approach, combining behavioral intelligence, network propagation tracking, and automated incident response.

The system is designed to act as a **Security Operations Center (SOC)** for digital discourse, providing end-to-end visibility into how threats emerge and spread.

---

## 🚀 Core Features

### 🔍 1. Threat Detection Engine
* **Heuristic Analysis:** Linguistic processing to identify sensationalist patterns and high-risk terminology.
* **Credibility Indexing:** Generates real-time scores for content authenticity (0–100%).
* **Automated Firewalling:** Every intercepted signal is assigned a status: 
    * `✅ SAFE` 
    * `🚩 FLAGGED` 
    * `⚠️ QUARANTINED` 
    * `❌ BLOCKED`

### 🤖 2. Bot & Behavioral Intelligence
* **Pattern Recognition:** Detects repetitive text signatures and excessive metadata anomalies.
* **Account Classification:** Categorizes entities into Human, Suspicious, or Automated Bot profiles.
* **Network Clustering:** Identifies "Bot Armies" by grouping accounts exhibiting coordinated timing and content patterns.

### 🌐 3. Spread & Containment Simulation
* **Network Graphing:** Visualizes "Patient Zero" and the propagation path using interactive node-link diagrams.
* **Containment Modeling:** Compares uncontained viral spread against active neutralization efforts to measure defense effectiveness.

### ⚔️ 4. Active Incident Response
* **The "War Room":** A central management dashboard that groups related signals into macro-level **Incidents** with assigned severity (Low to Critical).
* **Truth Injection:** Simulates automated counter-responses to neutralize detected misinformation families at the source.
* **Self-Evolving Signatures:** The system archives new threat patterns into a permanent database to improve future detection speeds.

---

## 🏗️ System Architecture

### 🔹 Frontend (The Dashboard)
* **UI/UX:** Modern Glassmorphism interface with a dark-theme SOC aesthetic.
* **Visualizations:** Powered by **Chart.js** (threat metrics) and **Vis-network** (dynamic propagation maps).
* **Operation Modes:** Toggle between **Live Intercept Stream** (automated data ingestion) and **Manual Override** (custom analysis).

### 🔹 Backend (The Logic)
* **Process Engine:** Python-based architecture handling complex logic and API orchestration.
* **Data Pipeline:** Real-time ingestion system that streams data from structured datasets into the analysis engine.

### 🔹 Database (The Intelligence)
* **Storage:** **SQLite** integration for persistent logging of incidents, threat signatures, and historical analysis data.

---

## 🔄 Technical Workflow
1. **Ingestion:** Data is pulled from the Live Feed or manual user input.
2. **Analysis:** The engine runs concurrent checks for linguistic risk and behavioral bot patterns.
3. **Scoring:** The system calculates the Trust Score, Risk Score, and Virality Potential.
4. **Visualization:** Real-time updates are pushed to the Network Map and the War Room dashboard.
5. **Mitigation:** The Incident Management system logs the event and generates a counter-defense protocol.

---

## 🛠️ Installation & Execution

### 1. Initialize the Backend
Navigate to the project directory and start the server:
```bash
python3 server.py
