import numpy as np
from typing import Dict, List


class ThresholdService:
    """
    Enhanced threshold-based anomaly detection.

    Designed as a stronger baseline than naive fixed thresholds by:
    - Supporting dynamic thresholds (moving average + std dev)
    - Reducing false negatives using adaptive sensitivity
    """

    def __init__(self):
        # Base safety threshold (engine domain assumption)
        self.base_threshold = 95.0

        # Sensitivity controls (tunable)
        self.std_multiplier = 2.5  # higher = fewer false positives, more risk of FN
        self.adaptive_window = 20  # rolling window size

    # -----------------------------------
    # Static Threshold (Baseline)
    # -----------------------------------
    def static_threshold(self, temperature: float) -> Dict:
        """
        Simple rule-based detection
        """

        is_anomaly = temperature > self.base_threshold

        confidence = min(
            abs(temperature - self.base_threshold) / 10.0,
            1.0
        )

        return {
            "is_anomaly": is_anomaly,
            "confidence": confidence,
            "threshold": self.base_threshold,
            "method": "static"
        }

    # -----------------------------------
    # Adaptive Threshold (Improved Baseline)
    # -----------------------------------
    def adaptive_threshold(self, window: List[float]) -> Dict:
        """
        Uses rolling statistics:
        threshold = mean + k * std

        This reduces false negatives in drifting engine conditions.
        """

        if len(window) < 2:
            mean = np.mean(window)
            std = 0.0
        else:
            mean = np.mean(window)
            std = np.std(window)

        dynamic_threshold = mean + (self.std_multiplier * std)

        latest_value = window[-1]

        is_anomaly = latest_value > dynamic_threshold

        # Confidence based on deviation from adaptive boundary
        confidence = min(
            abs(latest_value - dynamic_threshold) / (std + 1e-6),
            1.0
        )

        return {
            "is_anomaly": is_anomaly,
            "confidence": confidence,
            "threshold": float(dynamic_threshold),
            "mean": float(mean),
            "std": float(std),
            "method": "adaptive"
        }

    # -----------------------------------
    # Hybrid Threshold Logic
    # -----------------------------------
    def hybrid_threshold(self, window: List[float]) -> Dict:
        """
        Combines:
        - Static safety threshold (hard rule)
        - Adaptive statistical threshold (context-aware)

        Goal: Reduce false negatives in edge cases
        """

        static_result = self.static_threshold(window[-1])
        adaptive_result = self.adaptive_threshold(window)

        # 🔥 Fusion strategy (FN reduction priority)
        is_anomaly = (
            static_result["is_anomaly"]
            or adaptive_result["is_anomaly"]
        )

        confidence = max(
            static_result["confidence"],
            adaptive_result["confidence"]
        )

        return {
            "is_anomaly": is_anomaly,
            "confidence": confidence,
            "static_flag": static_result["is_anomaly"],
            "adaptive_flag": adaptive_result["is_anomaly"],
            "static_threshold": static_result["threshold"],
            "adaptive_threshold": adaptive_result["threshold"],
            "method": "hybrid_threshold"
        }

    # -----------------------------------
    # Batch Evaluation (for analysis)
    # -----------------------------------
    def evaluate(self, data: List[float]) -> Dict:
        """
        Compare static vs adaptive vs hybrid performance
        """

        static_count = 0
        adaptive_count = 0
        hybrid_count = 0

        results = []

        for i in range(len(data)):
            window = data[max(0, i - self.adaptive_window): i + 1]

            static = self.static_threshold(data[i])
            adaptive = self.adaptive_threshold(window)
            hybrid = self.hybrid_threshold(window)

            static_count += int(static["is_anomaly"])
            adaptive_count += int(adaptive["is_anomaly"])
            hybrid_count += int(hybrid["is_anomaly"])

            results.append({
                "value": data[i],
                "static": static["is_anomaly"],
                "adaptive": adaptive["is_anomaly"],
                "hybrid": hybrid["is_anomaly"]
            })

        return {
            "total_points": len(data),
            "static_anomalies": static_count,
            "adaptive_anomalies": adaptive_count,
            "hybrid_anomalies": hybrid_count,
            "false_negative_reduction_proxy": round(
                (adaptive_count - hybrid_count) / max(adaptive_count, 1) * 100,
                2
            ),
            "results": results
        }


# Singleton instance
threshold_service = ThresholdService()
