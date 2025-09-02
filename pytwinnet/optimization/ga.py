from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Any
import random
from ..core.digital_twin import DigitalTwin
from .objective import Objective

@dataclass
class ChannelAllocationGA:
    """Toy GA for assigning channels (ints) to tx nodes to maximize objective."""
    channels: List[int]
    population: int = 30
    generations: int = 20
    mutation_p: float = 0.1
    seed: int = 0

    def optimize(self, twin: DigitalTwin, node_ids: List[str], objective: Objective) -> Dict[str, Any]:
        rng = random.Random(self.seed)

        def random_ind():
            return {nid: rng.choice(self.channels) for nid in node_ids}

        def fitness(ind):
            sim = twin.snapshot()
            for nid, ch in ind.items():
                n = sim.network.get_node_by_id(nid)
                if n:
                    n.metadata["channel"] = ch
            return objective.evaluate(sim)

        pop = [random_ind() for _ in range(self.population)]
        scores = [fitness(ind) for ind in pop]
        for _ in range(self.generations):
            parents = []
            for _ in range(self.population):
                cand = rng.sample(range(self.population), k=min(3, self.population))
                best_i = max(cand, key=lambda i: scores[i])
                parents.append(pop[best_i])
            children = []
            for i in range(0, self.population, 2):
                p1 = parents[i]
                p2 = parents[min(i + 1, self.population - 1)]
                keys = list(p1.keys())
                cut = rng.randrange(1, len(keys)) if len(keys) > 1 else 1
                c = {k: (p1[k] if j < cut else p2[k]) for j, k in enumerate(keys)}
                children.append(c)
            for c in children:
                if rng.random() < self.mutation_p:
                    k = rng.choice(list(c.keys()))
                    c[k] = rng.choice(self.channels)
            pop = children
            scores = [fitness(ind) for ind in pop]
        best_idx = max(range(self.population), key=lambda i: scores[i])
        return {"best_allocation": pop[best_idx], "best_score": scores[best_idx]}
