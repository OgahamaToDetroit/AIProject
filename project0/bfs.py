from pacman_module.game import Agent
from pacman_module.pacman import Directions
from collections import deque


class PacmanAgent(Agent):
    """
    A Pacman agent based on Breadth-First-Search.
    """

    def __init__(self, args):
        """
        Arguments:
        ----------
        - `args`: Namespace of arguments from command-line prompt.
        """
        super().__init__()
        self.args = args

    def get_action(self, state):
        """
        Given a pacman game state, returns a legal move.

        Arguments:
        ----------
        - `state`: the current game state. See FAQ and class
                   `pacman.GameState`.

        Return:
        -------
        - A legal move as defined in `game.Directions`.
        """

        # Fringe (Queue) to store states to visit.
        # Each item is a tuple: (state, actions_path)
        fringe = deque([(state, [])])

        # Set to store explored states to avoid cycles and redundant work.
        # A state is defined by (pacman_position, food_grid)
        explored = set()

        while fringe:
            # Get the oldest state from the fringe (FIFO)
            current_state, actions = fringe.popleft()

            # Create a hashable key for the current state
            key = (current_state.getPacmanPosition(), current_state.getFood())

            # If this state has been explored, skip it
            if key in explored:
                continue

            # Mark the state as explored
            explored.add(key)

            # If it's a win state, we found a solution
            if current_state.isWin():
                return actions[0] if actions else Directions.STOP

            # Expand the node: get all possible next states
            for next_state, action in current_state.generatePacmanSuccessors():
                new_actions = actions + [action]
                fringe.append((next_state, new_actions))

        # Should not be reached if a solution exists
        return Directions.STOP