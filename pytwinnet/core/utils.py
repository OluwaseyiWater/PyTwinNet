
from __future__ import annotations
from typing import List
from .network import Network

def list_gnbs(network: Network) -> List[str]:
    out = []
    for n in network:
        role = str(n.metadata.get("role", "")).lower()
        if "gnb" in role or "bs" in role:
            out.append(n.node_id)
    return out
