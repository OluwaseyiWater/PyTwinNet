from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, Tuple, Any
import numpy as np
import math
from typing import Dict

def rbf_kernel(X1: np.ndarray, X2: np.ndarray, lengthscale: float, variance: float) -> np.ndarray:
    D = ((X1[:, None, :] - X2[None, :, :]) ** 2).sum(axis=2)
    return variance * np.exp(-0.5 * D / (lengthscale ** 2 + 1e-12))

@dataclass
class SimpleBayesOpt:
    """Tiny Bayesian Optimization (RBF GP + Expected Improvement)."""
    bounds: List[Tuple[float, float]]
    init_points: int = 8
    iters: int = 32
    lengthscale: float = 0.5
    variance: float = 1.0
    noise: float = 1e-6
    seed: int = 0

    X: List[List[float]] = field(default_factory=list)
    y: List[float] = field(default_factory=list)

    def ask(self, n: int = 1) -> List[List[float]]:
        rng = np.random.default_rng(self.seed + len(self.X))
        pts = []
        for _ in range(n):
            x = [rng.uniform(a, b) for (a, b) in self.bounds]
            pts.append(x)
        return pts

    def tell(self, X: List[List[float]], y: List[float]) -> None:
        self.X.extend(X); self.y.extend(y)

    def _posterior(self, Xs: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if not self.X:
            mu = np.zeros((Xs.shape[0],)); s2 = np.ones_like(mu)
            return mu, s2
        X = np.array(self.X, float); y = np.array(self.y, float)
        K = rbf_kernel(X, X, self.lengthscale, self.variance) + self.noise * np.eye(X.shape[0])
        Ks = rbf_kernel(X, Xs, self.lengthscale, self.variance)
        Kss = rbf_kernel(Xs, Xs, self.lengthscale, self.variance) + self.noise * np.eye(Xs.shape[0])
        L = np.linalg.cholesky(K)
        alpha = np.linalg.solve(L.T, np.linalg.solve(L, y))
        mu = Ks.T @ alpha
        v = np.linalg.solve(L, Ks)
        s2 = np.maximum(np.diag(Kss) - (v * v).sum(axis=0), 1e-12)
        return mu, s2

    def _ei(self, mu: np.ndarray, s2: np.ndarray, y_best: float) -> np.ndarray:
            # Vectorized Expected Improvement
            s = np.sqrt(s2)
            z = (mu - y_best) / (s + 1e-12)
            erf = np.vectorize(math.erf)
            Phi = 0.5 * (1.0 + erf(z / np.sqrt(2.0)))                  # CDF of N(0,1)
            phi = (1.0 / np.sqrt(2.0 * np.pi)) * np.exp(-0.5 * z * z)  # PDF of N(0,1)
            return (mu - y_best) * Phi + s * phi


    def suggest(self, n: int = 1) -> List[List[float]]:
        rng = np.random.default_rng(self.seed + 1234 + len(self.X))
        cand = rng.uniform(
            low=np.array([a for a, _ in self.bounds]),
            high=np.array([b for _, b in self.bounds]),
            size=(1024, len(self.bounds)),
        )
        mu, s2 = self._posterior(cand)
        y_best = max(self.y) if self.y else 0.0
        ei = self._ei(mu, s2, y_best)
        idx = np.argsort(-ei)[:n]
        return cand[idx].tolist()

    def run(self, evaluate: Callable[[List[float]], float]) -> Dict[str, Any]:
        X0 = self.ask(self.init_points)
        y0 = [evaluate(x) for x in X0]
        self.tell(X0, y0)
        for _ in range(self.iters):
            Xn = self.suggest(1)
            yn = [evaluate(x) for x in Xn]
            self.tell(Xn, yn)
        best_i = int(np.argmax(self.y))
        return {"best_x": self.X[best_i], "best_y": float(self.y[best_i]), "n_evals": len(self.y)}
