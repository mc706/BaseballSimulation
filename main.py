from dataclasses import dataclass
from enum import Enum, auto
from itertools import cycle, permutations, repeat
import random
from typing import List, Tuple
from statistics import mean
from multiprocessing import Pool, cpu_count, freeze_support
from multiprocessing.dummy import Pool as TPool
import json

@dataclass(frozen=True)
class Player:
    name: str
    strikeout_chance: float
    contact_chance: float
    onbase_chance: float
    extrabase_chance: float

    @property
    def walk_chance(self):
        return 1.0 - self.strikeout_chance - self.contact_chance

    @property
    def hit_out_chance(self):
        return self.contact_chance - self.onbase_chance - self.extrabase_chance

    @property
    def outcome_chances(self):
        return [
            self.strikeout_chance,
            self.walk_chance,
            self.hit_out_chance,
            self.onbase_chance,
            self.extrabase_chance,
        ]

class AtBatOutcome(Enum):
    STRIKEOUT = auto()
    WALK = auto()
    HIT_OUT = auto()
    HIT = auto()
    EXTRA_BASE_HIT = auto()

class Game:
    def __init__(self, team: List[Player], innings: int = 7, debug: bool = False):
        self.lineup = cycle(team)
        self.num_innings = innings
        self.innings = []
        self.debug = debug

    def simulate(self) -> int:
        self.innings = [self.simulate_inning() for inning in range(self.num_innings)]
        self.score = sum(self.innings)
        return self.score

    def simulate_inning(self) -> int:
        outs = 0
        score = 0
        bases = [False, False, False]

        while outs < 3:
            player_at_bat = next(self.lineup)
            outcome = self.bat(player_at_bat)
            if outcome == AtBatOutcome.STRIKEOUT:
                outs += 1
            elif outcome == AtBatOutcome.WALK:
                bases.insert(0, True)
                score += int(bases.pop())
            elif outcome == AtBatOutcome.HIT_OUT:
                outs += 1
                bases.insert(0, False)
                score += int(bases.pop())
            elif outcome == AtBatOutcome.HIT:
                bases.insert(0, True)
                score += int(bases.pop())
            elif outcome == AtBatOutcome.EXTRA_BASE_HIT:
                bases.insert(0, True)
                score += int(bases.pop())
                bases.insert(0, False)
                score += int(bases.pop())
            if self.debug: print(f"{score=} {outs=} {bases=}")
        if self.debug: print("Inning Complete")
        return score

    def bat(self, player: Player) -> AtBatOutcome:
        outcome, *_ = random.choices(
            list(AtBatOutcome),
            weights=player.outcome_chances,
            k=1,
        )
        if self.debug: print(f"{player=} {outcome=}")
        return outcome

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
    with TPool(8) as pool:
        results = pool.map(simulate_team, repeat(team, iterations))
    return mean(results)

def evaulate_lineup(lineup: List[Player]) -> Tuple[str, float]:
    lineup_name = "".join(player.name for player in lineup)
    expected_value = lineup_expected_value(lineup)
    print(f"{lineup_name=} {expected_value=}")
    return lineup_name, expected_value

if __name__ == "__main__":
    print(sum(1 for _ in permutations(team)))
    freeze_support()
    with Pool(cpu_count()) as pool:
        lineup_values = dict(pool.imap_unordered(evaulate_lineup, permutations(team)))

    print(f'{lineup_values=}')
    print(sorted(lineup_values, key=lineup_values.get))
    with open('output.json', 'w') as output_file:
        json.dump(lineup_values, output_file)
