from abc import ABC
from planners.in_season import InSeasonPlanner
from planners.full_season import FullSeasonPlanner


class Planner(ABC):
    """
    Abstract class for planners.
    This represents a combination of steps for outputting different types of plans.
    """

    def run(self):
       pass


class PlannerFactory(ABC):
    def __init__(self):
        self.factories = {
            "in_season": InSeasonPlanner,
            "full_season": FullSeasonPlanner,
        }

    def get_planner(self, planner_type):
        return self.factories[planner_type]()