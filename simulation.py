from typing import List, Tuple
from dataclasses import dataclass
from itertools import cycle
from enum import Enum, auto
import random

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