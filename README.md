# Anomaly Detection Project

This is a full-stack anomaly detection application with a Python FastAPI backend and a React frontend.

## Project Structure

- `backend/` - Python FastAPI backend with anomaly detection models
- `frontend/` - React application with Vite

## Architecture Diagram

```mermaid
graph TB
    A[React Frontend<br/>Port: 5173] -->|HTTP Requests| B[FastAPI Backend<br/>Port: 8000]
    B --> C[Anomaly Detection Service]
    C --> D[VAE Model<br/>Reconstruction Error]
    C --> E[GRU Model<br/>Temporal Analysis]
    C --> F[Threshold Service<br/>Dynamic Thresholds]
    B --> G[Explanation Service<br/>SHAP/LIME]
    B --> H[Fusion Service<br/>Model Ensemble]
    I[Sensor Data<br/>Engine Temperature, etc.] -->|API Calls| B
    B --> J[Database/API<br/>Historical Data]
```

## Detailed Pipeline Diagrams

### VAE+GRU Anomaly Detection Pipeline

```mermaid
graph TD
    A[Sensor Data Input<br/>Time Series] --> B[Data Preprocessing<br/>Normalization, Windowing]
    B --> C[VAE Branch]
    B --> D[GRU Branch]
    
    C --> E[VAE Encoder<br/>Compress to Latent Space]
    E --> F[VAE Decoder<br/>Reconstruct Input]
    F --> G[Reconstruction Error<br/>MSE Loss]
    
    D --> H[GRU Network<br/>Temporal Dependencies]
    H --> I[Sequence Prediction<br/>Next Step Forecast]
    I --> J[Prediction Error<br/>Forecast Accuracy]
    
    G --> K[Fusion Layer<br/>Weighted Combination]
    J --> K
    K --> L[Anomaly Score<br/>Combined Metric]
    L --> M[Threshold Comparison<br/>Dynamic Threshold]
    M --> N{Anomaly?<br/>Yes/No}
    
    N --> O[Normal Operation]
    N --> P[Anomaly Detected<br/>Alert Generation]
```

### SHAP Explainability Layer

```mermaid
graph TD
    A[Anomaly Detection Model<br/>VAE+GRU Pipeline] --> B[SHAP Explainer<br/>Initialize]
    B --> C[Generate Background Dataset<br/>Representative Normal Samples]
    
    D[Test Instance<br/>Anomalous Data Point] --> E[SHAP Kernel Explainer]
    C --> E
    A --> E
    
    E --> F[Compute SHAP Values<br/>Feature Contributions]
    F --> G[Feature Importance Scores<br/>Positive/Negative Impact]
    
    G --> H[Local Explanation<br/>Why this instance is anomalous]
    G --> I[Global Feature Ranking<br/>Most important features]
    
    H --> J[Interactive Dashboard<br/>Feature contribution plots]
    I --> J
    
    J --> K[Model Interpretability<br/>Trust & Debugging]
```

## Architecture

AutoAnomaly-AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── data.py
│   │   │   │   ├── models.py
│   │   │   │   ├── detection.py
│   │   │   │   └── auth.py
│   │   │   └── middleware/
│   │   ├── models/
│   │   │   ├── ml_models.py
│   │   │   ├── database_models.py
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── anomaly_detector.py
│   │   │   ├── data_processor.py
│   │   │   └── model_manager.py
│   │   ├── utils/
│   │   │   ├── preprocessing.py
│   │   │   └── validators.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── DataUpload.jsx
│   │   │   ├── AnomalyVisualization.jsx
│   │   │   └── ModelConfig.jsx
│   │   ├── pages/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   ├── .env.example
│   └── Dockerfile
│
├── config/
│   ├── model_config.yaml
│   └── app_config.yaml
│
├── data/
│   ├── input/
│   ├── output/
│   └── models/
│
├── docs/
│   ├── API.md
│   ├── MODELS.md
│   └── DEPLOYMENT.md
│
├── docker-compose.yml
├── .gitignore
└── README.md

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

## Setup and Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install fastapi uvicorn pydantic numpy
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

## Running the Application

### Start the Backend

1. From the backend directory (with virtual environment activated):
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

   The backend will be available at `http://localhost:8000`

### Start the Frontend

1. From the frontend directory:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173` (default Vite port)

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for the FastAPI interactive documentation.

## Development

- Backend uses FastAPI for the API and includes anomaly detection services
- Frontend is built with React and Vite for fast development
- Models include VAE (Variational Autoencoder) and GRU for anomaly detection

## License

ISC
