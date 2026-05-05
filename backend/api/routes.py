from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import numpy as np
from datetime import datetime

# Import your pipelines (assume implemented in services/)
from services.static_threshold import static_threshold_detect
from services.vae_gru_pipeline import vae_gru_detect
from services.explainability import generate_explanation

router = APIRouter()

# -------------------------------
# Request / Response Schemas
# -------------------------------

class SensorInput(BaseModel):
    timestamp: datetime
    engine_temperature: float


class DetectionResponse(BaseModel):
    timestamp: datetime
    temperature: float
    is_anomaly: bool
    method: str
    confidence: float
    explanation: str


# -------------------------------
# Health Check
# -------------------------------

@router.get("/health")
def health_check():
    return {"status": "OK", "message": "Anomaly Detection Service Running"}


# -------------------------------
# Static Threshold Endpoint (Baseline)
# -------------------------------

@router.post("/detect/static", response_model=DetectionResponse)
def detect_static(data: SensorInput):
    try:
        is_anomaly, confidence = static_threshold_detect(data.engine_temperature)

        explanation = (
            "Temperature exceeded fixed threshold"
            if is_anomaly
            else "Within safe threshold limits"
        )

        return DetectionResponse(
            timestamp=data.timestamp,
            temperature=data.engine_temperature,
            is_anomaly=is_anomaly,
            method="static_threshold",
            confidence=confidence,
            explanation=explanation
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Proposed VAE + GRU Endpoint
# -------------------------------

@router.post("/detect/advanced", response_model=DetectionResponse)
def detect_advanced(data: SensorInput):
    try:
        # Convert input to sequence format (simulate streaming window)
        input_sequence = np.array([[data.engine_temperature]])

        result = vae_gru_detect(input_sequence)

        is_anomaly = result["is_anomaly"]
        confidence = result["confidence"]
        reconstruction_error = result["reconstruction_error"]

        explanation = generate_explanation(
            temperature=data.engine_temperature,
            reconstruction_error=reconstruction_error,
            is_anomaly=is_anomaly
        )

        return DetectionResponse(
            timestamp=data.timestamp,
            temperature=data.engine_temperature,
            is_anomaly=is_anomaly,
            method="vae_gru",
            confidence=confidence,
            explanation=explanation
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Hybrid Detection (Reduced False Negatives)
# -------------------------------

@router.post("/detect/hybrid", response_model=DetectionResponse)
def detect_hybrid(data: SensorInput):
    """
    Combines static threshold + VAE-GRU
    Goal: Reduce false negatives by catching subtle anomalies
    """

    try:
        temp = data.engine_temperature

        # Baseline check
        static_flag, static_conf = static_threshold_detect(temp)

        # Advanced model
        input_sequence = np.array([[temp]])
        advanced_result = vae_gru_detect(input_sequence)

        advanced_flag = advanced_result["is_anomaly"]
        advanced_conf = advanced_result["confidence"]
        reconstruction_error = advanced_result["reconstruction_error"]

        # 🔥 Fusion Logic (key improvement)
        # Catch anomalies missed by static threshold
        final_flag = static_flag or advanced_flag

        # Confidence fusion (weighted)
        final_confidence = max(static_conf, advanced_conf)

        explanation = generate_explanation(
            temperature=temp,
            reconstruction_error=reconstruction_error,
            is_anomaly=final_flag,
            hybrid=True,
            static_flag=static_flag,
            advanced_flag=advanced_flag
        )

        return DetectionResponse(
            timestamp=data.timestamp,
            temperature=temp,
            is_anomaly=final_flag,
            method="hybrid_vae_gru",
            confidence=final_confidence,
            explanation=explanation
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Batch Detection (for evaluation)
# -------------------------------

@router.post("/detect/batch")
def detect_batch(data: list[SensorInput]):
    """
    Used for evaluation + metrics (false negatives comparison)
    """

    results = []

    for point in data:
        temp = point.engine_temperature

        static_flag, _ = static_threshold_detect(temp)
        advanced_result = vae_gru_detect(np.array([[temp]]))

        hybrid_flag = static_flag or advanced_result["is_anomaly"]

        results.append({
            "timestamp": point.timestamp,
            "temperature": temp,
            "static": static_flag,
            "advanced": advanced_result["is_anomaly"],
            "hybrid": hybrid_flag
        })

    return {
        "total_points": len(results),
        "results": results
    }
