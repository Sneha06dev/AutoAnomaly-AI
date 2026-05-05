from typing import Dict
import numpy as np


class FusionService:
    """
    Central decision fusion layer for anomaly detection.

    Combines outputs from:
    - Static Threshold Model
    - Adaptive Threshold Model
    - VAE Model
    - GRU Model

    Goal:
    🔥 Minimize false negatives in engine anomaly detection
    """

    def __init__(self):
        # Fusion weights (can be tuned during evaluation)
        self.weights = {
            "static": 0.2,
            "adaptive": 0.2,
            "vae": 0.3,
            "gru": 0.3
        }

        # Decision threshold for final anomaly score
        self.decision_threshold = 0.5

    # -----------------------------------
    # Score normalization helper
    # -----------------------------------
    def _normalize(self, value: float) -> float:
        """
        Ensures scores are in [0, 1]
        """
        return max(0.0, min(float(value), 1.0))

    # -----------------------------------
    # Fusion of multiple model outputs
    # -----------------------------------
    def fuse(self, static_result: Dict, adaptive_result: Dict,
             vae_result: Dict, gru_result: Dict) -> Dict:
        """
        Weighted fusion of multiple anomaly detectors
        """

        # Extract confidence scores
        static_score = self._normalize(static_result.get("confidence", 0))
        adaptive_score = self._normalize(adaptive_result.get("confidence", 0))
        vae_score = self._normalize(vae_result.get("confidence", 0))
        gru_score = self._normalize(gru_result.get("confidence", 0))

        # -----------------------------------
        # Weighted anomaly score
        # -----------------------------------
        fused_score = (
            static_score * self.weights["static"] +
            adaptive_score * self.weights["adaptive"] +
            vae_score * self.weights["vae"] +
            gru_score * self.weights["gru"]
        )

        # -----------------------------------
        # Hard safety override (critical FN reduction step)
        # -----------------------------------
        hard_override = (
            static_result.get("is_anomaly", False)
            or adaptive_result.get("is_anomaly", False)
        )

        # Final decision logic
        is_anomaly = fused_score > self.decision_threshold or hard_override

        # Confidence scaling (boost if multiple models agree)
        agreement_bonus = sum([
            static_result.get("is_anomaly", False),
            adaptive_result.get("is_anomaly", False),
            vae_result.get("is_anomaly", False),
            gru_result.get("is_anomaly", False),
        ]) / 4.0

        final_confidence = min(fused_score + (0.2 * agreement_bonus), 1.0)

        return {
            "is_anomaly": bool(is_anomaly),
            "fused_score": float(fused_score),
            "confidence": float(final_confidence),
            "model_agreement": float(agreement_bonus),
            "static_flag": static_result.get("is_anomaly"),
            "adaptive_flag": adaptive_result.get("is_anomaly"),
            "vae_flag": vae_result.get("is_anomaly"),
            "gru_flag": gru_result.get("is_anomaly"),
            "method": "fusion_v1"
        }

    # -----------------------------------
    # Explain fusion decision
    # -----------------------------------
    def explain(self, fusion_result: Dict) -> str:
        """
        Human-readable explanation for anomaly decision
        """

        reasons = []

        if fusion_result.get("static_flag"):
            reasons.append("Static threshold breach detected")

        if fusion_result.get("adaptive_flag"):
            reasons.append("Adaptive threshold deviation detected")

        if fusion_result.get("vae_flag"):
            reasons.append("Reconstruction anomaly detected (VAE)")

        if fusion_result.get("gru_flag"):
            reasons.append("Temporal pattern deviation detected (GRU)")

        if not reasons:
            reasons.append("All models indicate normal engine behavior")

        return " | ".join(reasons)

    # -----------------------------------
    # Batch fusion evaluation
    # -----------------------------------
    def batch_fuse(self, results_list: list) -> Dict:
        """
        Evaluate fusion performance across dataset
        """

        anomalies = 0
        scores = []

        for r in results_list:
            if r["is_anomaly"]:
                anomalies += 1
            scores.append(r.get("fused_score", 0))

        avg_score = np.mean(scores) if scores else 0

        return {
            "total_samples": len(results_list),
            "anomalies_detected": anomalies,
            "anomaly_rate": round(anomalies / len(results_list), 4) if results_list else 0,
            "average_fused_score": float(avg_score)
        }


# Singleton instance
fusion_service = FusionService()
