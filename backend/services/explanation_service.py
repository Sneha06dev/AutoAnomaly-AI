from typing import Dict, List


class ExplanationService:
    """
    Converts model outputs into human-readable explanations.

    Works with:
    - Static threshold service
    - Adaptive threshold service
    - VAE reconstruction errors
    - GRU temporal scores
    - Fusion decisions

    Goal:
    🔥 Improve interpretability and reduce "black-box" perception
    """

    # -----------------------------------
    # Single decision explanation
    # -----------------------------------
    def explain_single(self, result: Dict) -> str:
        """
        Explain one detection result in simple language
        """

        reasons: List[str] = []

        if result.get("static_flag"):
            reasons.append(
                "Engine temperature exceeded safe static threshold."
            )

        if result.get("adaptive_flag"):
            reasons.append(
                "Temperature deviates from recent operating baseline (adaptive anomaly)."
            )

        if result.get("vae_flag"):
            reasons.append(
                "Reconstruction error is high, indicating unusual engine behavior pattern."
            )

        if result.get("gru_flag"):
            reasons.append(
                "Temporal pattern inconsistency detected in sensor sequence (GRU signal)."
            )

        if not reasons:
            return "Engine behavior is normal. No anomalies detected across all models."

        return " | ".join(reasons)

    # -----------------------------------
    # Fusion explanation (main system output)
    # -----------------------------------
    def explain_fusion(self, fusion_result: Dict) -> str:
        """
        Explain final fused decision
        """

        reasons: List[str] = []

        score = fusion_result.get("fused_score", 0)

        # Score-based interpretation
        if score > 0.8:
            reasons.append("Very high anomaly confidence across multiple models.")
        elif score > 0.5:
            reasons.append("Moderate anomaly signal detected.")
        else:
            reasons.append("Low anomaly score (near-normal behavior).")

        # Model agreement analysis
        agreement = fusion_result.get("model_agreement", 0)

        if agreement >= 0.75:
            reasons.append("Strong agreement between models.")
        elif agreement >= 0.5:
            reasons.append("Partial agreement between models.")
        else:
            reasons.append("Low agreement — possible ambiguous pattern.")

        # Component-level reasoning
        if fusion_result.get("static_flag"):
            reasons.append("Static threshold triggered (safety rule breach).")

        if fusion_result.get("adaptive_flag"):
            reasons.append("Adaptive threshold deviation detected.")

        if fusion_result.get("vae_flag"):
            reasons.append("VAE detected reconstruction anomaly.")

        if fusion_result.get("gru_flag"):
            reasons.append("GRU detected temporal anomaly pattern.")

        return " | ".join(reasons)

    # -----------------------------------
    # Failure analysis (important for FN reduction story)
    # -----------------------------------
    def analyze_failure_mode(self, result: Dict) -> Dict:
        """
        Identifies why anomaly was missed or detected.

        Useful for:
        - false negative analysis
        - model improvement justification
        """

        missed_by = []

        if not result.get("static_flag"):
            missed_by.append("static_threshold")

        if not result.get("adaptive_flag"):
            missed_by.append("adaptive_threshold")

        if not result.get("vae_flag"):
            missed_by.append("vae_model")

        if not result.get("gru_flag"):
            missed_by.append("gru_model")

        return {
            "missed_by": missed_by,
            "coverage_score": 1.0 - (len(missed_by) / 4.0),
            "risk_level": (
                "high" if len(missed_by) >= 3
                else "medium" if len(missed_by) == 2
                else "low"
            )
        }

    # -----------------------------------
    # Batch explanation (for dashboards/reports)
    # -----------------------------------
    def batch_explain(self, results: List[Dict]) -> Dict:
        """
        Summarizes explanation across dataset
        """

        total = len(results)
        anomaly_count = 0
        high_confidence_count = 0

        for r in results:
            if r.get("is_anomaly"):
                anomaly_count += 1

            if r.get("confidence", 0) > 0.75:
                high_confidence_count += 1

        return {
            "total_samples": total,
            "anomalies_detected": anomaly_count,
            "high_confidence_anomalies": high_confidence_count,
            "anomaly_rate": round(anomaly_count / total, 4) if total else 0,
            "high_confidence_rate": round(high_confidence_count / total, 4) if total else 0
        }


# Singleton instance
explanation_service = ExplanationService()
