# Complete this class for all parts of the project

from pacman_module.game import Agent
import numpy as np
from pacman_module import util
from scipy.stats import binom


class BeliefStateAgent(Agent):
    def __init__(self, args):
        """
        Arguments:
        ----------
        - `args`: Namespace of arguments from command-line prompt.
        """
        self.args = args

        """
            Variables to use in 'update_belief_state' method.
            Initialization occurs in 'get_action' method.

            XXX: DO NOT MODIFY THE DEFINITION OF THESE VARIABLES
            # Doing so will result in a 0 grade.
        """

        # Current list of belief states over ghost positions
        self.beliefGhostStates = None

        # Grid of walls (assigned with 'state.getWalls()' method)
        self.walls = None

        # Hyper-parameters
        self.ghost_type = self.args.ghostagent
        self.sensor_variance = self.args.sensorvariance

        self.p = 0.5
        self.n = int(self.sensor_variance/(self.p*(1-self.p)))

        # XXX: Your code here
        # List to store metrics recorded at each time step
        self.metrics = []


    def _get_sensor_model(self, pacman_position, evidence):
        """
        Arguments:
        ----------
        - `pacman_position`: 2D coordinates position
          of pacman at state x_{t}
          where 't' is the current time step

        Return:
        -------
        The sensor model represented as a 2D numpy array of
        size [width, height].
        The element at position (w, h) is the probability
        P(E_t=evidence | X_t=(w, h))
        """
        width, height = self.walls.width, self.walls.height
        sensor_model = np.zeros((width, height))

        for w in range(width):
            for h in range(height):
                if not self.walls[w][h]:
                    true_distance = util.manhattanDistance(
                        (w, h), pacman_position)
                    # The value 'k' for the binomial PMF, representing the number of successes
                    # noise = k - n*p, evidence = true_distance + noise
                    # => k = evidence - true_distance + n*p
                    k = evidence - true_distance + self.n * self.p
                    prob = binom.pmf(k, self.n, self.p)
                    sensor_model[w, h] = prob

        # If the sum is zero, it means the evidence is impossible under the model
        # for any state. To avoid issues with normalization later, we can
        # return a uniform distribution over legal positions.
        if np.sum(sensor_model) == 0:
            # All positions have zero probability, which is problematic.
            num_legal_positions = width * height - np.sum(self.walls.data)
            if num_legal_positions > 0:
                uniform_prob = 1.0 / num_legal_positions
                for w in range(width):
                    for h in range(height):
                        if not self.walls[w][h]:
                            sensor_model[w, h] = uniform_prob

        return sensor_model

    def _get_transition_model(self, pacman_position):
        """
        Arguments:
        ----------
        - `pacman_position`: 2D coordinates position
          of pacman at state x_{t}, which influences ghost movement.

        Return:
        -------
        The transition model represented as a 4D numpy array of
        size [width, height, width, height].
        The element at position (w1, h1, w2, h2) is the probability
        P(X_t+1=(w1, h1) | X_t=(w2, h2))
        """
        width, height = self.walls.width, self.walls.height
        transition_model = np.zeros((width, height, width, height))

        # 1. Set the "fear factor" based on the ghost's personality.
        # Set fear_factor based on ghost type as per README instructions
        if self.ghost_type == 'confused':
            fear_factor = 1
        elif self.ghost_type == 'afraid':
            fear_factor = 2
        elif self.ghost_type == 'scared':
            fear_factor = 8  # 2**3
        else:
            raise ValueError("Unknown ghost type: {}".format(self.ghost_type))

        # 2. Iterate over all possible starting positions (x_{t-1}).
        for w2 in range(width):      # Current position w2
            for h2 in range(height):   # Current position h2
                if self.walls[w2][h2]:
                    continue

                # 3. Determine all legal successor positions (x_t).
                # Get legal successor positions from (w2, h2)
                successors = []
                for dw, dh in [(0, 1), (0, -1), (1, 0), (-1, 0)]:  # N, S, E, W
                    w_succ, h_succ = w2 + dw, h2 + dh
                    if not self.walls[w_succ][h_succ]:
                        successors.append((w_succ, h_succ))

                if not successors:
                    # Ghost is trapped, stays in place
                    transition_model[w2, h2, w2, h2] = 1.0
                    continue

                # 4. Calculate the probability distribution over successors.
                # Calculate probability distribution over successors
                dist = util.Counter()
                current_dist_to_pacman = util.manhattanDistance(
                    (w2, h2), pacman_position)

                for w_succ, h_succ in successors:
                    succ_dist_to_pacman = util.manhattanDistance(
                        (w_succ, h_succ), pacman_position
                    )

                    # Ghosts prefer to move away from Pacman.
                    weight = 1.0
                    if succ_dist_to_pacman >= current_dist_to_pacman:
                        weight = float(fear_factor)

                    dist[(w_succ, h_succ)] = weight

                dist.normalize()

                # 5. Populate the transition model matrix.
                for (w1, h1), prob in dist.items():
                    transition_model[w1, h1, w2, h2] = prob

        return transition_model

    def _get_updated_belief(self, belief, evidences, pacman_position,
            ghosts_eaten):
        """
        Given a list of (noised) distances from pacman to ghosts,
        and the previous belief states before receiving the evidences,
        returns the updated list of belief states about ghosts positions.

        Arguments:
        ----------
        - `belief`: A list of Z belief states at state x_{t-1}
          as N*M numpy mass probability matrices.
        - `evidences`: list of distances between
          pacman and ghosts at state x_{t}.
        - `pacman_position`: 2D coordinates position
          of pacman at state x_{t}.
        - `ghosts_eaten`: list of booleans indicating
          whether ghosts have been eaten or not.

        Return:
        -------
        - A list of Z belief states at state x_{t}
          as N*M numpy mass probability matrices.

        N.B. : [0,0] is the bottom left corner of the maze.
               Matrices filled with zeros must be returned for eaten ghosts.
        """
        width, height = self.walls.width, self.walls.height
        num_ghosts = len(belief)
        new_beliefs = []

        # The transition model is the same for all ghosts as they share the
        # same policy, so we compute it only once.
        transition_model = self._get_transition_model(pacman_position)

        for i in range(num_ghosts):
            if ghosts_eaten[i]:
                # Ghost is eaten, belief is a zero matrix
                new_beliefs.append(np.zeros((width, height)))
                continue

            prev_belief = belief[i]

            # 1. Prediction step: P(X_t|e_{1:t-1}) =
            #    sum_{x_{t-1}} P(X_t|x_{t-1}) * P(x_{t-1}|e_{1:t-1})
            predicted_belief = np.einsum(
                'klwh,wh->kl', transition_model, prev_belief)

            # 2. Update step: P(X_t|e_{1:t}) ∝ P(e_t|X_t) * P(X_t|e_{1:t-1})
            evidence = evidences[i]
            sensor_model = self._get_sensor_model(pacman_position, evidence)
            updated_belief_unnormalized = sensor_model * predicted_belief

            # 3. Normalization
            s = np.sum(updated_belief_unnormalized)
            if s < 1e-9:  # Use a small epsilon to handle floating point issues
                # Evidence was impossible. Reset to uniform belief over legal
                # positions to avoid division by zero and recover.
                num_legal_positions = width * height - np.sum(self.walls.data)
                if num_legal_positions > 0:
                    uniform_prob = 1.0 / num_legal_positions
                else:
                    uniform_prob = 0
                updated_belief = np.full((width, height), uniform_prob)
                updated_belief[self.walls.data] = 0

            else:
                updated_belief = updated_belief_unnormalized / s

            new_beliefs.append(updated_belief)

        return new_beliefs

    def update_belief_state(self, evidences, pacman_position, ghosts_eaten):
        """
        Given a list of (noised) distances from pacman to ghosts,
        returns a list of belief states about ghosts positions

        Arguments:
        ----------
        - `evidences`: list of distances between
          pacman and ghosts at state x_{t}
          where 't' is the current time step
        - `pacman_position`: 2D coordinates position
          of pacman at state x_{t}
          where 't' is the current time step
        - `ghosts_eaten`: list of booleans indicating
          whether ghosts have been eaten or not

        Return:
        -------
        - A list of Z belief states at state x_{t}
          as N*M numpy mass probability matrices
          where N and M are respectively width and height
          of the maze layout and Z is the number of ghosts.

        XXX: DO NOT MODIFY THIS FUNCTION !!!
        Doing so will result in a 0 grade.
        """
        belief = self._get_updated_belief(self.beliefGhostStates, evidences,
                                          pacman_position, ghosts_eaten)
        self.beliefGhostStates = belief
        return belief

    def _get_evidence(self, state):
        """
        Computes noisy distances between pacman and ghosts.

        Arguments:
        ----------
        - `state`: The current game state s_t
                   where 't' is the current time step.
                   See FAQ and class `pacman.GameState`.


        Return:
        -------
        - A list of Z noised distances in real numbers
          where Z is the number of ghosts.

        XXX: DO NOT MODIFY THIS FUNCTION !!!
        Doing so will result in a 0 grade.
        """
        positions = state.getGhostPositions()
        pacman_position = state.getPacmanPosition()
        noisy_distances = []

        for pos in positions:
            true_distance = util.manhattanDistance(pos, pacman_position)
            noise = binom.rvs(self.n, self.p) - self.n*self.p
            noisy_distances.append(true_distance + noise)

        return noisy_distances

    def _record_metrics(self, belief_states, state):
        """
        Use this function to record your metrics
        related to true and belief states.
        Won't be part of specification grading.

        Arguments:
        ----------
        - `state`: The current game state s_t
                   where 't' is the current time step.
                   See FAQ and class `pacman.GameState`.
        - `belief_states`: A list of Z
           N*M numpy matrices of probabilities
           where N and M are respectively width and height
           of the maze layout and Z is the number of ghosts.

        N.B. : [0,0] is the bottom left corner of the maze
        """
        # Dictionary to store metrics for the current time step
        metrics_t = {}
        ghost_positions = state.getGhostPositions()
        num_ghosts = len(belief_states)

        for i in range(num_ghosts):
            belief = belief_states[i]
            
            # If belief is all zeros (e.g., ghost is eaten), skip metrics
            if np.sum(belief) == 0:
                continue

            true_pos = ghost_positions[i]

            # Metric for 3.a: Uncertainty (Shannon Entropy)
            # A higher entropy means the belief is more spread out (more uncertain).
            # A lower entropy means the belief is more concentrated (more certain).
            # We filter out probabilities equal to 0 to avoid log(0).
            probs = belief[belief > 0]
            entropy = -np.sum(probs * np.log2(probs))
            metrics_t[f'ghost_{i}_entropy'] = entropy

            # Metrics for 3.b: Quality of the belief state

            # Metric 1: Error Distance
            # Manhattan distance between the most likely position and the true
            # position. Lower is better.
            predicted_pos_flat = np.argmax(belief)
            predicted_pos = np.unravel_index(predicted_pos_flat, belief.shape)
            error_dist = util.manhattanDistance(predicted_pos, true_pos)
            metrics_t[f'ghost_{i}_error_dist'] = error_dist

            # Metric 2: Probability at Ground Truth
            # The probability assigned to the ghost's true location.
            # Higher is better.
            true_x, true_y = int(true_pos[0]), int(true_pos[1])
            prob_at_true_pos = belief[true_x, true_y]
            metrics_t[f'ghost_{i}_prob_at_true'] = prob_at_true_pos

        if metrics_t:
            self.metrics.append(metrics_t)

    def get_action(self, state):
        """
        Given a pacman game state, returns a belief state.

        Arguments:
        ----------
        - `state`: the current game state.
                   See FAQ and class `pacman.GameState`.

        Return:
        -------
        - A belief state.
        """

        """
           XXX: DO NOT MODIFY THAT FUNCTION !!!
                Doing so will result in a 0 grade.
        """
        # Variables are specified in constructor.
        if self.beliefGhostStates is None:
            self.beliefGhostStates = state.getGhostBeliefStates()
        if self.walls is None:
            self.walls = state.getWalls()

        evidence = self._get_evidence(state)
        newBeliefStates = self.update_belief_state(evidence,
                                                   state.getPacmanPosition(),
                                                   state.data._eaten[1:])
        self._record_metrics(self.beliefGhostStates, state)

        return newBeliefStates, evidence
