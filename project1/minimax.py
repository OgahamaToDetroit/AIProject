from pacman_module.game import Agent
from pacman_module.pacman import Directions


def manhattan_distance(xy1, xy2):
    """Calculate Manhattan distance between two points."""
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])


class PacmanAgent(Agent):
    def __init__(self):
        super().__init__()
        self.depth = 3  # Reduce depth for faster computation

    def get_action(self, state):
        legal = state.getLegalActions(0)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        if not legal:
            return Directions.STOP

        scores = []
        for action in legal:
            successor = state.generateSuccessor(0, action)
            score, _ = self.minimax(successor, 1, 1)
            scores.append(score)

        best_score = max(scores)
        best_indices = [
            i for i, score in enumerate(scores) if score == best_score
        ]
        chosen_index = best_indices[0]  # Choose the first best action

        return legal[chosen_index]

    def minimax(self, state, agent_index, depth):
        if state.isWin():
            return float("inf"), None
        if state.isLose():
            return float("-inf"), None
        if depth >= self.depth * state.getNumAgents():
            return self.evaluation_function(state), None

        legal_moves = state.getLegalActions(agent_index)
        if Directions.STOP in legal_moves and len(legal_moves) > 1:
            legal_moves.remove(Directions.STOP)

        next_agent = (agent_index + 1) % state.getNumAgents()
        next_depth = depth + 1 if next_agent == 0 else depth

        if agent_index == 0:  # Pacman (MAX)
            max_score = float("-inf")
            best_action = None
            for action in legal_moves:
                successor = state.generateSuccessor(agent_index, action)
                score, _ = self.minimax(successor, next_agent, next_depth)
                if score > max_score:
                    max_score = score
                    best_action = action
            return max_score, best_action

        # Ghost (MIN)
        min_score = float("inf")
        worst_action = None
        for action in legal_moves:
            successor = state.generateSuccessor(agent_index, action)
            score, _ = self.minimax(successor, next_agent, next_depth)
            if score < min_score:
                min_score = score
                worst_action = action
        return min_score, worst_action

    def evaluation_function(self, state):
        if state.isWin():
            return float("inf")
        if state.isLose():
            return float("-inf")

        pacman_pos = state.getPacmanPosition()
        food = state.getFood()
        ghost_states = state.getGhostStates()
        food_list = food.asList()

        if not food_list:
            return float("inf")

        # 1. Ghost Distance Evaluation
        ghost_distances = []
        for ghost in ghost_states:
            ghost_pos = ghost.getPosition()
            dist = manhattan_distance(pacman_pos, ghost_pos)
            if dist <= 1:
                return float("-inf")
            ghost_distances.append(dist)

        min_ghost_dist = min(ghost_distances)

        # 2. Food Distance Evaluation
        food_distances = [
            manhattan_distance(pacman_pos, food)
            for food in food_list
        ]
        closest_food = min(food_distances)
        remaining_food = len(food_list)

        # 3. Calculate Score
        score = state.getScore()

        # Avoid ghosts
        if min_ghost_dist < 3:
            score -= 500 / (min_ghost_dist + 1)

        # Prefer getting closer to food
        score -= closest_food * 2

        # Penalty for remaining food
        score -= remaining_food * 20

        # Penalty for being in a corridor
        if len(state.getLegalActions(0)) <= 2:
            score -= 100

        return score
