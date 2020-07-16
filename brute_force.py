from typing import List, Tuple
from statistics import mean
from multiprocessing import Pool, cpu_count, freeze_support
from multiprocessing.dummy import Pool as TPool
import json
from tqdm import tqdm
from simulation import Player


team = [
    # Name, Strikoute, Contact Rate, On Base Rate, Extra Base Rate
    Player('A', .400, .500, .300, .050),
    Player('B', .400, .500, .300, .050),
    Player('C', .400, .400, .300, .050),
    Player('D', .400, .400, .250, .200),
    Player('E', .500, .400, .250, .100),
    Player('F', .500, .300, .100, .050),
    Player('G', .600, .300, .100, .050),
    Player('H', .600, .300, .100, .050),
    Player('I', .600, .200, .050, .050),
    # Player('J', .600, .200, .050, .050),
    # Player('K', .600, .200, .050, .050),
]

def single_simulation():
    single_game = Game(team, debug=True)
    print(single_game.simulate())

def simulate_team(team: List[Player]) -> int:
    return Game(team).simulate()


### Brute Force Optimization
def lineup_expected_value(team: List[Player], iterations: int = 1000) -> float:
    with TPool(16) as pool:
        results = pool.map(simulate_team, repeat(team, iterations))
    return mean(results)

def evaulate_lineup(lineup: List[Player]) -> Tuple[str, float]:
    lineup_name = "".join(player.name for player in lineup)
    expected_value = lineup_expected_value(lineup)
    # print(f"{lineup_name=} {expected_value=}")
    return lineup_name, expected_value

if __name__ == "__main__":
    total = sum(1 for _ in permutations(team))
    print(f"Brute Forcing {total} lineups")
    freeze_support()

    with Pool(cpu_count()) as pool:
        lineup_values = dict(tqdm(pool.imap_unordered(evaulate_lineup, permutations(team)), total=total))

    print(f'{lineup_values=}')
    print(sorted(lineup_values, key=lineup_values.get))
    with open('output.json', 'w') as output_file:
        json.dump(lineup_values, output_file)
