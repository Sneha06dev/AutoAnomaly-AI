import numpy as np
from typing import Tuple


class VAEModel:
    """
    Variational Autoencoder (VAE) mock implementation for engine sensor anomaly detection.

    Purpose:
    - Reconstruct engine temperature sequences
    - Compute reconstruction error
    - Detect anomalies when reconstruction deviates significantly

    In production:
    - Replace with trained PyTorch / TensorFlow model
    """

    def __init__(self, latent_dim: int = 8):
        self.latent_dim = latent_dim

        # Simulated learned parameters (placeholder for real weights)
        self.weights_mean = np.random.normal(0, 0.1, latent_dim)
        self.weights_var = np.random.normal(1, 0.05, latent_dim)

    # -----------------------------------
    # Encoder (simulated)
    # -----------------------------------
    def encode(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Encodes input sequence into latent space (mean, log variance)
        """

        z_mean = np.mean(x, axis=0) * self.weights_mean[0]
        z_log_var = np.log(np.var(x + 1e-6)) * self.weights_var[0]

        return z_mean, z_log_var

    # -----------------------------------
    # Reparameterization trick (simulated)
    # -----------------------------------
    def reparameterize(self, z_mean: np.ndarray, z_log_var: np.ndarray) -> np.ndarray:
        """
        Sample latent vector from learned distribution
        """

        epsilon = np.random.normal(0, 1, size=z_mean.shape)

        z = z_mean + np.exp(0.5 * z_log_var) * epsilon

        return z

    # -----------------------------------
    # Decoder (simulated reconstruction)
    # -----------------------------------
    def decode(self, z: np.ndarray, original_shape: Tuple[int, ...]) -> np.ndarray:
        """
        Reconstruct input from latent space
        """

        reconstruction = np.ones(original_shape) * np.mean(z)

        # Add slight noise to simulate imperfect reconstruction
        noise = np.random.normal(0, 0.02, original_shape)

        return reconstruction + noise

    # -----------------------------------
    # Full forward pass
    # -----------------------------------
    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Full VAE pipeline:
        encode → sample → decode
        """

        z_mean, z_log_var = self.encode(x)
        z = self.reparameterize(z_mean, z_log_var)
        reconstructed = self.decode(z, x.shape)

        return reconstructed

    # -----------------------------------
    # Reconstruction + anomaly scoring
    # -----------------------------------
    def reconstruct(self, x: np.ndarray) -> np.ndarray:
        """
        Returns reconstructed input
        """

        return self.forward(x)

    def compute_reconstruction_error(self, x: np.ndarray) -> float:
        """
        Computes anomaly score based on reconstruction error
        """

        reconstructed = self.reconstruct(x)

        error = np.mean((x - reconstructed) ** 2)

        return float(error)

    # -----------------------------------
    # Anomaly detection
    # -----------------------------------
    def predict(self, x: np.ndarray, threshold: float = 0.12) -> dict:
        """
        Returns anomaly decision + score
        """

        error = self.compute_reconstruction_error(x)

        is_anomaly = error > threshold

        confidence = min(error / threshold, 1.0)

        return {
            "is_anomaly": bool(is_anomaly),
            "reconstruction_error": float(error),
            "confidence": float(confidence),
            "method": "vae_model"
        }


# Singleton instance for backend usage
vae_model = VAEModel()
