from __future__ import annotations
from typing import List, Tuple, Dict


Operation = Tuple[Tuple[int, int], Tuple[int, int]]
# ((job_id, op_index), (machine_id, duration))


class Scheduler:
    """Event-based simulator for regular Job-Shop & Dynamic rescheduling."""
    __slots__ = ("num_machines", "_cache")

    def __init__(self, num_machines: int, use_cache: bool = False) -> None:
        self.num_machines: int = num_machines
        self._cache: Dict[Tuple[int, ...], int] | None = {} if use_cache else None


    def calculate_makespan(self, chromosome: List[Operation]) -> int:
        """
        Parameters
        ----------
        chromosome : list[Operation]
            List produced by GA.decode(...):
            [((job_id, op_idx), (machine, proc_time)), ...]
        """
        if self._cache is not None:                       # optional memoisation
            key = tuple(op[0] for op in chromosome)       # hashable job/order sig
            if key in self._cache:
                return self._cache[key]

        m_ready = [0] * self.num_machines                 # machine availability
        j_ready: Dict[int, int] = {}                      # last finish per job

        for ((jid, _), (mach, dur)) in chromosome:
            start = max(m_ready[mach], j_ready.get(jid, 0))
            finish = start + dur
            m_ready[mach] = finish
            j_ready[jid] = finish                         # <-- correct index!

        cmax = max(m_ready)

        if self._cache is not None:
            self._cache[key] = cmax
        return cmax
