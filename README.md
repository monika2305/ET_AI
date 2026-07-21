EPC Intelligence Platform

AI-powered project intelligence for Data Centre EPC delivery — unifying asset risk, commissioning readiness, dependency cascade analysis, and natural language Q&A into a single decision platform.

Overview

India's data centre construction market is projected to grow from 900 MW in 2024 to over 2,700 MW by 2027, representing $15B+ in capital deployment. A single hyperscale facility involves 15,000–40,000 equipment line items, hundreds of concurrent trade contractors, and thousands of commissioning test procedures — with zero tolerance for errors.

EPC Intelligence Platform addresses the core problem: information fragmentation. Specifications, vendor submittals, delivery records, RFI logs, and commissioning checklists exist in disconnected systems. This platform connects them into a living intelligence layer that answers five questions visually:

Are we ready for commissioning?
What is blocking us?
What will be affected if something delays?
What should we fix first?
Will we be ready on time?
Features
Module	Description
Executive Dashboard	Project Health Score, Commissioning Readiness %, Critical Assets At Risk, Predicted Delay Days, Business Impact, Benchmark Comparison
Asset & Supply Chain Intelligence	Full asset register with risk scoring, delivery status, lead-time analysis, spec compliance checking
Dependency & Risk Intelligence	NetworkX knowledge graph, cascade impact simulation, scenario analysis, risk heatmap
Commissioning & RFI	Prerequisite readiness tracking, hard blocker identification, mitigation recommendations, RFI log with precedent matching
AI Copilot	RAG-powered Q&A over specs, submittals, commissioning protocols, and RFI logs using Groq LLaMA
Tech Stack
Frontend        Streamlit
LLM             Groq (LLaMA 3.3 70B)
Vector Database ChromaDB
Knowledge Graph NetworkX
Visualization   Plotly
Data            CSV (structured project data)
Language        Python 3.11+
Project Structure
epc-platform/
├── app.py                          # Entry point + sidebar navigation
├── requirements.txt
├── .streamlit/
│   └── config.toml                 # Dark theme config
├── data/
│   ├── critical_assets.csv         # 20 critical equipment items
│   ├── dependencies.csv            # Asset → milestone → system edges
│   ├── commissioning_checklist.csv # Prerequisites with completion %
│   ├── milestones.csv              # Project schedule milestones
│   └── specifications_knowledge.csv # RAG knowledge base (specs, RFIs, submittals)
├── pages_modules/
│   ├── p0_landing.py               # Marketing landing page
│   ├── p1_executive.py             # Executive Dashboard
│   ├── p2_assets.py                # Asset & Supply Chain Intelligence
│   ├── p3_dependency.py            # Dependency & Risk Intelligence
│   ├── p4_commissioning.py         # Commissioning & RFI
│   └── p5_ai.py                    # AI Copilot
└── utils/
    ├── data_loader.py              # Cached CSV loading
    ├── risk_engine.py              # Asset risk scoring, project health
    ├── dep_engine.py               # NetworkX graph + cascade traversal
    ├── comm_engine.py              # Commissioning readiness calculation
    ├── mitigation_engine.py        # Rule-based mitigation recommendations
    ├── rag_engine.py               # ChromaDB + Groq RAG pipeline
    └── styles.py                   # Design tokens and CSS
Getting Started
1. Clone the repository
bash
git clone https://github.com/your-username/epc-intelligence-platform.git
cd epc-intelligence-platform
2. Install dependencies
bash
pip install -r requirements.txt
pip install groq
3. Get a free Groq API key

Sign up at https://console.groq.com → API Keys → Create key.

4. Set the API key

Windows (PowerShell):

powershell
$env:GROQ_API_KEY="gsk_your-key-here"

macOS / Linux:

bash
export GROQ_API_KEY="gsk_your-key-here"
5. Run the app
bash
streamlit run app.py

Opens at http://localhost:8501

How It Works
Asset Risk Scoring

Every critical asset is scored 0–100 based on:

Delivery status (Delayed / In Transit / Delivered)
Days overdue vs. expected delivery
Lead time length (longer = higher inherent risk)

Risk bands: Critical (65+) · High (40+) · Medium (20+) · Low

Dependency Cascade Engine

A directed graph is built from the dependency CSV:

Asset → Milestone → System

When any asset is selected, the engine traverses all downstream nodes using NetworkX to compute:

Impacted milestones
Affected systems
Cascade depth
Full impact chain (e.g. Switchgear Delayed → Energization Blocked → Commissioning Delayed → Handover Delayed)
RAG Pipeline

Project documents (specs, submittals, commissioning protocols, RFI logs) are embedded into ChromaDB using the default MiniLM sentence-transformer. On query:

Top-4 relevant chunks retrieved by cosine similarity
Context passed to Groq LLaMA 3.3 70B with a structured prompt
Response returned with source citations

Offline fallback: If no API key is set, the app shows retrieved source excerpts directly — fully demoable without any key.

Data Model
File	Contents
critical_assets.csv	20 equipment items — transformer, switchgear, UPS, generators, chillers, CRAH, IT gear — with vendor, lead time, order/delivery dates, status
dependencies.csv	Directed edges: asset → milestone → system, with relationship type (blocks/affects)
commissioning_checklist.csv	14 prerequisites with completion %, status, blocking milestone, related asset
milestones.csv	7 project milestones — planned vs. forecast dates, critical path flag
specifications_knowledge.csv	12 documents — technical specs, vendor FAT reports, commissioning protocols, RFI logs

All data is internally consistent — delayed assets in critical_assets.csv map to blockers in commissioning_checklist.csv, which map to at-risk milestones in milestones.csv, which are explained in specifications_knowledge.csv.

Demo Script

For hackathon presentations, follow this narrative across all five modules:

Landing Page — Platform overview
Executive Dashboard → Show composite health score and top risks
Asset & Supply Chain → Drill into a delayed asset (e.g. Switchgear SG1)
Dependency & Risk → Select that same asset, show cascade chain and knowledge graph
Commissioning & RFI → Show readiness gauge, blockers, and mitigation plan for that asset
AI Copilot → Ask "What is the cascade impact of the Switchgear delay?" live

This keeps one asset as a throughline across all modules, which reads as a coherent intelligence platform rather than six disconnected demos.

Hackathon Context

Built for ET AI Hackathon 2026 — Problem Statement: AI Intelligence Platform for Data Centre EPC Project Delivery

Evaluation criteria addressed:

Criteria	Implementation
Business Impact (25%)	Penalty exposure calculator, benchmark comparison, manual hours saved
Technical Excellence (25%)	RAG pipeline, knowledge graph traversal, risk scoring engine
Scalability (20%)	Modular architecture, CSV → database swap ready, any IFC/ERP data source
Innovation (15%)	Cascade simulation, precedent-matched RFI resolution, AI Copilot with citations
User Experience (15%)	Dark enterprise UI, KPI-first layout, expandable details, sub-second navigation
License

MIT License — free to use, modify, and distribute.

Acknowledgements
Streamlit — UI framework
Groq — LLM inference (LLaMA 3.3 70B)
ChromaDB — Vector database
NetworkX — Graph analysis
Plotly — Interactive visualizations
JLL Data Centre Report 2025 — Market context
Turner & Townsend Asia-Pacific EPC Survey 2024 — Benchmark data
