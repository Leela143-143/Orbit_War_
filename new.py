import math
from collections import defaultdict
from kaggle_environments.envs.orbit_wars.orbit_wars import Planet, Fleet

# --- CONSTANTS ---
BOARD = 100.0
CENTER_X, CENTER_Y = BOARD / 2.0, BOARD / 2.0
SUN_R = 10.0
MAX_SPEED = 6.0
TOTAL_STEPS = 500

MAX_DIST = math.hypot(BOARD, BOARD)
MAX_SIM_TURNS = int(math.ceil(MAX_DIST / 1.0))

# ==========================================
# GEOMETRY & PHYSICS
# ==========================================
def dist(ax, ay, bx, by): return math.hypot(ax - bx, ay - by)

def fleet_speed(ships):
    if ships <= 1: return 1.0
    ratio = math.log(max(1, ships)) / math.log(1000.0)
    return 1.0 + (MAX_SPEED - 1.0) * (max(0.0, min(1.0, ratio)) ** 1.5)

def segment_hits_circle(x1, y1, x2, y2, cx, cy, r):
    if x1 < x2:
        if cx + r < x1 or cx - r > x2: return False
    else:
        if cx + r < x2 or cx - r > x1: return False
    if y1 < y2:
        if cy + r < y1 or cy - r > y2: return False
    else:
        if cy + r < y2 or cy - r > y1: return False
        
    dx, dy = x2 - x1, y2 - y1
    fx, fy = x1 - cx, y1 - cy
    a = dx*dx + dy*dy
    if a < 1e-9: return math.hypot(fx, fy) <= r
    b = 2*(fx*dx + fy*dy)
    c = fx*fx + fy*fy - r*r
    disc = b*b - 4*a*c
    if disc < 0: return False
    disc = math.sqrt(disc)
    t1 = (-b - disc) / (2*a)
    t2 = (-b + disc) / (2*a)
    return (0 <= t1 <= 1) or (0 <= t2 <= 1)

# ==========================================
# DYNAMIC TRICKLE PREVENTION
# ==========================================
def get_dynamic_batch_size(src_prod, dist_val):
    if src_prod <= 0: return 1
    target_throughput = src_prod * dist_val
    for s in range(1, 1001):
        if s * fleet_speed(s) >= target_throughput:
            return s
    return 1000

# ==========================================
# ORBITAL PREDICTION
# ==========================================
def predict_planet_pos(planet, initial_by_id, ang_vel, turns):
    init = initial_by_id.get(planet.id)
    if init is None: return planet.x, planet.y
    orbital_r = dist(init.x, init.y, CENTER_X, CENTER_Y)
    if orbital_r + init.radius >= BOARD / 2.0: return planet.x, planet.y
    cur_ang = math.atan2(planet.y - CENTER_Y, planet.x - CENTER_X)
    new_ang = cur_ang + ang_vel * turns
    return CENTER_X + orbital_r * math.cos(new_ang), CENTER_Y + orbital_r * math.sin(new_ang)

def get_comet_lifespan(planet_id, comets):
    for g in comets:
        pids = g.get("planet_ids",[])
        if planet_id not in pids: continue
        idx = pids.index(planet_id)
        paths = g.get("paths",[])
        path_index = g.get("path_index", 0)
        if idx >= len(paths): return 0
        path = paths[idx]
        return max(0, len(path) - path_index)
    return TOTAL_STEPS

def predict_comet_pos(planet_id, comets, turns):
    for g in comets:
        pids = g.get("planet_ids",[])
        if planet_id not in pids: continue
        idx = pids.index(planet_id)
        paths = g.get("paths",[])
        path_index = g.get("path_index", 0)
        if idx >= len(paths): return None
        path = paths[idx]
        future_idx = path_index + int(turns)
        if 0 <= future_idx < len(path):
            return path[future_idx][0], path[future_idx][1]
        return None
    return None

def predict_pos(planet, initial_by_id, ang_vel, comets, comet_ids, turns):
    if planet.id in comet_ids:
        return predict_comet_pos(planet.id, comets, turns)
    return predict_planet_pos(planet, initial_by_id, ang_vel, turns)

def precompute_trajectories(planets, initial_by_id, ang_vel, comets, comet_ids, max_turns):
    traj = {}
    for p in planets:
        traj[p.id] =[predict_pos(p, initial_by_id, ang_vel, comets, comet_ids, t) for t in range(1, max_turns + 1)]
    return traj

# ==========================================
# DISCRETE EVENT SIMULATION
# ==========================================
def build_threat_map(fleets, planets, traj, max_turns):
    arrivals = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for f in fleets:
        sp = fleet_speed(f.ships)
        vx, vy = math.cos(f.angle) * sp, math.sin(f.angle) * sp
        fx, fy = f.x, f.y
        for t in range(1, max_turns + 1):
            nx, ny = fx + vx, fy + vy
            if not (0 <= nx <= BOARD and 0 <= ny <= BOARD): break
            if segment_hits_circle(fx, fy, nx, ny, CENTER_X, CENTER_Y, SUN_R): break
            
            hit_pid = None
            for p in planets:
                if t - 1 >= len(traj[p.id]): continue
                pos = traj[p.id][t - 1]
                if pos is None: continue
                px, py = pos
                if segment_hits_circle(fx, fy, nx, ny, px, py, p.radius):
                    hit_pid = p.id
                    break
            if hit_pid is not None:
                arrivals[hit_pid][t][f.owner] += f.ships
                break
            else:
                fx, fy = nx, ny
    return arrivals

def simulate_planet(planet, arrivals, test_fleet=None, max_turn=MAX_SIM_TURNS):
    owner = planet.owner
    ships = planet.ships
    prod = planet.production
    
    events = defaultdict(lambda: defaultdict(int))
    if arrivals:
        for t, arrs in arrivals.items():
            if t > max_turn: continue
            for o, s in arrs.items():
                events[t][o] += s
                
    if test_fleet:
        arr_t, s, o = test_fleet
        if arr_t <= max_turn:
            events[arr_t][o] += s
            
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
            att_forces =[]
            for o, s in arrs.items():
                att_forces.append((s, o))
                
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

def get_death_info(planet, arrivals, player, max_turn):
    owner = planet.owner
    ships = planet.ships
    prod = planet.production
    
    events = defaultdict(lambda: defaultdict(int))
    if arrivals:
        for t, arrs in arrivals.items():
            if t > max_turn: continue
            for o, s in arrs.items():
                events[t][o] += s
                
    if not events: return -1, 0
        
    max_event_t = max(events.keys())
    actual_max = min(max_turn, max_event_t)
    
    for t in range(1, actual_max + 1):
        if owner != -1:
            ships += prod
            
        if t in events:
            arrs = events[t]
            att_forces = [(s, o) for o, s in arrs.items()]
            
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
                        if surv_s >= ships:
                            deficit = surv_s - ships + 1
                            return t, deficit
                        else:
                            ships -= surv_s
    return -1, 0

def get_required_defense(planet, arrivals, player, max_turn):
    """Replaces safe_reserve: calculates the exact starting ships required to survive all simulated attacks in O(N)."""
    owner = planet.owner
    prod = planet.production
    
    events = defaultdict(lambda: defaultdict(int))
    if arrivals:
        for t, arrs in arrivals.items():
            if t > max_turn: continue
            for o, s in arrs.items():
                events[t][o] += s
                
    if not events: return 0
        
    max_event_t = max(events.keys())
    actual_max = min(max_turn, max_event_t)
    
    required = 0
    current_ships = 0
    
    for t in range(1, actual_max + 1):
        if owner != -1:
            current_ships += prod
            
        if t in events:
            arrs = events[t]
            att_forces = [(s, o) for o, s in arrs.items()]
            
            if att_forces:
                att_forces.sort(reverse=True)
                if len(att_forces) == 1:
                    surv_s, surv_o = att_forces[0]
                else:
                    surv_s = att_forces[0][0] - att_forces[1][0]
                    surv_o = att_forces[0][1] if surv_s > 0 else -1
                
                if surv_s > 0 and surv_o != -1:
                    if surv_o == owner:
                        current_ships += surv_s
                    else:
                        if surv_s >= current_ships:
                            shortfall = surv_s - current_ships + 1
                            required += shortfall
                            current_ships += shortfall
                            current_ships -= surv_s
                        else:
                            current_ships -= surv_s
                            
    return required

def evaluate_timeline(planet, arrivals, player, remaining_steps, is_ffa, comet_lifespan, test_fleet=None):
    max_t = min(remaining_steps, comet_lifespan)
    last_event = 0
    if arrivals: last_event = max(arrivals.keys())
    if test_fleet: last_event = max(last_event, test_fleet[0])
    
    sim_t = min(max_t, last_event)
    owner, ships = simulate_planet(planet, arrivals, test_fleet, sim_t)
    
    post_turns = max_t - sim_t
    if owner != -1: ships += post_turns * planet.production
    
    if owner == player: return ships
    elif owner == -1: return 0
    else: return 0 if is_ffa else -ships

def path_blocked_by_planet(src, target, angle, ships, planets, traj, turns):
    sp = fleet_speed(ships)
    vx, vy = math.cos(angle) * sp, math.sin(angle) * sp
    fx, fy = src.x + math.cos(angle)*(src.radius + 0.1), src.y + math.sin(angle)*(src.radius + 0.1)
    
    for t in range(1, turns + 1):
        nx, ny = fx + vx, fy + vy
        if segment_hits_circle(fx, fy, nx, ny, CENTER_X, CENTER_Y, SUN_R): return True
        for p in planets:
            if p.id == target.id or p.id == src.id: continue
            if t - 1 >= len(traj[p.id]): continue
            pos = traj[p.id][t - 1]
            if pos is None: continue
            px, py = pos
            if segment_hits_circle(fx, fy, nx, ny, px, py, p.radius): return True
        fx, fy = nx, ny
    return False

def flight_hits_target(src, target, angle, ships, traj, max_turns):
    sp = fleet_speed(ships)
    vx, vy = math.cos(angle) * sp, math.sin(angle) * sp
    fx, fy = src.x + math.cos(angle)*(src.radius + 0.1), src.y + math.sin(angle)*(src.radius + 0.1)
    
    for t in range(1, max_turns + 1):
        nx, ny = fx + vx, fy + vy
        if t - 1 < len(traj[target.id]) and traj[target.id][t - 1] is not None:
            px, py = traj[target.id][t - 1]
        else:
            px, py = target.x, target.y
            
        if segment_hits_circle(fx, fy, nx, ny, px, py, target.radius):
            return t
        fx, fy = nx, ny
    return -1

def get_guaranteed_intercept(src, target, ships, traj):
    sp = fleet_speed(ships)
    tx, ty = target.x, target.y
    
    turns = 1
    # INCREASED: 10 prediction loops to catch high-speed comets accurately
    for _ in range(10):
        d = max(0.0, dist(src.x, src.y, tx, ty) - src.radius - 0.1 - target.radius)
        turns = max(1, int(math.ceil(d / sp)))
        if turns - 1 < len(traj[target.id]) and traj[target.id][turns - 1] is not None:
            tx, ty = traj[target.id][turns - 1]
        else:
            break
            
    # WIDENED: Expand temporal window for fractional hits
    for t in range(max(1, turns - 4), turns + 8):
        if t - 1 < len(traj[target.id]) and traj[target.id][t - 1] is not None:
            px, py = traj[target.id][t - 1]
            d = dist(src.x, src.y, px, py)
            base_angle = math.atan2(py - src.y, px - src.x)
            
            width = math.asin(min(1.0, target.radius / max(1.0, d)))
            
            # FINER RESOLUTION: 15 angles tested (guarantees hit on tiny comet radius)
            for offset in [0, 0.15, -0.15, 0.3, -0.3, 0.45, -0.45, 0.6, -0.6, 0.75, -0.75, 0.9, -0.9, 1.05, -1.05]:
                test_angle = base_angle + offset * width
                hit_turn = flight_hits_target(src, target, test_angle, ships, traj, t + 4)
                if hit_turn != -1:
                    return test_angle, hit_turn
                    
    return None, None

def get_min_ships_to_conquer(src, target, arrivals, player, remaining_steps, available_ships, traj):
    owner, _ = simulate_planet(target, arrivals, test_fleet=None, max_turn=min(MAX_SIM_TURNS, remaining_steps))
    if owner == player:
        return None 
        
    low, high = 1, available_ships
    best = None
    
    while low <= high:
        mid = (low + high) // 2
        angle, turns = get_guaranteed_intercept(src, target, mid, traj)
        if angle is None:
            low = mid + 1 
            continue
            
        owner, _ = simulate_planet(target, arrivals, test_fleet=(turns, mid, player), max_turn=min(MAX_SIM_TURNS, remaining_steps))
        
        if owner == player:
            best = mid
            high = mid - 1
        else:
            low = mid + 1
            
    return best

# ==========================================
# MAIN AGENT
# ==========================================
def agent(obs):
    get = obs.get if isinstance(obs, dict) else lambda k, d=None: getattr(obs, k, d)
    player        = get("player", 0)
    step          = get("step", 0) or 0
    planets       =[Planet(*p) for p in get("planets", [])]
    fleets        =[Fleet(*f) for f in get("fleets", [])]
    ang_vel       = get("angular_velocity", 0.0) or 0.0
    initial_by_id = {Planet(*p).id: Planet(*p) for p in get("initial_planets",[])}
    comets        = get("comets",[]) or[]
    comet_ids     = set(get("comet_planet_ids",[]) or[])
    my_planets    =[p for p in planets if p.owner == player]
    
    if not my_planets: return[]

    remaining = max(1, TOTAL_STEPS - step)
    n_players = len(set([p.owner for p in planets if p.owner != -1]))
    is_ffa = n_players > 2
    
    traj = precompute_trajectories(planets, initial_by_id, ang_vel, comets, comet_ids, max_turns=MAX_SIM_TURNS)
    arrivals = build_threat_map(fleets, planets, traj, max_turns=MAX_SIM_TURNS)
    moves =[]
    
    enemy_planets =[p for p in planets if p.owner != player and p.owner != -1]
    
    doomed_planets = {}
    planet_available = {}
    
    for p in planets:
        if p.owner == -1:
            planet_available[p.id] = 0
            continue
            
        if p.owner == player:
            death_turn, deficit = get_death_info(p, arrivals.get(p.id, {}), player, min(MAX_SIM_TURNS, remaining))
            comet_life = get_comet_lifespan(p.id, comets) if p.id in comet_ids else float('inf')
            
            # Unify comet lifespan death and enemy invasion death into one timeline
            actual_death_turn = min(death_turn if death_turn != -1 else float('inf'), comet_life)
            
            if actual_death_turn != float('inf'):
                is_doomed = False
                
                # If a comet's natural lifespan ends, it's inevitably doomed.
                if actual_death_turn == comet_life:
                    is_doomed = True
                else:
                    # DEFENSE CHECK: Can friendly planets save this planet before the enemy arrives?
                    reinforcements = 0
                    for friend in my_planets:
                        if friend.id == p.id: continue
                        req_turns = math.ceil(dist(friend.x, friend.y, p.x, p.y) / fleet_speed(friend.ships))
                        if req_turns <= actual_death_turn:
                            reinforcements += friend.ships
                            
                    if reinforcements < deficit:
                        is_doomed = True
                        
                if is_doomed:
                    doomed_planets[p.id] = actual_death_turn
                    # Wait/Hoard perfectly until exactly 1 turn before death (Evacuate all at once without trickling)
                    if actual_death_turn <= 1:
                        planet_available[p.id] = p.ships 
                    else:
                        planet_available[p.id] = 0 
                    continue
                
        # Use mathematically exact calculation instead of binary search safe_reserve
        res = get_required_defense(p, arrivals.get(p.id, {}), p.owner, min(MAX_SIM_TURNS, remaining))
        planet_available[p.id] = max(0, p.ships - res)

    # ====================================================
    # PRE-SORT SOURCE PLANETS (Front-line priority)
    # ====================================================
    # Sort planets by their best potential target base_score. 
    # Because distance heavily penalizes the score, front-line planets will process first.
    # They will claim the targets and update `arrivals`, forcing back-line 
    # planets to naturally fall through to the Funneling logic.
    src_priorities =[]
    for src in my_planets:
        available = planet_available[src.id]
        
        # Priority 1: Doomed planets evacuating this turn MUST go first
        if src.id in doomed_planets and doomed_planets[src.id] <= 1 and available > 0:
            src_priorities.append((float('inf'), src))
            continue
            
        max_base_score = -1.0
        if available >= 1:
            for tgt in planets:
                if src.id == tgt.id: continue
                
                d_val = max(1.0, dist(src.x, src.y, tgt.x, tgt.y))
                est_turns = d_val / fleet_speed(available)
                active_turns = max(1.0, remaining - est_turns)
                
                value = tgt.production * active_turns
                cost = max(1.0, tgt.ships)
                
                if tgt.owner != player and tgt.owner != -1:
                    value *= 2.0
                    cost = max(1.0, tgt.ships + (tgt.production * est_turns))
                
                base_score = (value / cost) / (d_val ** 1.1)
                
                if base_score > max_base_score:
                    max_base_score = base_score
                    
        src_priorities.append((max_base_score, src))
        
    # Sort descending (highest base score goes first)
    src_priorities.sort(key=lambda x: x[0], reverse=True)
    ordered_my_planets = [src for score, src in src_priorities]

    # ====================================================
    # COMMAND LOOP
    # ====================================================
    for src in ordered_my_planets:
        available = planet_available[src.id]
                
        # --- UNIFIED INDEFENSIBLE PLANET EVACUATION (Last Second Only) ---
        if src.id in doomed_planets:
            death_turn = doomed_planets[src.id]
            
            # If the end is more than 1 turn away, skip this planet entirely to hoard ships!
            if death_turn > 1:
                continue 
                
            if available > 0:
                best_tgt = None
                best_angle = None
                best_turns = None
                
                # Sort all possible targets by distance
                possible_targets =[]
                for f in my_planets:
                    if f.id != src.id and f.id not in doomed_planets and f.id not in comet_ids:
                        possible_targets.append((dist(src.x, src.y, f.x, f.y), f))
                for e in enemy_planets:
                    possible_targets.append((dist(src.x, src.y, e.x, e.y), e))
                
                possible_targets.sort(key=lambda x: x[0])
                
                # Exhaustive evaluation to pick the nearest guaranteed unblocked route.
                for _, tgt in possible_targets:
                    angle, turns = get_guaranteed_intercept(src, tgt, available, traj)
                    if angle is not None:
                        # Ensures paths don't hit planets or the sun
                        if not path_blocked_by_planet(src, tgt, angle, available, planets, traj, turns):
                            best_tgt = tgt
                            best_angle = angle
                            best_turns = turns
                            break
                            
                if best_tgt:
                    moves.append([src.id, float(best_angle), int(available)])
                    arrivals[best_tgt.id][best_turns][player] += available
                    
                planet_available[src.id] = 0
                available = 0
            
            # Evacuated/Hoarding planets skip the Aggression Loop.
            continue
        
        if available < 1: continue
            
        # --- CONTEXT-AWARE AGGRESSION LOOP ---
        candidates =[]
        for tgt in planets:
            if src.id == tgt.id: continue
            
            d_val = max(1.0, dist(src.x, src.y, tgt.x, tgt.y))
            est_turns = d_val / fleet_speed(available)
            active_turns = max(1.0, remaining - est_turns)
            
            value = tgt.production * active_turns
            cost = max(1.0, tgt.ships)
            
            if tgt.owner != player and tgt.owner != -1:
                value *= 2.0
                cost = max(1.0, tgt.ships + (tgt.production * est_turns))
            
            base_score = (value / cost) / (d_val ** 1.1)
            candidates.append((base_score, tgt, value))
            
        candidates.sort(key=lambda x: -x[0])
        
        launched_attack = False
        
        while available >= 1: 
            best_move = None
            best_roi = -1.0
            best_tgt_obj = None
            
            for base_score, tgt, value in candidates:
                d_tgt = dist(src.x, src.y, tgt.x, tgt.y)
                
                best_req = get_min_ships_to_conquer(src, tgt, arrivals.get(tgt.id, {}), player, remaining, available, traj)
                if best_req is None: continue
                
                angle, turns = get_guaranteed_intercept(src, tgt, best_req, traj)
                if angle is None or turns > remaining: continue
                
                tgt_life = get_comet_lifespan(tgt.id, comets) if tgt.id in comet_ids else remaining
                if tgt_life <= turns: continue
                
                # --- CONTEXT CHECK: EXPANSION vs COMBAT ---
                is_expansion = (tgt.owner == -1)
                
                if is_expansion:
                    required_to_launch = best_req
                    speed_bonus = int(tgt.production * 5)
                    optimal_send = min(available, best_req + speed_bonus)
                else:
                    dynamic_batch_req = get_dynamic_batch_size(src.production, d_tgt)
                    required_to_launch = max(best_req, dynamic_batch_req)
                    optimal_send = max(required_to_launch, min(available, 1000))
                
                if available < required_to_launch: 
                    continue 
                    
                strict_angle, strict_turns = get_guaranteed_intercept(src, tgt, optimal_send, traj)
                if strict_angle is None or strict_turns > remaining or path_blocked_by_planet(src, tgt, strict_angle, optimal_send, planets, traj, strict_turns): 
                    continue
                
                V_A = evaluate_timeline(tgt, arrivals.get(tgt.id, {}), player, remaining, is_ffa, tgt_life)
                V_B_strict = evaluate_timeline(tgt, arrivals.get(tgt.id, {}), player, remaining, is_ffa, tgt_life, test_fleet=(strict_turns, optimal_send, player))
                
                profit = (V_B_strict - optimal_send) - V_A
                if profit > 0:
                    roi = (profit / max(1.0, float(optimal_send))) * value / (max(1.0, d_tgt) ** 1.1)
                        
                    if roi > best_roi:
                        best_roi = roi
                        best_move = (tgt.id, strict_angle, optimal_send, strict_turns)
                        best_tgt_obj = (base_score, tgt, value)
                        
            if best_move:
                tgt_id, angle, send, turns = best_move
                moves.append([src.id, float(angle), int(send)])
                arrivals[tgt_id][turns][player] += send
                planet_available[src.id] -= send
                available -= send
                candidates.remove(best_tgt_obj)
                launched_attack = True
            else:
                break
                
        # --- DYNAMIC FUNNELING (Supply Chain Routing) ---
        if available >= max(1, src.production) and not launched_attack and enemy_planets:
            closest_enemy = min(enemy_planets, key=lambda e: dist(src.x, src.y, e.x, e.y))
            d_enemy = dist(src.x, src.y, closest_enemy.x, closest_enemy.y)
            
            forward_friends =[
                f for f in my_planets 
                if f.id != src.id and f.id not in comet_ids 
                and dist(f.x, f.y, closest_enemy.x, closest_enemy.y) < d_enemy - 5.0
            ]
            
            if forward_friends:
                best_f = min(forward_friends, key=lambda f: dist(f.x, f.y, closest_enemy.x, closest_enemy.y))
                d_front = dist(src.x, src.y, best_f.x, best_f.y)
                
                dynamic_batch_req = get_dynamic_batch_size(src.production, d_front)
                
                speed_now = fleet_speed(available)
                speed_next = fleet_speed(available + src.production)
                turns_now = d_front / speed_now
                turns_next = 1.0 + (d_front / speed_next)
                
                owner_at_arrival, _ = simulate_planet(best_f, arrivals.get(best_f.id, {}), max_turn=int(turns_now)+1)
                
                if available >= dynamic_batch_req and turns_now <= turns_next and owner_at_arrival == player:
                    send = available
                    angle, turns = get_guaranteed_intercept(src, best_f, send, traj)
                    if angle is not None and not path_blocked_by_planet(src, best_f, angle, send, planets, traj, turns):
                        moves.append([src.id, float(angle), int(send)])
                        arrivals[best_f.id][turns][player] += send
                        planet_available[src.id] -= send
                        available -= send

    return moves
