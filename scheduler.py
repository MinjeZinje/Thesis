from __future__ import annotations
from typing import Dict, List, Tuple, Optional

# ((job-id, op-idx), (machine, duration))
Operation = Tuple[Tuple[int, int], Tuple[int, int]]

class Scheduler:
    """Event-based JSSP simulator with optional machine‐state modifiers."""
    __slots__ = ("num_machines", "_cache")

    def __init__(self, num_machines: int, use_cache: bool = False) -> None:
        self.num_machines = num_machines
        self._cache: Optional[Dict[Tuple[int, ...], int]] = {} if use_cache else None

    def calculate_makespan(
        self,
        chromosome: List[Operation],
        machine_status: Optional[Dict[int, str | float]] = None,
        noise_factor: float = 1.2,          # default multiplier for “noisy” machines
        breakdown_penalty: int = 10**6      # large delay for “broken” machines
    ) -> int:
        """
        machine_status[m] can be:
          • "broken"  → task on machine m incurs breakdown_penalty extra time
          • "noisy"   → task duration is multiplied by noise_factor
          • a float   → task duration is multiplied by that float (custom noise)
        """
        if self._cache is not None:
            key = tuple(op[0] for op in chromosome)
            hit = self._cache.get(key)
            if hit is not None:
                return hit

        m_ready = [0] * self.num_machines
        j_ready: Dict[int, int] = {}

        for (job_id, _), (mach, dur) in chromosome:
            status = (machine_status or {}).get(mach)

            if status == "broken":
                dur += breakdown_penalty
            elif status == "noisy":
                dur = int(dur * noise_factor)
            elif isinstance(status, (int, float)):      # custom factor
                dur = int(dur * status)

            start  = max(m_ready[mach], j_ready.get(job_id, 0))
            finish = start + dur
            m_ready[mach] = finish
            j_ready[job_id] = finish

        cmax = max(m_ready)
        if self._cache is not None:
            self._cache[key] = cmax
        return cmax
