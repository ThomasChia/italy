from abc import ABC


class PlannerFactory(ABC):
    """
    Abstract class for planner factory.
    This represents a combination of steps for outputting different types of plans.
    """

    def run(self):
       pass