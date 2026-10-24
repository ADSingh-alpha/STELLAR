<div align="center">

<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
<img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
<img src="https://img.shields.io/badge/LangGraph-Agentic-6750A4?style=for-the-badge" />

<br/><br/>

# 🛰️ Stellar AI
### *Multi-Agent Satellite Intelligence Platform*

**Natural Language Interface for Earth Observation · Powered by LangGraph Agentic Orchestration**

[Architecture](#architecture) · [Workflow](#workflow) · [Specialist Models](#-specialist-models) · [Setup](#setup--installation) · [API Reference](#-api-reference)

</div>

---

## 📌 Problem Statement

Satellite imagery from missions like **Sentinel-1 (SAR)** and **Sentinel-2 (Optical)** generates petabytes of geospatial data daily. Yet, extracting actionable intelligence from this data requires specialized GIS expertise, complex toolchains, and significant processing time — creating a high barrier for disaster response teams, urban planners, and environmental researchers.

**Stellar AI** eliminates this barrier by enabling anyone to query satellite imagery using plain natural language.

---

## 🎯 What is Stellar AI?

Stellar AI is a **multi-agent Earth Observation (EO) intelligence platform** that processes satellite imagery queries through an autonomous LangGraph state graph. It routes natural language questions to specialized AI models for:

| Capability | Description |
|---|---|
| 🔍 **Visual Question Answering** | Ask questions about satellite scenes in plain English |
| 🗺️ **Open-Vocabulary Grounding** | Locate & draw bounding boxes around any target entity |
| 🔄 **Bi-Temporal Change Detection** | Detect and quantify land-cover changes between two time periods |
| 📡 **Optical-SAR Fusion** | Fuse Sentinel-1 SAR with Sentinel-2 optical for all-weather analysis |
| 🌿 **Land Cover Classification** | Segment and classify terrain into 14+ LULC categories |
| 🔗 **Compound Pipelines** | Chain multiple specialists for complex multi-step analysis |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      Stellar AI — System Architecture                       │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐   HTTPS   ┌──────────────────────┐  REST/WS  ┌─────────────────────────────────┐
│                  │◄─────────►│                      │◄──────────►│                                 │
│ React Frontend   │           │  Express.js Gateway  │            │  FastAPI AI Agent Microservice  │
│ (Vite · Port 5173)          │  (Node.js · Port 5000)            │  (Uvicorn · Port 8000)          │
│                  │           │                      │            │                                 │
│ · ConstellationField WebGL  │  · Auth Proxy        │            │  ┌─────────────────────────┐   │
│ · LiquidMetal Chat UI       │  · JWT Middleware     │            │  │  LangGraph State Graph  │   │
│ · GlassSidebar History      │  · PostgreSQL ORM    │            │  │                         │   │
│ · Liquid Query Bar          │  · Query History API │            │  │  [Input Validator]      │   │
│ · ISRO / India Badges       │                      │            │  │         ↓               │   │
│ · Language Switcher         └──────────────────────┘            │  │  [Controller Router]    │   │
│                                       ▲                          │  │         ↓               │   │
└──────────────────┘                    │                          │  │  [Interpret & Validate] │   │
                                        │ PostgreSQL               │  │         ↓               │   │
                                 ┌──────┴──────┐                   │  │  [Specialist Pipeline]  │   │
                                 │  Auth DB    │                   │  │   ↙  ↓  ↓  ↓  ↘       │   │
                                 │  (SQLite /  │                   │  │  VQA Gnd CD SAR LC     │   │
                                 │  Postgres)  │                   │  │         ↓               │   │
                                 └─────────────┘                   │  │  [Output Synthesizer]   │   │
                                                                   │  └─────────────────────────┘   │
                                                                   └─────────────────────────────────┘
```

### Directory Structure

```
📦 StellarAI/
├── 🖥️  client/                      # React + Vite Frontend
│   └── src/
│       ├── pages/
│       │   └── Scene.jsx            # WebGL ConstellationField intro
│       ├── components/
│       │   ├── LiquidMetalChatUI    # Main chat interface
│       │   ├── GlassSidebar         # Navigation + query history
│       │   ├── LiquidMetalQueryBar  # Natural language query input
│       │   ├── TopologyBackground   # Animated mesh background
│       │   └── TwinklingStars       # Particle star field
│       └── services/
│           └── authService          # JWT auth management
│
├── 🌐  server/                      # Express.js API Gateway
│   ├── server.js                    # Entry point (Port 5000)
│   ├── config/db.js                 # PostgreSQL connection
│   ├── routes/                      # Auth + query routing
│   ├── middleware/                  # JWT verification
│   └── models/                     # Sequelize data models
│
└── 🤖  ai_agent/                    # Python AI Microservice
    ├── main.py                      # FastAPI entrypoint (Port 8000)
    ├── agent_core/
    │   ├── orchestrator.py          # LangGraph state machine
    │   ├── tools.py                 # Specialist tool registry
    │   ├── state.py                 # AgentState + RSAgentState schemas
    │   └── query_validator.py       # Input gatekeeping
    ├── specialist_models/
    │   ├── vision_vqa.py            # VLM with 4-bit NF4 quantization
    │   ├── change_det.py            # Siamese bi-temporal change detector
    │   ├── cross_modal.py           # Optical-SAR cross-attention fusion
    │   ├── bigearthnet_pipeline.py  # BigEarthNet 14-band data pipeline
    │   ├── train_lora_sft.py        # LoRA supervised fine-tuning trainer
    │   └── merge_lora.py            # LoRA weight consolidation
    ├── utils/
    │   ├── geospatial.py            # Rasterio/GDAL raster validation
    │   └── report.py                # Audit report generator
    └── persistence.py               # SQLite/Postgres audit trail
```

---

## 🔄 Workflow

### End-to-End Query Processing Pipeline

```
 User submits query + satellite image(s)
               │
               ▼
 ┌─────────────────────────────────┐
 │      Node 1: Input Validator    │
 │  · Query meaningfulness check   │
 │  · Geospatial coordinate bounds │
 │  · Image format validation      │
 │    (GeoTIFF / COG / JP2 / PNG)  │
 │  · Modality compatibility check │
 └──────────────┬──────────────────┘
                │ VALID ✓
                ▼
 ┌─────────────────────────────────┐
 │    Node 2: Controller Router    │
 │  · Keyword + semantic analysis  │
 │  · Task classification          │
 │  · Image count detection        │
 │  · Compound pipeline assembly   │
 │  · Execution queue construction │
 └──────────────┬──────────────────┘
                │
                ▼
 ┌─────────────────────────────────┐
 │  Node 2b: Interpret & Validate  │
 │  · Conversational memory lookup │
 │  · Relative reference resolution│
 │    ("that box", "same spot")    │
 │  · LLM-based task confirmation  │
 │  · Modality compatibility check │
 └──────────────┬──────────────────┘
                │
                ▼
 ┌─────────────────────────────────────────────────────────┐
 │           Node 3: Specialist Pipeline Executor          │
 │                                                         │
 │ ┌────────────┐ ┌────────────┐ ┌────────────────────┐   │
 │ │ vision_vqa │ │grounding_rs│ │  change_detector   │   │
 │ │ 4-bit NF4  │ │Open-Vocab  │ │  Siamese-STANet    │   │
 │ │ LoRA SFT   │ │BBox output │ │  Change Masks      │   │
 │ └────────────┘ └────────────┘ └────────────────────┘   │
 │                                                         │
 │ ┌─────────────────────┐  ┌───────────────────────┐     │
 │ │  cross_modal_fusion │  │  land_cover_classifier│     │
 │ │  CrossAttentionNet  │  │  BigEarthNet 14-Band  │     │
 │ │  Sentinel-1 + S-2   │  │  LULC Segmentation   │     │
 │ └─────────────────────┘  └───────────────────────┘     │
 │                                                         │
 │  ◄── Compound pipelines chain specialists ──►           │
 └──────────────┬──────────────────────────────────────────┘
                │
                ▼
 ┌─────────────────────────────────┐
 │     Node 4: Output Synthesizer  │
 │  · Multi-specialist result merge│
 │  · Confidence score aggregation │
 │  · GeoJSON / GeoTIFF artifacts  │
 │  · Audit trail persistence      │
 │  · Spatial context cache update │
 └──────────────┬──────────────────┘
                │
                ▼
         Structured Response
  (Text + BBoxes + Change Mask
   + Metrics + Artifacts + Trace)
```

### Compound Pipeline Example

> **"What was built in this area between 2022 and 2023? Describe the changes."**

```
[Change Detector] ─→ change mask + diff regions
        ↓
[Crop differential region from mask]
        ↓
[Vision VQA] ─→ describes the detected changed zone
        ↓
 Synthesized: "New residential construction detected.
              Built-up area increased by 34% in T2..."
```

---

## 🧠 Specialist Models

### 1. 🔍 VisionVQAModel — Visual Question Answering
- **Backbone**: Fine-tuned Vision-Language Model (VLM)
- **Quantization**: 4-bit NormalFloat4 (NF4) with merged LoRA weights
- **Training**: LoRA SFT on BigEarthNet 14-band Sentinel-1/2 pairs
- **Tasks**: Multi-spectral scene understanding, caption generation
- **Formats**: GeoTIFF, COG, JP2, PNG, JPEG

### 2. 🔄 ChangeDetector — Bi-Temporal Change Detection
- **Architecture**: Siamese network / STANet-inspired
- **Input**: T1 (before) + T2 (after) co-registered rasters
- **Output**: Binary change mask, changed area in km², textual description
- **Use Cases**: Deforestation, urban expansion, flood extent, disaster damage

### 3. 📡 CrossModalFusion — Optical-SAR Fusion
- **Architecture**: CrossAttentionNet-S1S2
- **Input**: Sentinel-2 optical + Sentinel-1 SAR (GeoTIFF pairs)
- **Fusion Strategies**: `pixel_level`, `feature_fusion`, `cross_attention`
- **Capability**: Cloud-penetrating all-weather composite generation
- **Polarizations**: VV+VH SAR modes

### 4. 🌿 LandCoverClassifier — LULC Segmentation
- **Pipeline**: BigEarthNet 14-band multi-spectral classification
- **Categories**: Urban, forest, agriculture, water bodies, wetlands, bare soil, and more
- **Output**: Category distribution map + area percentages

---

## 🔁 Conversational Memory System

Stellar AI maintains **multi-turn spatial context** across conversations:

| Feature | Description |
|---|---|
| **Spatial Context Cache** | Fast O(1) lookup of active bounding boxes and ROIs |
| **Conversation History** | Full turn-by-turn log with detected boxes & image paths |
| **Relative Reference Resolution** | Understands "that box", "same spot", "adjacent to it" |
| **Modality Reference** | "Check the SAR image" → auto-resolves correct raster path |
| **Pronoun Anaphora** | "Describe it" → resolves to last detected spatial object |

---

## 🛡️ Validation & Guardrails

### Input Guardrails
- ✅ GeoTIFF / COG / JP2 / NetCDF / HDF5 format enforcement
- ✅ Geospatial coordinate boundary checks (lat: ±90, lon: ±180)
- ✅ Query gibberish / keyboard-mash detection
- ✅ Modality compatibility enforcement (JPEG rejected for SAR fusion)
- ✅ Parameterized tool whitelist — strips unknown parameters before execution

### Tool Parameter Whitelist
```python
TOOL_PARAM_WHITELIST = {
  "change_detector":       { threshold: [0.0–1.0], patch_size: [64–1024] },
  "grounding_rs":          { box_threshold: [0.0–1.0], n_bboxes: [1–20] },
  "cross_modal_fusion":    { fusion_strategy: {pixel_level, feature_fusion, cross_attention} },
  "land_cover_classifier": { compute_area_metrics: bool, target_classes: list },
}
```

---

## 🖥️ Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| **React 18 + Vite** | UI framework with HMR dev server |
| **WebGL (ConstellationField)** | Immersive intro scene |
| **Glassmorphism CSS** | LiquidMetal chat UI aesthetic |
| **JWT Auth** | Client-side session management |

### Backend (API Gateway)
| Technology | Purpose |
|---|---|
| **Node.js + Express.js** | REST API gateway (Port 5000) |
| **PostgreSQL** | User auth + query history persistence |
| **JWT + bcrypt** | Secure authentication |

### AI Microservice
| Technology | Purpose |
|---|---|
| **FastAPI + Uvicorn** | Async REST + WebSocket endpoints (Port 8000) |
| **LangGraph** | State graph orchestration |
| **LangChain** | Tool wrappers + StructuredTool |
| **Transformers (HuggingFace)** | VLM backbone |
| **PEFT + LoRA** | 4-bit quantized fine-tuning |
| **BitsAndBytes** | NF4 quantization |
| **Rasterio + GDAL** | GeoTIFF / raster processing |
| **Shapely + PyProj** | Geospatial geometry operations |
| **OpenCV** | Image preprocessing |
| **SQLAlchemy + SQLite** | Audit trail persistence |

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- CUDA-capable GPU (recommended for model inference)

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/StellarAI.git
cd StellarAI
```

### 2. Install All Dependencies
```bash
npm run install:all
```

### 3. Setup AI Agent (Python)
```bash
cd ai_agent
pip install -r requirements.txt
```

### 4. Configure Environment Variables

**`ai_agent/.env`**
```env
HF_TOKEN=your_huggingface_token
MODEL_CHECKPOINT=path/to/weights
```

**`server/.env`**
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/stellar
JWT_SECRET=your_jwt_secret
PORT=5000
```

### 5. Run the Full Stack
```bash
npm run dev
```

| Service | URL |
|---|---|
| Frontend (Vite) | http://localhost:5173 |
| API Gateway (Express) | http://localhost:5000 |
| AI Agent (FastAPI) | http://localhost:8000 |
| FastAPI Swagger Docs | http://localhost:8000/docs |

---

## 📡 API Reference

### `POST /query`
Submit a satellite intelligence query with optional image attachments.

**Request:**
```json
{
  "query": "What has changed between these two satellite images?",
  "uploaded_images": [
    { "file_path": "/uploads/t1_2022.tif", "role": "t1" },
    { "file_path": "/uploads/t2_2023.tif", "role": "t2" }
  ],
  "geo_context": { "latitude": 28.6, "longitude": 77.2 },
  "conversation_id": "uuid-optional"
}
```

**Response includes:**
- `summary` — Core finding in natural language
- `bounding_boxes` — WGS84 spatial bounding box detections
- `spatial_mask` — Change mask / segmentation data
- `metrics` — Area statistics (km², percentages)
- `artifacts` — Downloadable GeoTIFF / GeoJSON outputs
- `thought_trace` — Full agent reasoning chain
- `confidence` — Model certainty score

### `POST /upload` — Upload satellite raster files (GeoTIFF, COG, JP2, PNG)
### `GET /history/{session_id}` — Retrieve past query results
### `POST /auth/signup` · `POST /auth/login` — JWT authentication

---

## 📊 Supported Image Formats

| Format | Extension | VQA | Grounding | Change Det | SAR Fusion |
|---|---|:---:|:---:|:---:|:---:|
| GeoTIFF | `.tif` `.tiff` | ✅ | ✅ | ✅ | ✅ |
| Cloud-Optimized GeoTIFF | `.cog` | ✅ | ✅ | ✅ | ✅ |
| JPEG 2000 | `.jp2` | ✅ | ✅ | ✅ | ✅ |
| NetCDF | `.nc` | ✅ | ✅ | — | — |
| HDF5 | `.hdf5` `.h5` | ✅ | ✅ | — | — |
| Sentinel SAFE | `.safe` | ✅ | — | — | ✅ |
| PNG / JPEG | `.png` `.jpg` | ✅ | ✅ | — | — |

---

## 🏆 SIH 2024 — Key Innovations

| Innovation | Impact |
|---|---|
| **LangGraph Multi-Agent Orchestration** | Dynamic compound specialist chaining — no hardcoded pipelines |
| **Conversational Spatial Memory** | Multi-turn EO analysis with anaphora & reference resolution |
| **Compound EO Pipelines** | SAR Fusion → Change Detection → VQA in one natural language query |
| **Parameterized Tool Guardrails** | Strict whitelist schema prevents hallucinated tool parameters |
| **4-bit NF4 LoRA VLM** | Production-grade quantized VLM trained on BigEarthNet Sentinel data |
| **All-Weather SAR Fusion** | Cloud-penetrating analysis using Sentinel-1 cross-attention |
| **WGS84 Bounding Box Outputs** | Geo-referenced detections usable directly in GIS tools |
| **Liquid Metal UI** | Premium glassmorphism + WebGL frontend for intuitive interaction |

---

## 🌍 Use Cases

- 🌊 **Flood Monitoring** — Detect inundation extent using SAR + optical fusion
- 🌳 **Deforestation Alerts** — Quantify canopy loss between temporal captures
- 🏗️ **Urban Growth Tracking** — Monitor construction and infrastructure expansion
- 🌾 **Crop Health Analysis** — Multi-spectral biomass and NDVI assessment
- 🚢 **Maritime Surveillance** — Vessel detection in SAR imagery
- 💥 **Disaster Damage Assessment** — Before/after change maps for emergency response
- 🗺️ **Land Cover Mapping** — Automated LULC classification at scale

---

<div align="center">

**Made with ❤️ for ISRO · Bharat 🇮🇳**

*Stellar AI — Democratizing Earth Observation Intelligence*

</div>
