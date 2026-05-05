from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import numpy as np

from services.anomaly_service import anomaly_service

router = APIRouter()


# -----------------------------------
# Request Schema
# -----------------------------------
class EngineSensorInput(BaseModel):
    timestamp: datetime
    engine_temperature: float


# -----------------------------------
# Response Schema
# -----------------------------------
class DetectionResponse(BaseModel):
    timestamp: datetime
    temperature: float
    is_anomaly: bool
    method: str
    confidence: float
    static_flag: bool = None
    vae_flag: bool = None
    gru_flag: bool = None
    reconstruction_error: float = None
    gru_score: float = None


# -----------------------------------
# Health Check
# -----------------------------------
@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "engine-anomaly-detection",
        "timestamp": datetime.utcnow()
    }


# -----------------------------------
# Static Threshold Detection (Baseline)
# -----------------------------------
@router.post("/detect/static", response_model=DetectionResponse)
def detect_static(data: EngineSensorInput):
    try:
        result = anomaly_service.static_detect(data.engine_temperature)

        return DetectionResponse(
            timestamp=data.timestamp,
            temperature=data.engine_temperature,
            is_anomaly=result["is_anomaly"],
            confidence=result["confidence"],
            method="static_threshold"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------
# VAE + GRU Advanced Detection
# -----------------------------------
@router.post("/detect/advanced", response_model=DetectionResponse)
def detect_advanced(data: EngineSensorInput):
    try:
        sequence = np.array([[data.engine_temperature]])

        result = anomaly_service.advanced_detect(sequence)

        return DetectionResponse(
            timestamp=data.timestamp,
            temperature=data.engine_temperature,
            is_anomaly=result["is_anomaly"],
            confidence=result["confidence"],
            reconstruction_error=result.get("reconstruction_error"),
            gru_score=result.get("gru_score"),
            method="vae_gru"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------
# Hybrid Detection (Main Production Logic)
# -----------------------------------
@router.post("/detect/hybrid", response_model=DetectionResponse)
def detect_hybrid(data: EngineSensorInput):
    """
    Final production endpoint:
    Combines Static + VAE + GRU
    Optimized to reduce false negatives
    """

    try:
        sequence = np.array([[data.engine_temperature]])

        result = anomaly_service.hybrid_detect(
            temperature=data.engine_temperature,
            sequence=sequence
        )

        return DetectionResponse(
            timestamp=data.timestamp,
            temperature=data.engine_temperature,
            is_anomaly=result["is_anomaly"],
            confidence=result["confidence"],
            static_flag=result.get("static_flag"),
            vae_flag=result.get("vae_flag"),
            gru_flag=result.get("gru_flag"),
            reconstruction_error=result.get("reconstruction_error"),
            gru_score=result.get("gru_score"),
            method="hybrid_vae_gru"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------
# Real-time Streaming Simulation Endpoint
# -----------------------------------
@router.post("/detect/stream")
def detect_stream(data: list[EngineSensorInput]):
    """
    Simulates real-time IoT stream processing
    """

    try:
        results = []

        for point in data:
            sequence = np.array([[point.engine_temperature]])

            result = anomaly_service.hybrid_detect(
                temperature=point.engine_temperature,
                sequence=sequence
            )

            results.append({
                "timestamp": point.timestamp,
                "temperature": point.engine_temperature,
                "is_anomaly": result["is_anomaly"],
                "confidence": result["confidence"]
            })

        anomaly_count = sum(r["is_anomaly"] for r in results)

        return {
            "total_points": len(results),
            "anomalies_detected": anomaly_count,
            "anomaly_rate": round(anomaly_count / len(results), 4) if results else 0,
            "stream_results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------
# Explainability Endpoint
# -----------------------------------
@router.post("/detect/explain")
def detect_with_explanation(data: EngineSensorInput):
    """
    Returns anomaly + human-readable explanation
    """

    try:
        sequence = np.array([[data.engine_temperature]])

        result = anomaly_service.hybrid_detect(
            temperature=data.engine_temperature,
            sequence=sequence
        )

        explanation = []

        if result.get("static_flag"):
            explanation.append("Static threshold exceeded (possible spike).")

        if result.get("vae_flag"):
            explanation.append("High reconstruction error (pattern deviation).")

        if result.get("gru_flag"):
            explanation.append("Temporal drift detected in sequence behavior.")

        if not explanation:
            explanation.append("Normal engine behavior detected.")

        return {
            "timestamp": data.timestamp,
            "temperature": data.engine_temperature,
            "is_anomaly": result["is_anomaly"],
            "confidence": result["confidence"],
            "explanation": " | ".join(explanation),
            "reconstruction_error": result.get("reconstruction_error"),
            "gru_score": result.get("gru_score")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
