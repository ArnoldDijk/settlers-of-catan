"""Summary statistics over many GameResults."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field

from .runner import GameResult


@dataclass(slots=True)
class Summary:
    games: int = 0
    seats: int = 0
    capped: int = 0
    turns_total: int = 0
    seat_wins: Counter[int] = field(default_factory=Counter)
    agent_wins: Counter[str] = field(default_factory=Counter)
    agent_seats: Counter[str] = field(default_factory=Counter)

    def add(self, r: GameResult) -> None:
        self.games += 1
        self.turns_total += r.turns
        self.seats = max(self.seats, len(r.agents))
        self.agent_seats.update(r.agents)
        if r.winner is None:
            self.capped += 1
        else:
            self.seat_wins[r.winner] += 1
            self.agent_wins[r.agents[r.winner]] += 1

    def format(self) -> str:
        if not self.games:
            return "No games played."
        lines = [
            f"Games: {self.games}  finished: {self.games - self.capped}  hit turn cap: {self.capped}",
            f"Average length: {self.turns_total / self.games:.1f} turns",
            "Win rate per agent (wins / seats played):",
        ]
        for agent, seats in sorted(self.agent_seats.items()):
            wins = self.agent_wins[agent]
            lines.append(f"  {agent:<24} {wins / seats:6.1%}  ({wins}/{seats})")
        lines.append("Win rate per seat:")
        for s in range(self.seats):
            lines.append(f"  seat {s + 1}: {self.seat_wins[s] / self.games:6.1%}")
        return "\n".join(lines)


def summarize(results: Iterable[GameResult]) -> Summary:
    s = Summary()
    for r in results:
        s.add(r)
    return s
