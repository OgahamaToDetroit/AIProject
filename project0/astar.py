from pacman_module.game import Agent
from pacman_module.pacman import Directions
from pacman_module.util import PriorityQueue

def manhattan_distance(p1, p2):
    """Calculate Manhattan distance between two points."""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

class PacmanAgent(Agent):
    """
    Pacman agent using the A* search algorithm.
    """

    def __init__(self, args):
        super().__init__()
        self.args = args

    def get_action(self, state):
        """
        Returns the next action using A* search.
        """
        def heuristic(game_state):
            food = game_state.getFood().asList()
            pacman_pos = game_state.getPacmanPosition()
            if not food:
                return 0
            # Heuristic: max Manhattan distance to any food dot
            return max(manhattan_distance(pacman_pos, f) for f in food)

        fringe = PriorityQueue()
        # Each item: (game_state, actions_so_far, cost_so_far)
        fringe.push((state, [], 0), heuristic(state))
        visited = set()

        while not fringe.isEmpty():
            _, (current_state, actions, cost) = fringe.pop()
            key = (current_state.getPacmanPosition(), current_state.getFood())
            if key in visited:
                continue
            visited.add(key)

            if current_state.isWin():
                return actions[0] if actions else Directions.STOP

            for successor, action in current_state.generatePacmanSuccessors():
                if (successor.getPacmanPosition(), successor.getFood()) not in visited:
                    new_actions = actions + [action]
                    new_cost = cost + 1
                    priority = new_cost + heuristic(successor)
                    fringe.push((successor, new_actions, new_cost), priority)

        return Directions.STOP