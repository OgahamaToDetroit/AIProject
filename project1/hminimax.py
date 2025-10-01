from pacman_module.game import Agent
from pacman_module.pacman import Directions


def manhattan_distance(xy1, xy2):
    """Calculate Manhattan distance between two points."""
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])


class PacmanAgent(Agent):
    def __init__(self):
        super().__init__()
        self.depth = 3
        self.position_history = []

    def get_action(self, state):
        legal = state.getLegalActions(0)
        if not legal:
            return Directions.STOP

        if len(legal) > 1 and Directions.STOP in legal:
            legal.remove(Directions.STOP)

        best_score = float('-inf')
        best_action = None

        # Update position history
        curr_pos = state.getPacmanPosition()
        self.position_history.append(curr_pos)
        if len(self.position_history) > 4:
            self.position_history.pop(0)

        for action in legal:
            successor = state.generateSuccessor(0, action)
            score = self.h_minimax(
                successor,
                1,
                1,
                list(self.position_history)
            )
            if score > best_score:
                best_score = score
                best_action = action

        return best_action if best_action else legal[0]

    def h_minimax(self, state, agent_index, depth, position_history):
        if state.isWin():
            return float('inf')
        if state.isLose():
            return float('-inf')
        if depth >= self.depth * state.getNumAgents():
            return self.evaluation_function(state, position_history)

        legal_moves = state.getLegalActions(agent_index)
        next_agent = (agent_index + 1) % state.getNumAgents()
        next_depth = depth + 1 if next_agent == 0 else depth

        if agent_index == 0:
            new_history = (
                position_history + [state.getPacmanPosition()]
                if len(position_history) < 4
                else position_history[1:] + [state.getPacmanPosition()]
            )
            return max(
                self.h_minimax(
                    state.generateSuccessor(agent_index, action),
                    next_agent,
                    next_depth,
                    new_history
                )
                for action in legal_moves
            )

        return min(
            self.h_minimax(
                state.generateSuccessor(agent_index, action),
                next_agent,
                next_depth,
                position_history
            )
            for action in legal_moves
        )

    def evaluation_function(self, state, position_history):
        if state.isWin():
            return float('inf')
        if state.isLose():
            return float('-inf')

        pacman_pos = state.getPacmanPosition()
        food_list = state.getFood().asList()
        ghost_states = state.getGhostStates()
        score = state.getScore()

        # Ghost avoidance (strong exponential penalty)
        for ghost in ghost_states:
            dist = manhattan_distance(pacman_pos, ghost.getPosition())
            if dist <= 1:
                return float('-inf')
            if dist <= 2:
                score -= 2000
            elif dist < 4:
                score -= 1000 / (dist ** 2)
            else:
                score -= 50 / dist

        # Food: reward for being close to food and for eating food
        if food_list:
            food_distances = [
                manhattan_distance(pacman_pos, food)
                for food in food_list
            ]
            min_food_dist = min(food_distances)
            avg_food_dist = sum(food_distances) / len(food_distances)

            # Reward for being close to the closest food
            score += 200 / (min_food_dist + 1)
            # Reward for being close to the average food position
            score += 50 / (avg_food_dist + 1)
            # Stronger penalty for remaining food
            score -= len(food_list) * 25

            # Reward for being close to the center of food
            food_center = (
                sum(f[0] for f in food_list) / len(food_list),
                sum(f[1] for f in food_list) / len(food_list)
            )
            center_dist = manhattan_distance(pacman_pos, food_center)
            score += 30 / (center_dist + 1)

        # Penalize loops: repeated positions in the last 4 moves
        repeat_count = position_history.count(pacman_pos)
        if repeat_count > 1:
            score -= 600 * repeat_count

        # Reward for having more legal moves (mobility)
        num_moves = len(state.getLegalActions(0))
        if num_moves <= 2:
            score -= 200
        else:
            score += 30 * num_moves

        return score
