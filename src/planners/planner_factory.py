from abc import ABC
from planners.planner import Planner
from planners.in_season import InSeasonPlanner
from planners.full_season import FullSeasonPlanner
from planners.reset import ResetPlanner


class PlannerFactory(ABC):
    def __init__(self):
        self.factories = {
            "in_season": InSeasonPlanner,
            "full_season": FullSeasonPlanner,
            "reset": ResetPlanner
        }

    def get_planner(self, planner_type) -> Planner:
        return self.factories[planner_type]()