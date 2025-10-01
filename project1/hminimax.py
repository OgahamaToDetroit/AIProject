from pacman_module.game import Agent
from pacman_module.pacman import Directions


def manhattan_distance(xy1, xy2):
    """Calculate Manhattan distance between two points."""
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])


class PacmanAgent(Agent):
    def __init__(self):
        super().__init__()
        self.depth = 4
        self.position_history = []

    def get_action(self, state):
        legal = state.getLegalActions(0)
        if not legal:
            return Directions.STOP

        if len(legal) > 1 and Directions.STOP in legal:
            legal.remove(Directions.STOP)

        # --- START: THE "SMART" GREEDY ENDGAME SWITCH ---
        food_list = state.getFood().asList()
        
        # ถ้าเหลืออาหาร 1 เม็ด ให้เปลี่ยนเป็นโหมด Greedy ที่ฉลาดขึ้น
        if len(food_list) == 1:
            best_score = -float('inf')
            best_action = None
            pacman_pos = state.getPacmanPosition()
            
            for action in legal:
                successor = state.generateSuccessor(0, action)
                if successor.isLose():
                    continue # ถ้าเดินไปแล้วแพ้ทันที ไม่ต้องพิจารณา

                successor_pos = successor.getPacmanPosition()
                dist_to_food = manhattan_distance(successor_pos, food_list[0])
                
                ghost_positions = [g.getPosition() for g in successor.getGhostStates()]
                dist_to_ghost = min([manhattan_distance(successor_pos, g) for g in ghost_positions])

                # ให้คะแนนโดยพิจารณา 2 อย่าง: ระยะห่างจากอาหาร และ ระยะห่างจากผี
                # ทำให้มันอยากเข้าใกล้อาหาร แต่ก็ยังกลัวผีอยู่ด้วย
                score = (dist_to_ghost * 2) - (dist_to_food * 3)

                if score > best_score:
                    best_score = score
                    best_action = action

            return best_action
        # --- END: THE "SMART" GREEDY ENDGAME SWITCH ---


        # ถ้ายังเหลืออาหารเยอะ ให้ใช้ Alpha-Beta ที่ซับซ้อนและฉลาดเหมือนเดิม
        best_score = -float('inf')
        best_action = None

        # Update position history (ยังคงเดิม)
        curr_pos = state.getPacmanPosition()
        self.position_history.append(curr_pos)
        if len(self.position_history) > 4:
            self.position_history.pop(0)

        for action in legal:
            successor = state.generateSuccessor(0, action)
            score = self.alpha_beta(
                successor,
                1,
                1,
                list(self.position_history),
                float('-inf'),
                float('inf')
            )
            if score > best_score:
                best_score = score
                best_action = action

        return best_action if best_action else legal[0]

        # ถ้ายังเหลืออาหารเยอะ ให้ใช้ Alpha-Beta ที่ซับซ้อนและฉลาดเหมือนเดิม
        best_score = float('-inf')
        best_action = None

        # Update position history (ยังคงเดิม)
        curr_pos = state.getPacmanPosition()
        self.position_history.append(curr_pos)
        if len(self.position_history) > 4:
            self.position_history.pop(0)

        for action in legal:
            successor = state.generateSuccessor(0, action)
            score = self.alpha_beta(
                successor,
                1,
                1,
                list(self.position_history),
                float('-inf'),
                float('inf')
            )
            if score > best_score:
                best_score = score
                best_action = action

        return best_action if best_action else legal[0]

    def alpha_beta(self, state, agent_index, depth, position_history, alpha, beta):
        if state.isWin():
            return float('inf')
        if state.isLose():
            return float('-inf')
        if depth >= self.depth * state.getNumAgents():
            return self.evaluation_function(state, position_history)
    
        legal_moves = state.getLegalActions(agent_index)
        if not legal_moves:
            return self.evaluation_function(state, position_history)
    
        next_agent = (agent_index + 1) % state.getNumAgents()
        next_depth = depth + 1
    
        if agent_index == 0:
            # Pacman (MAX node)
            value = float('-inf')
            for action in legal_moves:
                successor = state.generateSuccessor(agent_index, action)
                new_history = position_history[1:] + [successor.getPacmanPosition()]
                value = max(value, self.alpha_beta(successor, next_agent, next_depth, new_history, alpha, beta))
                if value > beta:
                    return value  # Prune
                alpha = max(alpha, value)
            return value
        else:
            # Ghost (MIN node)
            value = float('inf')
            for action in legal_moves:
                successor = state.generateSuccessor(agent_index, action)
                value = min(value, self.alpha_beta(successor, next_agent, next_depth, position_history, alpha, beta))
                if value < alpha:
                    return value  # Prune
                beta = min(beta, value)
            return value

    def evaluation_function(self, state, position_history):
        if state.isWin():
            return 1e9
        if state.isLose():
            return -1e9

        pacman_pos = state.getPacmanPosition()
        food_list = state.getFood().asList()
        ghost_states = state.getGhostStates()
        ghost_positions = [g.getPosition() for g in ghost_states]

        # โทษผีแบบแปรผัน (คงเดิม)
        min_ghost_dist = min(manhattan_distance(pacman_pos, g) for g in ghost_positions)
        if min_ghost_dist == 0:
            return -1e9
        elif min_ghost_dist == 1:
            ghost_penalty = -300
        elif min_ghost_dist == 2:
            ghost_penalty = -100
        elif min_ghost_dist == 3:
            ghost_penalty = -30
        else:
            ghost_penalty = 0

        # รางวัลหลัก: ลดจำนวนอาหาร (คงเดิม)
        food_count = len(food_list)
        score = -1000 * food_count

        # รางวัลรอง: เข้าใกล้อาหาร (คงเดิม)
        if food_list:
            min_food_dist = min(manhattan_distance(pacman_pos, food) for food in food_list)
            score -= 10 * min_food_dist
            if min_food_dist == 1:
                score += 300

        # --- START: THE DEFINITIVE FIX ---
        # เราจะลงโทษการเดินซ้ำที่ "ก็ต่อเมื่อ" ยังเหลืออาหารมากกว่า 1 เม็ดเท่านั้น
        # เพื่อให้ตอนจบเกม Pacman สามารถเดินย้อนกลับไปกินเม็ดสุดท้ายได้โดยไม่โดนลงโทษ
        if food_count > 1 and pacman_pos in position_history:
            score -= 100
        # --- END: THE DEFINITIVE FIX ---

        score += ghost_penalty

        return score