import numpy as np
from typing import Dict, List


class VAEGRUService:
    """
    Hybrid deep learning service combining:
    - VAE (Variational Autoencoder) → reconstruction error detection
    - GRU (Gated Recurrent Unit) → temporal anomaly detection

    Goal: Reduce false negatives in engine sensor anomaly detection
    """

    def __init__(self, vae_model=None, gru_model=None):
        # In real system, these would be loaded ML models
        self.vae_model = vae_model
        self.gru_model = gru_model

        # Tuned thresholds (important for FN reduction)
        self.reconstruction_threshold = 0.12
        self.gru_threshold = 0.65

    # -----------------------------------
    # VAE-based anomaly detection
    # -----------------------------------
    def vae_detect(self, sequence: np.ndarray) -> Dict:
        """
        Detects anomalies based on reconstruction error
        """

        # Simulated reconstruction (replace with model inference)
        reconstructed = sequence * np.random.normal(1.0, 0.02, sequence.shape)

        reconstruction_error = np.mean((sequence - reconstructed) ** 2)

        is_anomaly = reconstruction_error > self.reconstruction_threshold

        confidence = min(reconstruction_error / self.reconstruction_threshold, 1.0)

        return {
            "is_anomaly": bool(is_anomaly),
            "confidence": float(confidence),
            "reconstruction_error": float(reconstruction_error),
            "method": "vae"
        }

    # -----------------------------------
    # GRU-based anomaly detection
    # -----------------------------------
    def gru_detect(self, sequence: np.ndarray) -> Dict:
        """
        Detects temporal anomalies using sequence behavior
        """

        # Simulated GRU score (replace with model.predict)
        trend = np.mean(np.diff(sequence.flatten(), prepend=sequence[0]))
        anomaly_score = abs(trend) + np.random.normal(0, 0.05)

        is_anomaly = anomaly_score > self.gru_threshold

        confidence = min(anomaly_score, 1.0)

        return {
            "is_anomaly": bool(is_anomaly),
            "confidence": float(confidence),
            "gru_score": float(anomaly_score),
            "method": "gru"
        }

    # -----------------------------------
    # Combined VAE + GRU detection
    # -----------------------------------
    def detect(self, sequence: np.ndarray) -> Dict:
        """
        Fusion model combining reconstruction + temporal signals
        """

        vae_result = self.vae_detect(sequence)
        gru_result = self.gru_detect(sequence)

        # 🔥 Fusion logic (false-negative reduction priority)
        is_anomaly = (
            vae_result["is_anomaly"]
            or gru_result["is_anomaly"]
        )

        # Confidence fusion (take strongest signal)
        confidence = max(
            vae_result["confidence"],
            gru_result["confidence"]
        )

        return {
            "is_anomaly": bool(is_anomaly),
            "confidence": float(confidence),
            "reconstruction_error": vae_result["reconstruction_error"],
            "gru_score": gru_result["gru_score"],
            "vae_flag": vae_result["is_anomaly"],
            "gru_flag": gru_result["is_anomaly"],
            "method": "vae_gru_fusion"
        }

    # -----------------------------------
    # Streaming inference (real-time use case)
    # -----------------------------------
    def stream_detect(self, stream: List[float], window_size: int = 10) -> Dict:
        """
        Simulates real-time sensor stream processing
        """

        results = []

        for i in range(len(stream)):
            window = stream[max(0, i - window_size + 1): i + 1]

            sequence = np.array(window).reshape(-1, 1)

            result = self.detect(sequence)

            results.append({
                "value": stream[i],
                "is_anomaly": result["is_anomaly"],
                "confidence": result["confidence"]
            })

        anomaly_count = sum(r["is_anomaly"] for r in results)

        return {
            "total_points": len(stream),
            "anomalies_detected": anomaly_count,
            "anomaly_rate": round(anomaly_count / len(stream), 4) if stream else 0,
            "results": results
        }

    # -----------------------------------
    # Evaluation utility
    # -----------------------------------
    def evaluate(self, data: List[float]) -> Dict:
        """
        Compare VAE vs GRU vs fused model performance
        """

        vae_count = 0
        gru_count = 0
        fusion_count = 0

        results = []

        for i in range(len(data)):
            window = data[max(0, i - 10): i + 1]
            sequence = np.array(window).reshape(-1, 1)

            vae = self.vae_detect(sequence)
            gru = self.gru_detect(sequence)
            fusion = self.detect(sequence)

            vae_count += int(vae["is_anomaly"])
            gru_count += int(gru["is_anomaly"])
            fusion_count += int(fusion["is_anomaly"])

            results.append({
                "value": data[i],
                "vae": vae["is_anomaly"],
                "gru": gru["is_anomaly"],
                "fusion": fusion["is_anomaly"]
            })

        return {
            "total_points": len(data),
            "vae_anomalies": vae_count,
            "gru_anomalies": gru_count,
            "fusion_anomalies": fusion_count,
            "false_negative_reduction_proxy": round(
                (gru_count - fusion_count) / max(gru_count, 1) * 100,
                2
            ),
            "results": results
        }


# Singleton instance for backend usage
vae_gru_service = VAEGRUService()
