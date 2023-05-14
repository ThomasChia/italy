from abc import ABC


class Planner(ABC):
    """
    Abstract class for planners.
    This represents a combination of steps for outputting different types of plans.
    """

    def run(self, debug=False):
       pass