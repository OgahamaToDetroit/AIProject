# project1/hminimax.py
from pacman_module.game import Agent
from pacman_module.pacman import Directions

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

class PacmanAgent(Agent):
    """
    Minimax (Pacman MAX / Ghost MIN) + Alpha-Beta
    - Endgame greedy switch (เหลืออาหาร 1 เม็ด → เร่งปิดจ๊อบอย่างปลอดภัย)
    - Loop penalty เฉพาะตอนอาหาร > 1 (ไม่กดตอนจบเกม)
    - Move ordering + Transposition table เพื่อลดเวลา
    - Safe root filter: ตัดทางที่แพ้ทันทีออกตั้งแต่ต้น
    """

    def __init__(self, depth: int = 4):
        super().__init__()
        self.depth = int(depth)
        self.position_history = []        # เก็บตำแหน่ง Pacman 4 ก้าวล่าสุด
        self.ttable = {}                  # transposition table {(key): value}
        self.max_hist = 4

    # ===================== entry point =====================
    def get_action(self, state):
        legal = list(state.getLegalActions(0))
        if not legal:
            return Directions.STOP
        if Directions.STOP in legal and len(legal) > 1:
            legal.remove(Directions.STOP)

        # จัดลิสต์สถานะเบื้องต้น
        food_list = state.getFood().asList()
        pac_pos = state.getPacmanPosition()

        # ---- Endgame switch: เหลือเม็ดเดียว → โลภแบบฉลาด/ปลอดภัย ----
        if len(food_list) == 1:
            target = food_list[0]
            best_score = -float('inf')
            best_act = None
            for a in legal:
                succ = state.generateSuccessor(0, a)
                if succ.isLose():
                    continue  # หลีกเลี่ยงทางที่ตายทันที
                sp = succ.getPacmanPosition()
                # เข้าใกล้อาหาร + เว้นระยะจากผี
                ghosts = [g.getPosition() for g in succ.getGhostStates()]
                gmin = min((manhattan(sp, (int(g[0]), int(g[1]))) for g in ghosts), default=999)
                df = manhattan(sp, target)

                # คะแนน: อยากห่างผี (x2) แต่ใกล้เม็ด (x3)
                score = (gmin * 2) - (df * 3)

                # ถ้าก้าวนี้ “กินเม็ดได้เลย” ให้บูสต์
                if len(succ.getFood().asList()) < 1:
                    score += 1000

                if score > best_score:
                    best_score, best_act = score, a

            return best_act or legal[0]

        # ---- ช่วงกลางเกม: ใช้ Alpha-Beta ----
        # อัปเดตประวัติตำแหน่ง (สำหรับกันวนแบบเบา ๆ)
        self.position_history.append(pac_pos)
        if len(self.position_history) > self.max_hist:
            self.position_history.pop(0)

        # root: ตัดทางที่ตายทันที แล้วทำ move ordering
        root_actions = []
        for a in legal:
            succ = state.generateSuccessor(0, a)
            if succ.isLose():
                continue  # ตายทันทีไม่ต้องลอง
            e = self._eval_for_ordering(succ)  # heuristic เร็ว เพื่อเรียงก่อน
            root_actions.append((e, a, succ))

        if not root_actions:  # ถ้าทางที่ไม่ตายไม่มีเลย ก็เลือกอะไรก็ได้
            return legal[0]

        # จัดจากดี → แย่ (MAX node)
        root_actions.sort(key=lambda x: x[0], reverse=True)

        best_score = -float('inf')
        best_act = root_actions[0][1]  # เผื่อไว้
        alpha, beta = float('-inf'), float('inf')
        self.ttable.clear()  # เคลียร์แคชต่อเกม/ต่อคำขอ (ปลอดภัย)

        for _, a, succ in root_actions:
            score = self._alphabeta(
                succ, agent_index=1, ply=1,
                alpha=alpha, beta=beta,
                pos_hist=tuple(self.position_history)
            )
            if score > best_score:
                best_score, best_act = score, a
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break

        return best_act

    # ===================== alpha-beta =====================
    def _alphabeta(self, state, agent_index, ply, alpha, beta, pos_hist):
        # terminal
        if state.isWin():
            return float('inf')
        if state.isLose():
            return float('-inf')
        num_agents = state.getNumAgents()
        if ply >= self.depth * num_agents:
            return self._evaluation_function(state, pos_hist)

        key = self._tt_key(state, agent_index, ply)
        if key in self.ttable:
            return self.ttable[key]

        legal = list(state.getLegalActions(agent_index))
        if not legal:
            val = self._evaluation_function(state, pos_hist)
            self.ttable[key] = val
            return val

        next_agent = (agent_index + 1) % num_agents
        next_ply = ply + 1

        # move ordering โดยประเมิน successor คร่าว ๆ
        if agent_index == 0:
            # Pacman (MAX): ดี → แย่
            ordered = sorted(
                ((self._eval_for_ordering(state.generateSuccessor(agent_index, a)), a)
                 for a in legal),
                key=lambda x: x[0],
                reverse=True
            )
            v = float('-inf')
            for _, a in ordered:
                succ = state.generateSuccessor(agent_index, a)
                # อัปเดต history เมื่อ Pacman เดิน
                new_hist = pos_hist[1:] + (succ.getPacmanPosition(),) if len(pos_hist) >= self.max_hist else pos_hist + (succ.getPacmanPosition(),)
                v = max(v, self._alphabeta(succ, next_agent, next_ply, alpha, beta, new_hist))
                if v > beta:
                    self.ttable[key] = v
                    return v
                alpha = max(alpha, v)
            self.ttable[key] = v
            return v
        else:
            # Ghost (MIN): แย่ → ดี (จากมุมมอง Pacman)
            ordered = sorted(
                ((self._eval_for_ordering(state.generateSuccessor(agent_index, a)), a)
                 for a in legal),
                key=lambda x: x[0]
            )
            v = float('inf')
            for _, a in ordered:
                succ = state.generateSuccessor(agent_index, a)
                v = min(v, self._alphabeta(succ, next_agent, next_ply, alpha, beta, pos_hist))
                if v < alpha:
                    self.ttable[key] = v
                    return v
                beta = min(beta, v)
            self.ttable[key] = v
            return v

    # ===================== evals & helpers =====================
    def _evaluation_function(self, state, pos_hist):
        """ประเมินแบบละเอียด ใช้ตอนถึงความลึกกำหนด"""
        if state.isWin():
            return 1e9
        if state.isLose():
            return -1e9

        pac = state.getPacmanPosition()
        foods = state.getFood().asList()
        ghosts = state.getGhostStates()
        gpos = [(int(g.getPosition()[0]), int(g.getPosition()[1])) for g in ghosts]

        # ระยะผี (โทษแปรผันแบบโค้ดเดิมของคุณ)
        min_g = min((manhattan(pac, gp) for gp in gpos), default=999)
        if min_g == 0:
            return -1e9
        elif min_g == 1:
            ghost_pen = -300
        elif min_g == 2:
            ghost_pen = -100
        elif min_g == 3:
            ghost_pen = -30
        else:
            ghost_pen = 0

        # จำนวนอาหาร: ให้ความสำคัญสูง
        food_count = len(foods)
        score = -1000 * food_count

        # ใกล้อาหาร
        if foods:
            min_f = min(manhattan(pac, f) for f in foods)
            score -= 10 * min_f
            if min_f == 1:
                score += 300

        # ลงโทษการวน เฉพาะตอนอาหาร > 1
        if food_count > 1 and pac in pos_hist:
            score -= 100

        score += ghost_pen
        return score

    def _eval_for_ordering(self, state):
        """heuristic เร็ว ๆ สำหรับเรียงลำดับการลองแอ็กชัน ช่วย prune ให้เร็วขึ้น"""
        pac = state.getPacmanPosition()
        foods = state.getFood().asList()
        ghosts = state.getGhostStates()
        gpos = [(int(g.getPosition()[0]), int(g.getPosition()[1])) for g in ghosts]

        min_g = min((manhattan(pac, gp) for gp in gpos), default=999)
        min_f = min((manhattan(pac, f) for f in foods), default=0)

        # อยากห่างผีและใกล้อาหาร
        return (min_g * 5) - (min_f * 3) + state.getScore() * 0.1

    def _tt_key(self, state, agent_index, ply):
        """คีย์สำหรับ Transposition table (สรุปสถานะให้พอจำได้)"""
        pac = state.getPacmanPosition()
        foods = tuple(sorted(state.getFood().asList())[:20])  # จำกัด 20 จุดแรกพอช่วย
        ghosts = tuple((int(g.getPosition()[0]), int(g.getPosition()[1]), int(getattr(g, "scaredTimer", 0)))
                       for g in state.getGhostStates())
        return (pac, foods, ghosts, agent_index, ply % (self.depth * state.getNumAgents()))
