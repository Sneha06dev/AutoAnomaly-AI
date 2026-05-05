import numpy as np
from typing import List, Dict


class GraphUtils:
    """
    Utility class for preparing data for visualization
    in anomaly detection system.

    Used for:
    - Comparing models (static vs VAE vs GRU vs hybrid)
    - Visualizing anomaly trends over time
    - Generating dataset summaries for frontend charts
    """

    # -----------------------------------
    # Convert detection results to time-series format
    # -----------------------------------
    def prepare_timeseries(self, results: List[Dict]) -> Dict:
        """
        Formats detection output for line chart visualization
        """

        timestamps = []
        values = []
        anomalies = []
        confidence = []

        for r in results:
            timestamps.append(str(r.get("timestamp", "")))
            values.append(r.get("temperature", r.get("value", 0)))
            anomalies.append(int(r.get("is_anomaly", False)))
            confidence.append(r.get("confidence", 0))

        return {
            "timestamps": timestamps,
            "values": values,
            "anomalies": anomalies,
            "confidence": confidence
        }

    # -----------------------------------
    # Model comparison data
    # -----------------------------------
    def compare_models(self, results: List[Dict]) -> Dict:
        """
        Generates comparison metrics for visualization
        (static vs adaptive vs VAE vs GRU vs hybrid)
        """

        static_count = sum(r.get("static", False) for r in results)
        adaptive_count = sum(r.get("adaptive", False) for r in results)
        vae_count = sum(r.get("vae", False) for r in results)
        gru_count = sum(r.get("gru", False) for r in results)
        hybrid_count = sum(r.get("hybrid", False) for r in results)

        return {
            "models": ["Static", "Adaptive", "VAE", "GRU", "Hybrid"],
            "anomalies": [
                static_count,
                adaptive_count,
                vae_count,
                gru_count,
                hybrid_count
            ]
        }

    # -----------------------------------
    # False negative proxy analysis
    # -----------------------------------
    def false_negative_analysis(self, results: List[Dict]) -> Dict:
        """
        Estimates false negative reduction trends
        """

        total = len(results)

        static_missed = 0
        adaptive_missed = 0
        vae_missed = 0
        gru_missed = 0

        for r in results:
            is_anomaly = r.get("is_anomaly", False)

            if is_anomaly:
                if not r.get("static", False):
                    static_missed += 1
                if not r.get("adaptive", False):
                    adaptive_missed += 1
                if not r.get("vae", False):
                    vae_missed += 1
                if not r.get("gru", False):
                    gru_missed += 1

        return {
            "models": ["Static", "Adaptive", "VAE", "GRU"],
            "false_negatives": [
                static_missed,
                adaptive_missed,
                vae_missed,
                gru_missed
            ],
            "reduction_vs_static": round(
                (static_missed - gru_missed) / max(static_missed, 1) * 100,
                2
            )
        }

    # -----------------------------------
    # Rolling anomaly rate (trend analysis)
    # -----------------------------------
    def rolling_anomaly_rate(self, results: List[Dict], window: int = 10) -> List[float]:
        """
        Computes anomaly rate over sliding window
        Useful for trend graphs
        """

        rates = []

        for i in range(len(results)):
            window_data = results[max(0, i - window + 1): i + 1]

            if len(window_data) == 0:
                rates.append(0)
                continue

            anomaly_count = sum(r.get("is_anomaly", False) for r in window_data)

            rates.append(anomaly_count / len(window_data))

        return rates

    # -----------------------------------
    # Summary statistics for dashboard
    # -----------------------------------
    def summary(self, results: List[Dict]) -> Dict:
        """
        Generates high-level system summary
        """

        total = len(results)
        anomalies = sum(r.get("is_anomaly", False) for r in results)

        confidences = [r.get("confidence", 0) for r in results]

        return {
            "total_samples": total,
            "anomalies_detected": anomalies,
            "anomaly_rate": round(anomalies / total, 4) if total else 0,
            "avg_confidence": round(np.mean(confidences), 4) if confidences else 0,
            "max_confidence": max(confidences) if confidences else 0
        }


# Singleton instance
graph_utils = GraphUtils()
