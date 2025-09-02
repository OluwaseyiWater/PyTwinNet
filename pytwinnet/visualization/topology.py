
from __future__ import annotations
from typing import Optional
import matplotlib.pyplot as plt
from ..core.network import Network

def plot_topology(network: Network, ax: Optional[plt.Axes] = None) -> plt.Axes:
    if ax is None:
        fig, ax = plt.subplots()
    for node in network:
        x, y, z = node.position
        role = str(node.metadata.get("role", "")).lower()
        if "gnb" in role or "bs" in role:
            ax.scatter([x], [y], marker="^", s=80)
        else:
            ax.scatter([x], [y], marker="o", s=50)
        ax.text(x, y, node.node_id, fontsize=8)
    ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)"); ax.set_title("PyTwinNet Topology")
    return ax
