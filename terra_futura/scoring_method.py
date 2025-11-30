from __future__ import annotations

from typing import List, Optional
from collections import Counter
from .simple_types import Resource, Points

class ScoringMethod:

    def __init__(self, resources: List[Resource], points_per_combination: Points):

        self.resources: List[Resource] = resources
        self.points_per_combination: Points = points_per_combination
        self.calculated_total: Optional[Points] = None
        self.selected: bool = False

    def select_this_method_and_calculate(self, available_resources: List[Resource]) -> Points:
        self.selected = True

        required = Counter(self.resources)

        available = Counter(r for r in available_resources
                            if r not in [Resource.MONEY, Resource.POLLUTION])

        if not required:
            num_complete_sets = 0
        else:

            num_complete_sets = min(
                available.get(resource, 0) // required[resource]
                for resource in required
            )

        total_points = Points(num_complete_sets * self.points_per_combination.value)
        self.calculated_total = total_points

        return total_points

    def state(self) -> str:

        resource_names = [r.name for r in self.resources]
        total_str = str(self.calculated_total) if self.calculated_total else "Not calculated"

        return (f"ScoringMethod["
                f"resources={resource_names}, "
                f"points={self.points_per_combination}, "
                f"selected={self.selected}, "
                f"total={total_str}]")
