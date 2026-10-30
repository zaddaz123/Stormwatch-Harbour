"""Stormwatch Harbour: reproducible, simple multi-agent grid simulation.
Run: python run.py --seed 11 --policy model --out results/demo.json
Run all experiments: python run.py --all
"""
import random
import argparse
import json

WIDTH, HEIGHT, RUN_TICKS = 24, 16, 600
BERTHS = {"B1": (3, 0), "B2": (9, 0), "B3": (15, 0), "B4": (21, 0)}
WAREHOUSE = (1, 15)
WORKERS = 10
CARGO = 8
STORM_STARTS = [150, 320, 490]
SAFE = {'B2', 'B3'}


def step_towards(pos, dst):
    x, y = pos
    if x != dst[0]: x += 1 if x < dst[0] else -1
    elif y != dst[1]: y += 1 if y < dst[1] else -1
    return (x, y)


def simulate(seed=11, policy='model'):
    assert policy in ('baseline', 'model')
    rng = random.Random(seed)
    workers = [{'pos': WAREHOUSE, 'cargo': False, 'target': None, 'warning_memory': -1, 'knocked': -1} for _ in range(WORKERS)]
    berth_ships = {name: None for name in BERTHS}
    waiting = []
    next_ship = 0
    ship_id = 0
    delivered = knockouts = invalid = fallback = 0
    warnings_sent = 0
    # Report is not allowed to override the system's fixed security rules.
    for tick in range(RUN_TICKS):
        warning = any(start - 5 <= tick < start for start in STORM_STARTS)
        storm = any(start <= tick < start + 15 for start in STORM_STARTS)
        if warning: warnings_sent += 1
        if tick == next_ship:
            ship_id += 1
            waiting.append({'id': ship_id, 'remaining': CARGO})
            next_ship += rng.randint(6, 10)
        # The Quartermaster assigns waiting ships to unoccupied berths.
        # In model/LLM policies, ships are held away from unsafe berths if danger is known.
        danger_known = storm or warning
        for name in BERTHS:
            if berth_ships[name] is None and waiting:
                if policy == 'model' and danger_known and name not in SAFE:
                    continue
                berth_ships[name] = waiting.pop(0)
        for worker in workers:
            if worker['knocked'] >= tick: continue
            # Baseline ignores the warning. Model/LLM store warning for the following five ticks.
            if warning and policy == 'model': worker['warning_memory'] = tick + 5
            remembered_danger = policy == 'model' and (storm or warning or worker['warning_memory'] >= tick)
            # Workers must drop current dangerous assignment and walk to safety.
            if remembered_danger and worker['target'] not in SAFE and worker['target'] is not None and not worker['cargo']:
                worker['target'] = None
            if worker['cargo']:
                if worker['pos'] == WAREHOUSE:
                    worker['cargo'] = False
                    delivered += 1
                else:
                    worker['pos'] = step_towards(worker['pos'], WAREHOUSE)
                continue
            choices = [(name, ship) for name, ship in berth_ships.items() if ship and ship['remaining'] > 0
                       and (not remembered_danger or name in SAFE)]
            if worker['target'] not in [name for name, _ in choices]:
                worker['target'] = min(choices, key=lambda b: abs(worker['pos'][0] - BERTHS[b[0]][0]) + worker['pos'][1])[0] if choices else None
            target = worker['target']
            if target is None: continue
            # Unsafe location in an active storm causes a 15-tick knock-out.
            if storm and target not in SAFE and worker['pos'] == BERTHS[target]:
                knockouts += 1
                worker['knocked'] = tick + 14
                worker['target'] = None
                continue
            if worker['pos'] == BERTHS[target]:
                ship = berth_ships[target]
                if ship and ship['remaining'] > 0:
                    ship['remaining'] -= 1
                    worker['cargo'] = True
                    if ship['remaining'] == 0: berth_ships[target] = None
                else: worker['target'] = None
            else:
                worker['pos'] = step_towards(worker['pos'], BERTHS[target])
    return {'seed': seed, 'policy': policy, 'cargo_delivered': delivered,
            'storm_knockouts': knockouts, 'ships_created': ship_id}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stormwatch Harbour simulation")
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--policy", choices=["baseline", "model"], default="model")
    args = parser.parse_args()
    result = simulate(seed=args.seed, policy=args.policy)
    print(json.dumps(result, indent=2))
