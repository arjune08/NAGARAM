# NAGARAM 🏙️

**NAGARAM** is a smart civic and urban management platform designed to connect citizens, municipal teams, NGOs, volunteers, and farmers through a shared digital workspace.

## 🌟 What it does

NAGARAM brings together civic issue reporting, infrastructure monitoring, risk analysis, maintenance planning, sustainability tracking, and decision-support tools in one Flask-based application.

### 🏛️ Civic & Urban Management
- Citizen complaint and issue tracking
- Infrastructure asset monitoring
- Risk assessment and prioritization
- Predictive maintenance workflows
- Maintenance team and resource management
- City health and infrastructure risk dashboards
- Geospatial data for complaints, assets, and emergency services
- Sustainability indicators and SDG-oriented monitoring
- Admin audit logs and decision-support tools

### 🧠 AI & Decision Support
NAGARAM includes prototype AI-assisted features for:
- Identifying urgent infrastructure risks
- Recommending maintenance crew deployment
- Providing city-health insights
- Exploring traffic and road-closure scenarios
- Supporting what-if analysis through a digital-twin interface

### 🌾 AGRI-NAGARAM
The platform also includes an agricultural workspace for farmers, sharing the same authentication and action network. It supports:
- Farm management
- Farm issue reporting
- Weather and crop-health scenario inputs
- Market opportunity information
- Prototype recommendations and decision scenarios

> Agricultural decision outputs and market values in the prototype are explicitly treated as demo/estimated data and are not scientific agronomic predictions.

## 🏗️ System Architecture

```mermaid
flowchart TB
    U[Users & Stakeholders] --> UI[Web Interface / Dashboards]

    U --> C[Citizens]
    U --> F[Farmers]
    U --> A[Admins / Municipal Teams]
    U --> O[NGOs / Volunteers]

    C --> UI
    F --> UI
    A --> UI
    O --> UI

    UI --> AUTH[Authentication & Role Control]
    AUTH --> APP[Flask Application]

    APP --> CIVIC[Civic & Community Workflows]
    APP --> AGRI[AGRI-NAGARAM]
    APP --> AI[AI & Decision Support]
    APP --> ADMIN[Admin Command Center]

    CIVIC --> DB[(PostgreSQL / SQLAlchemy)]
    AGRI --> DB
    AI --> DB
    ADMIN --> DB

    AI --> RISK[Risk Engine]
    AI --> PM[Predictive Maintenance]
    AI --> DT[Digital Twin / Scenarios]
    AI --> OPT[Resource Optimization]

    CIVIC --> MAP[Geospatial / Map Data]
    MAP --> DB

    ADMIN --> AUDIT[Audit Logging]
    AUDIT --> DB
```

### Architecture layers

| Layer | Responsibility |
|---|---|
| **Presentation** | Role-based web pages, dashboards, maps and management interfaces |
| **Authentication** | Login, sessions and role-based access control |
| **Application** | Flask routes, civic workflows, farmer workflows and admin operations |
| **Intelligence** | Risk analysis, predictive maintenance, recommendations and scenario simulation |
| **Data** | SQLAlchemy models with PostgreSQL support |
| **Integration** | Shared identity and action network between civic and agricultural workspaces |

## 🔄 Core Civic Issue Flow

```mermaid
flowchart LR
    C[Citizen Reports Issue] --> R[Complaint Created]
    R --> V[Issue Validation & Categorization]
    V --> S[Severity / Priority Assessment]
    S --> Risk[Infrastructure Risk Analysis]
    Risk --> D{High Risk?}
    D -- Yes --> T[Assign Maintenance Team]
    D -- No --> Q[Queue for Normal Workflow]
    T --> M[Maintenance Action]
    Q --> M
    M --> U[Update Status]
    U --> X[Citizen / Admin Visibility]
    U --> L[Audit Log]
```

## 🧠 AI Decision-Support Flow

```mermaid
flowchart TD
    DATA[City Data] --> INGEST[Data & Model Inputs]
    INGEST --> ANALYZE[AI / Rule-Based Analysis]
    ANALYZE --> RISK[Risk Detection]
    ANALYZE --> REC[Recommendations]
    ANALYZE --> SIM[What-If Simulation]

    RISK --> DASH[Decision Dashboard]
    REC --> DASH
    SIM --> DASH

    DASH --> ACTION[Human Decision & Action]
    ACTION --> FEEDBACK[Updated Operational Data]
    FEEDBACK --> DATA
```

> **Note:** AI outputs in the current project are prototype decision-support features. They should be reviewed by responsible human operators before real-world action.

## 🌾 AGRI-NAGARAM Flow

```mermaid
flowchart LR
    F[Farmer] --> FD[Farmer Dashboard]
    FD --> FARM[Farm Management]
    FD --> ISSUE[Farm Issue Reporting]
    FD --> WEATHER[Weather Scenario]
    FD --> HEALTH[Crop Health / Pest Risk]
    FD --> MARKET[Market Opportunity]

    WEATHER --> DEC[Prototype Decision Model]
    HEALTH --> DEC
    FARM --> DEC
    MARKET --> DEC
    DEC --> REC[Recommendation State]
    ISSUE --> NOTIFY[Shared Action Network]
    NOTIFY --> OPS[Relevant Platform Users]
```

## 🔐 Role & Access Flow

```mermaid
flowchart TD
    LOGIN[User Login / Registration] --> AUTH{Authenticated?}
    AUTH -- No --> RETRY[Return to Authentication]
    AUTH -- Yes --> ROLE{User Role}

    ROLE -->|Citizen| CIT[Citizen Workspace]
    ROLE -->|Farmer| FAR[AGRI-NAGARAM Workspace]
    ROLE -->|Admin| ADM[Admin Command Center]
    ROLE -->|NGO / Volunteer| ORG[Organization Workflows]

    ADM --> CONTROL[Risk, Maintenance, Resources & Digital Twin]
    CIT --> REPORT[Report & Track Civic Issues]
    FAR --> FARMER[Manage Farms & Issues]
    ORG --> COMMUNITY[Community Support]
```

## 🛠️ Technology

- **Backend:** Python, Flask
- **Database:** SQLAlchemy with PostgreSQL support
- **Authentication:** Flask-Login
- **Forms & security:** Flask-WTF, Werkzeug
- **Configuration:** python-dotenv
- **Frontend:** HTML templates and web-based dashboards

## 📁 Main capabilities

```text
NAGARAM
├── Civic reporting & community workflows
├── Admin command center
├── Infrastructure risk engine
├── Predictive maintenance
├── Resource optimization
├── Digital Twin / scenario simulation
├── Sustainability dashboard
├── Data hub & audit logging
└── AGRI-NAGARAM farmer workspace
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/arjune08/NAGARAM.git
cd NAGARAM
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it according to your operating system.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and configure the database and application settings required by the project.

### 5. Run the application

Start the Flask application using the repository's existing application entry point.

## 🔐 User roles

NAGARAM is structured around multiple platform roles, including citizens, farmers, administrators, NGOs, and volunteers, with role-specific workflows and dashboards.

## 🎯 Vision

NAGARAM aims to make cities more **responsive, resilient, sustainable, and data-driven** by turning community reports and infrastructure data into actionable information for the teams responsible for improving everyday urban life.

## 📌 Project status

NAGARAM is an evolving prototype focused on demonstrating an integrated smart-city platform and its potential extension into agriculture and community services.

---

**Built with Python, Flask, SQLAlchemy, and a vision for smarter communities.**
