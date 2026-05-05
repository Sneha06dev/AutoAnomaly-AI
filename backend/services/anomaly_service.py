import numpy as np
from typing import Dict, List
from datetime import datetime

# Simulated model loaders (replace with actual model loading)
from services.model_loader import load_vae_model, load_gru_model


class AnomalyService:
    """
    Core service handling anomaly detection logic.
    Combines:
    - Static Threshold (baseline)
    - VAE Reconstruction Error
    - GRU Temporal Pattern Detection
    """

    def __init__(self):
        self.vae_model = load_vae_model()
        self.gru_model = load_gru_model()

        # Thresholds (tuned to reduce false negatives)
        self.static_threshold = 95.0
        self.reconstruction_threshold = 0.12
        self.gru_threshold = 0.65

    # -----------------------------------
    # Static Threshold Detection
    # -----------------------------------
    def static_detect(self, temperature: float) -> Dict:
        is_anomaly = temperature > self.static_threshold

        confidence = min(abs(temperature - self.static_threshold) / 10, 1.0)

        return {
            "is_anomaly": is_anomaly,
            "confidence": confidence,
            "method": "static_threshold"
        }

    # -----------------------------------
    # VAE Detection (Pattern Reconstruction)
    # -----------------------------------
    def vae_detect(self, sequence: np.ndarray) -> Dict:
        reconstructed = self.vae_model.reconstruct(sequence)

        error = np.mean((sequence - reconstructed) ** 2)

        is_anomaly = error > self.reconstruction_threshold

        confidence = min(error / self.reconstruction_threshold, 1.0)

        return {
            "is_anomaly": is_anomaly,
            "confidence": confidence,
            "reconstruction_error": float(error),
            "method": "vae"
        }

    # -----------------------------------
    # GRU Detection (Temporal Drift)
    # -----------------------------------
    def gru_detect(self, sequence: np.ndarray) -> Dict:
        anomaly_score = self.gru_model.predict(sequence)

        is_anomaly = anomaly_score > self.gru_threshold

        confidence = min(anomaly_score, 1.0)

        return {
            "is_anomaly": is_anomaly,
            "confidence": confidence,
            "gru_score": float(anomaly_score),
            "method": "gru"
        }

    # -----------------------------------
    # Combined VAE + GRU Detection
    # -----------------------------------
    def advanced_detect(self, sequence: np.ndarray) -> Dict:
        vae_result = self.vae_detect(sequence)
        gru_result = self.gru_detect(sequence)

        # 🔥 Key Improvement: Soft OR fusion
        # Helps reduce false negatives
        is_anomaly = vae_result["is_anomaly"] or gru_result["is_anomaly"]

        # Weighted confidence fusion
        confidence = max(vae_result["confidence"], gru_result["confidence"])

        return {
            "is_anomaly": is_anomaly,
            "confidence": confidence,
            "reconstruction_error": vae_result["reconstruction_error"],
            "gru_score": gru_result["gru_score"],
            "method": "vae_gru_fusion"
        }

    # -----------------------------------
    # Hybrid Detection (FINAL PIPELINE)
    # -----------------------------------
    def hybrid_detect(self, temperature: float, sequence: np.ndarray) -> Dict:
        """
        Final production pipeline:
        Static + VAE + GRU

        Goal:
        Reduce false negatives by catching:
        - sudden spikes (static)
        - subtle deviations (VAE)
        - temporal drift (GRU)
        """

        static_result = self.static_detect(temperature)
        advanced_result = self.advanced_detect(sequence)

        # 🔥 Critical Logic: Aggressive anomaly capture
        final_flag = (
            static_result["is_anomaly"]
            or advanced_result["is_anomaly"]
        )

        # Confidence boosting for edge anomalies
        final_confidence = max(
            static_result["confidence"],
            advanced_result["confidence"]
        )

        return {
            "is_anomaly": final_flag,
            "confidence": final_confidence,
            "static_flag": static_result["is_anomaly"],
            "vae_flag": advanced_result["reconstruction_error"] > self.reconstruction_threshold,
            "gru_flag": advanced_result["gru_score"] > self.gru_threshold,
            "reconstruction_error": advanced_result["reconstruction_error"],
            "gru_score": advanced_result["gru_score"],
            "method": "hybrid_pipeline"
        }

    # -----------------------------------
    # Batch Evaluation (for metrics)
    # -----------------------------------
    def batch_detect(self, temperatures: List[float]) -> Dict:
        """
        Used to compute:
        - False Negatives
        - Model comparison
        """

        results = []

        for temp in temperatures:
            sequence = np.array([[temp]])

            static_res = self.static_detect(temp)
            advanced_res = self.advanced_detect(sequence)
            hybrid_res = self.hybrid_detect(temp, sequence)

            results.append({
                "temperature": temp,
                "static": static_res["is_anomaly"],
                "advanced": advanced_res["is_anomaly"],
                "hybrid": hybrid_res["is_anomaly"]
            })

        return {
            "total_points": len(results),
            "results": results
        }


# Singleton instance (used across routes)
anomaly_service = AnomalyService()
