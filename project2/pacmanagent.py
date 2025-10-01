# pacmanagent.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects
# were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from pacman_module.game import Agent
from pacman_module.game import Directions
from pacman_module import util
import numpy as np


class PacmanAgent(Agent):
    """
    A Pacman agent that actively hunts down ghosts using belief states.
    """

    def __init__(self, args):
        """
        Arguments:
        ----------
        - `args`: Namespace of arguments from command-line prompt.
        """
        self.args = args

    def get_action(self, state, belief_state):
        """
        Given a GameState, returns a legal action that moves Pacman towards the
        most likely position of the nearest ghost.

        Arguments:
        ----------
        - `state`: The current game state. See FAQ and class `pacman.GameState`.
        - `belief_state`: This argument is passed by the game framework when a
                          BeliefStateAgent is active. It is not used in this
                          implementation.

        Return:
        -------
        - A legal move as defined in `game.Directions`.
        """

        # Get legal actions, removing STOP to ensure Pacman always moves.
        legal_actions = state.getLegalActions()
        if Directions.STOP in legal_actions:
            legal_actions.remove(Directions.STOP)

        # If there are no other legal actions, Pacman is trapped.
        if not legal_actions:
            return Directions.STOP

        # Get Pacman's current position and the belief states for all ghosts.
        pacman_position = state.getPacmanPosition()
        belief_states = state.getGhostBeliefStates()
        ghosts_eaten = state.data._eaten[1:]

        # --- Step 1: Find the best ghost to target ---
        target_ghost_pos = None
        min_dist_to_ghost = float('inf')

        for i in range(len(belief_states)):
            # Skip ghosts that have already been eaten.
            if ghosts_eaten[i]:
                continue

            belief = belief_states[i]
            # Find the position with the highest probability in the belief state.
            # This is the most likely position (MLP) of the ghost.
            mlp_flat_index = np.argmax(belief)
            most_likely_pos = np.unravel_index(mlp_flat_index, belief.shape)

            # Calculate the distance from Pacman to this ghost's MLP.
            dist = util.manhattanDistance(pacman_position, most_likely_pos)

            # If this ghost is closer than the current target, update the target.
            if dist < min_dist_to_ghost:
                min_dist_to_ghost = dist
                target_ghost_pos = most_likely_pos

        # If all ghosts have been eaten, there's no target. Pacman can stop.
        if target_ghost_pos is None:
            return Directions.STOP

        # --- Step 2: Choose the action that gets closer to the target ---
        best_action = None
        min_dist_after_move = float('inf')

        for action in legal_actions:
            # Get the position Pacman would be in after taking the action.
            successor_state = state.generateSuccessor(0, action)
            successor_pos = successor_state.getPacmanPosition()

            # Calculate the distance from the new position to the target ghost.
            dist_to_target = util.manhattanDistance(successor_pos,
                                                    target_ghost_pos)

            # If this action results in a shorter distance, it's the new best action.
            if dist_to_target < min_dist_after_move:
                min_dist_after_move = dist_to_target
                best_action = action

        # Return the best action found. If no action strictly improves the
        # situation, this will be the last legal action checked.
        return best_action