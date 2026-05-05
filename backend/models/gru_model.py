import numpy as np
from typing import Tuple


class GRUModel:
    """
    GRU-based sequence anomaly detection model (mock implementation).

    Purpose:
    - Capture temporal dependencies in engine sensor data
    - Detect drift, spikes, and sequence irregularities
    - Output anomaly score based on sequence behavior

    In production:
    - Replace with PyTorch / TensorFlow GRU network
    """

    def __init__(self, hidden_dim: int = 16):
        self.hidden_dim = hidden_dim

        # Simulated learned weights (placeholders)
        self.W_h = np.random.normal(0, 0.1, hidden_dim)
        self.W_x = np.random.normal(0, 0.1, hidden_dim)

    # -----------------------------------
    # Hidden state initialization
    # -----------------------------------
    def init_hidden(self) -> np.ndarray:
        return np.zeros(self.hidden_dim)

    # -----------------------------------
    # GRU cell (simplified simulation)
    # -----------------------------------
    def gru_cell(self, x_t: float, h_prev: np.ndarray) -> np.ndarray:
        """
        Simulates GRU update step
        """

        # Reset and update gates (simplified)
        r_t = 1 / (1 + np.exp(-(x_t * 0.1)))
        z_t = 1 / (1 + np.exp(-(x_t * 0.05)))

        h_tilde = np.tanh(
            self.W_x * x_t + r_t * (self.W_h * h_prev)
        )

        h_t = (1 - z_t) * h_prev + z_t * h_tilde

        return h_t

    # -----------------------------------
    # Forward sequence pass
    # -----------------------------------
    def forward(self, sequence: np.ndarray) -> np.ndarray:
        """
        Processes full sequence through GRU
        """

        h = self.init_hidden()

        for x in sequence.flatten():
            h = self.gru_cell(x, h)

        return h

    # -----------------------------------
    # Sequence anomaly score
    # -----------------------------------
    def compute_anomaly_score(self, sequence: np.ndarray) -> float:
        """
        Detects anomalies based on temporal instability
        """

        h_states = []
        h = self.init_hidden()

        for x in sequence.flatten():
            prev_h = h.copy()
            h = self.gru_cell(x, h)

            # Track instability between hidden states
            instability = np.mean(np.abs(h - prev_h))
            h_states.append(instability)

        # Final anomaly score = volatility of hidden state changes
        anomaly_score = np.mean(h_states)

        return float(anomaly_score)

    # -----------------------------------
    # Prediction interface
    # -----------------------------------
    def predict(self, sequence: np.ndarray, threshold: float = 0.65) -> dict:
        """
        Returns anomaly prediction from GRU model
        """

        score = self.compute_anomaly_score(sequence)

        is_anomaly = score > threshold

        confidence = min(score / threshold, 1.0)

        return {
            "is_anomaly": bool(is_anomaly),
            "gru_score": float(score),
            "confidence": float(confidence),
            "method": "gru_model"
        }


# Singleton instance for backend usage
gru_model = GRUModel()
