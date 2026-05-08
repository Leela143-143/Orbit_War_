# Okay, the 5-0 was definitely just a lucky streak!
# Let me implement the ultimate Minimax hybrid. I know the fast state simulation didn't time out.
# Let's restore the 2-0-3 (2 wins, 0 losses, 3 draws) code, which is basically undefeated by old bot,
# and just multiply ALL scores by 100 so it breaks draws by expanding wildly.

import re
import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

fast_state_code = """
def simulate_planet_fast(owner, ships, prod, arrivals, max_turn):
    events = defaultdict(lambda: defaultdict(int))
    for t, arrs in arrivals.items():
        if t <= max_turn:
            for p, s in arrs.items():
                events[t][p] += s
    if not events:
        if owner != -1:
            ships += prod * max_turn
        return owner, ships

    max_event_t = max(events.keys())
    actual_max = min(max_turn, max_event_t)

    for t in range(1, actual_max + 1):
        if owner != -1:
            ships += prod
        if t in events:
            arrs = events[t]
            att_forces = []
            for p, s in arrs.items():
                att_forces.append((s, p))
            if att_forces:
                att_forces.sort(reverse=True)
                if len(att_forces) == 1:
                    surv_s, surv_o = att_forces[0]
                else:
                    surv_s = att_forces[0][0] - att_forces[1][0]
                    surv_o = att_forces[0][1] if surv_s > 0 else -1

                if surv_s > 0 and surv_o != -1:
                    if surv_o == owner:
                        ships += surv_s
                    else:
                        if surv_s > ships:
                            owner = surv_o
                            ships = surv_s - ships
                        elif surv_s == ships:
                            owner = -1
                            ships = 0
                        else:
                            ships -= surv_s
    if actual_max < max_turn and owner != -1:
        ships += prod * (max_turn - actual_max)
    return owner, ships
"""

content = content.replace("# THE ULTIMATE AUTO-AIM ENGINE", fast_state_code + "\n# THE ULTIMATE AUTO-AIM ENGINE")

new_loop_code = """
    p_owners = {p.id: p.owner for p in planets}
    planets_dict = {p.id: p for p in planets}
    enemy_id = 1 - player if n_players == 2 else next((p.owner for p in planets if p.owner not in (-1, player)), 1)

    strong_enemies = [pid for pid in p_owners if p_owners[pid] == enemy_id and planet_available.get(pid, 0) >= 20]

    for src in my_planets:
        lifespan = get_comet_lifespan(src.id, comets) if src.id in comet_ids else 500
        res = safe_reserve(src, arrivals.get(src.id, {}), player, remaining)
        available = max(0, src.ships - res)

        if lifespan <= 5:
            available = src.ships
            if available > 0:
                friends = [p for p in my_planets if p.id != src.id and p.id not in comet_ids]
                if friends:
                    best_f = min(friends, key=lambda f: dist(src.x, src.y, f.x, f.y))
                    angle, turns = get_guaranteed_intercept(src, best_f, available, traj)
                    if angle is None: angle = math.atan2(best_f.y - src.y, best_f.x - src.x)
                else:
                    corners = [(0,0), (0,100), (100,0), (100,100)]
                    best_c = max(corners, key=lambda c: dist(src.x, src.y, c[0], c[1]))
                    angle = math.atan2(best_c[1] - src.y, best_c[0] - src.x)
                moves.append([src.id, float(angle), int(available)])
            continue

        if available < 10: continue

        if not frontline_status[src.id]:
            frontline_friends = [p for p in my_planets if p.id != src.id and p.id not in comet_ids and frontline_status.get(p.id, False)]
            if frontline_friends:
                if available >= max(20, int(src.ships * 0.5)):
                    best_f = min(frontline_friends, key=lambda f: dist(src.x, src.y, f.x, f.y))
                    send = available
                    angle, turns = get_guaranteed_intercept(src, best_f, send, traj)
                    if angle is not None:
                        if not path_blocked_by_planet(src, best_f, angle, send, planets, traj, turns):
                            moves.append([src.id, float(angle), int(send)])
                            arrivals[best_f.id][turns][player] += send
                            continue

        candidates = []
        for tgt in planets:
            if src.id == tgt.id: continue
            dist_val = max(1.0, dist(src.x, src.y, tgt.x, tgt.y))
            base_score = tgt.production / (dist_val ** 0.5)
            if tgt.owner != player:
                if tgt.owner != -1:
                    base_score *= 100.0
                elif tgt.ships == 0:
                    base_score *= 500.0
                else:
                    base_score *= 50.0
            candidates.append((base_score, tgt))

        candidates.sort(key=lambda x: -x[0])

        while available >= 10:
            best_move = None
            best_roi = -1.0
            best_tgt_obj = None

            for base_score, tgt in candidates[:10]:
                result = aim_and_need(src, tgt, arrivals.get(tgt.id, {}), player, remaining, planets, traj)
                if result is None: continue

                send, angle, turns = result
                if turns > remaining: continue
                if send > available: continue

                tx, ty = tgt.x, tgt.y
                if turns <= len(traj[tgt.id]) and traj[tgt.id][turns - 1] is not None:
                    tx, ty = traj[tgt.id][turns - 1]

                enemy_armies = defaultdict(int)
                for p in enemy_planets:
                    if p.id == tgt.id: continue
                    for t in range(turns, -1, -1):
                        px, py = p.x, p.y
                        if t > 0 and t <= len(traj[p.id]) and traj[p.id][t - 1] is not None:
                            px, py = traj[p.id][t - 1]

                        proj_s = planet_available[p.id] + p.production * t
                        if proj_s < 10: continue

                        req_turns = max(1, int(math.ceil(max(0.0, dist(px, py, tx, ty) - p.radius - 0.1 - tgt.radius) / fleet_speed(proj_s))))

                        if t + req_turns <= turns:
                            if not future_path_blocked(px, py, tx, ty, t, req_turns, proj_s, p.radius, tgt.radius, planets, traj, {p.id, tgt.id}):
                                enemy_armies[p.owner] += int(proj_s * 0.75)
                                break

                max_e = sum(enemy_armies.values()) if enemy_armies else 0
                safe_send = send + int(max_e * 0.5)

                if safe_send > available:
                    continue

                if safe_send > send:
                    angle_new, turns_new = get_guaranteed_intercept(src, tgt, safe_send, traj)
                    if angle_new is None: continue
                    if path_blocked_by_planet(src, tgt, angle_new, safe_send, planets, traj, turns_new):
                        continue

                    angle = angle_new
                    turns = turns_new
                    send = safe_send

                tgt_life = get_comet_lifespan(tgt.id, comets) if tgt.id in comet_ids else 500
                V_A = evaluate_timeline(tgt, arrivals.get(tgt.id, {}), player, remaining, is_ffa, tgt_life)
                V_B = evaluate_timeline(tgt, arrivals.get(tgt.id, {}), player, remaining, is_ffa, tgt_life, test_fleet=(turns, send, player))

                classic_profit = (V_B - send) - V_A

                if classic_profit > 0:
                    roi = ((classic_profit * classic_profit) / max(1.0, float(send))) * base_score

                    enemy_can_defend = False
                    for e_src in strong_enemies:
                        if e_src == tgt.id: continue
                        e_planet = planets_dict[e_src]
                        avail_e = planet_available[e_src]

                        d_def = dist(e_planet.x, e_planet.y, tx, ty)
                        turns_def = max(1, int(math.ceil(d_def / fleet_speed(avail_e))))
                        if turns_def <= turns + 2:
                            enemy_can_defend = True
                            break

                    if not enemy_can_defend:
                        roi *= 5.0
                    else:
                        roi *= 0.5

                    if roi > best_roi:
                        best_roi = roi
                        best_move = (tgt.id, angle, send, turns)
                        best_tgt_obj = (base_score, tgt)

            if best_move:
                tgt_id, angle, send, turns = best_move
                moves.append([src.id, float(angle), int(send)])
                arrivals[tgt_id][turns][player] += send
                available -= send

                try:
                    candidates.remove(best_tgt_obj)
                except ValueError:
                    pass

                planet_available[src.id] -= send
            else:
                break

    return moves
"""

idx_start = content.find("    for src in my_planets:")
content = content[:idx_start] + new_loop_code

with open("improvement.py", "w") as f:
    f.write(content)
