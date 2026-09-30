"""The game engine: the only place where GameState changes.

    game = Game.new(["Anna", "Bram", "Carla"], seed=1)
    while not game.finished:
        pid = game.pending_actors()[0]
        game.apply(pid, choose(game.view(pid), game.legal_actions(pid)))

`legal_actions()` enumerates every legal move, except trade offers: it lists a canonical set of
simple offers (one card for one card, to everyone). `apply()` accepts any valid offer.
"""

from __future__ import annotations

import copy
import itertools
import random
from collections.abc import Iterator, Sequence
from typing import Any

from . import actions as A
from .board import RESOURCES, beginner_layout, random_layout
from .board import TOPOLOGY as T
from .projection import to_player_view
from .rules import awards, placement, production, scoring, trading
from .state import COSTS, DEV_DECK, PLAYER_COLORS, Config, GameState, Player, TradeOffer


class RuleError(Exception):
    """An illegal action. `code` is stable and machine-readable (e.g. for the API)."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def _require(cond: bool, code: str) -> None:
    if not cond:
        raise RuleError(code)


def _snake(n: int) -> list[int]:
    return list(range(n)) + list(reversed(range(n)))


def _combinations(hand: dict[str, int], size: int) -> Iterator[dict[str, int]]:
    """Every multiset of `size` cards drawable from `hand`."""
    res = [r for r in RESOURCES if hand[r] > 0]

    def rec(i: int, left: int, acc: dict[str, int]) -> Iterator[dict[str, int]]:
        if left == 0:
            yield dict(acc)
            return
        if i == len(res):
            return
        r = res[i]
        for n in range(min(hand[r], left), -1, -1):
            if n:
                acc[r] = n
            yield from rec(i + 1, left - n, acc)
            acc.pop(r, None)

    yield from rec(0, size, {})


class Game:
    def __init__(self, state: GameState, record: bool = False) -> None:
        self.state = state
        self.history: list[tuple[str, dict[str, Any]]] | None = [] if record else None

    # ----- construction -------------------------------------------------------------------

    @classmethod
    def new(
        cls,
        names: Sequence[str],
        seed: int,
        *,
        layout: str = "random",
        config: Config | None = None,
        game_id: str = "game",
        record: bool = False,
    ) -> Game:
        if not 2 <= len(names) <= 4:
            raise ValueError("Catan needs 2 to 4 players")
        rng = random.Random(seed)
        board = random_layout(rng) if layout == "random" else beginner_layout()
        deck = list(DEV_DECK)
        rng.shuffle(deck)
        players = [Player(id=f"p{i + 1}", name=n, color=PLAYER_COLORS[i]) for i, n in enumerate(names)]
        state = GameState(
            id=game_id,
            layout=board,
            players=players,
            rng=rng,
            config=config or Config(),
            robber=board.desert,
            dev_deck=deck,
        )
        return cls(state, record=record)

    def clone(self) -> Game:
        """Independent copy (including the RNG), e.g. for lookahead in agents."""
        return Game(copy.deepcopy(self.state))

    # ----- queries ------------------------------------------------------------------------

    @property
    def finished(self) -> bool:
        return self.state.phase == "finished"

    @property
    def winner_id(self) -> str | None:
        s = self.state
        return None if s.winner is None else s.players[s.winner].id

    def pending_actors(self) -> list[str]:
        """Players who must act now, in seat order. Usually just the current player."""
        s = self.state
        if s.phase == "finished":
            return []
        if s.step == "discard":
            return [s.players[p].id for p in sorted(s.pending_discards)]
        if s.trade is not None:
            waiting = [pid for pid in s.trade.to if s.trade.responses[pid] is None]
            if waiting:
                return waiting
        return [s.current_player.id]

    def view(self, player_id: str) -> dict[str, Any]:
        return to_player_view(self.state, player_id)

    def points(self, player_id: str) -> int:
        return scoring.total_points(self.state, self.state.player_index(player_id))

    def legal_actions(self, player_id: str) -> list[A.Action]:
        s = self.state
        p = s.player_index(player_id)
        if player_id not in self.pending_actors():
            # The offerer may withdraw an open offer while others are still answering.
            if s.trade is not None and s.trade.offerer == player_id:
                return [A.CancelTrade()]
            return []
        if s.step == "setupSettlement":
            return [A.PlaceSetupSettlement(v) for v in placement.setup_settlement_spots(s)]
        if s.step == "setupRoad":
            return [A.PlaceSetupRoad(e) for e in placement.setup_road_spots(s)]
        if s.step == "discard":
            return [
                A.Discard(A.bundle(c)) for c in _combinations(s.players[p].resources, s.pending_discards[p])
            ]
        if s.step == "moveRobber":
            out: list[A.Action] = []
            for h in placement.robber_hexes(s):
                victims = placement.steal_victims(s, h, p)
                if victims:
                    out.extend(A.MoveRobber(h, s.players[v].id) for v in victims)
                else:
                    out.append(A.MoveRobber(h))
            return out
        if s.step == "roadBuilding":
            return [A.BuildRoad(e) for e in placement.road_spots(s, p)]
        if s.trade is not None:
            return self._legal_trade_actions(p)
        if s.step == "roll":
            return [A.Roll(), *self._legal_dev_plays(p)]
        if s.step == "action":
            return self._legal_main_actions(p)
        return []

    def _legal_dev_plays(self, p: int) -> list[A.Action]:
        s = self.state
        pl = s.players[p]
        if s.dev_played_this_turn:
            return []
        out: list[A.Action] = []
        if pl.dev_cards["knight"]:
            out.append(A.PlayKnight())
        if pl.dev_cards["roadBuilding"] and placement.road_spots(s, p):
            out.append(A.PlayRoadBuilding())
        if pl.dev_cards["yearOfPlenty"]:
            for a, b in itertools.combinations_with_replacement(RESOURCES, 2):
                need = {a: 1} if a != b else {a: 2}
                if b != a:
                    need[b] = 1
                if all(s.bank[r] >= n for r, n in need.items()):
                    out.append(A.PlayYearOfPlenty(A.bundle(need)))
        if pl.dev_cards["monopoly"]:
            out.extend(A.PlayMonopoly(r) for r in RESOURCES)
        return out

    def _legal_main_actions(self, p: int) -> list[A.Action]:
        s = self.state
        pl = s.players[p]
        out: list[A.Action] = []
        if pl.can_pay(COSTS["settlement"]):
            out.extend(A.BuildSettlement(v) for v in placement.settlement_spots(s, p))
        if pl.can_pay(COSTS["city"]):
            out.extend(A.BuildCity(v) for v in placement.city_spots(s, p))
        if pl.can_pay(COSTS["road"]):
            out.extend(A.BuildRoad(e) for e in placement.road_spots(s, p))
        if pl.can_pay(COSTS["devCard"]) and s.dev_deck:
            out.append(A.BuyDevCard())
        out.extend(self._legal_dev_plays(p))
        rates = trading.trade_rates(s, p)
        for give in RESOURCES:
            if pl.resources[give] >= rates[give]:
                out.extend(A.BankTrade(give, get) for get in RESOURCES if get != give and s.bank[get] > 0)
        if self._may_offer():
            others = tuple(o.id for i, o in enumerate(s.players) if i != p)
            for give in RESOURCES:
                if pl.resources[give] > 0:
                    out.extend(
                        A.OfferTrade(((give, 1),), ((get, 1),), others) for get in RESOURCES if get != give
                    )
        out.append(A.EndTurn())
        return out

    def _may_offer(self) -> bool:
        cap = self.state.config.trade_offers_per_turn
        return cap is None or self.state.trade_offers_this_turn < cap

    def _legal_trade_actions(self, p: int) -> list[A.Action]:
        s = self.state
        t = s.trade
        if t is None:
            return []
        pid = s.players[p].id
        if pid != t.offerer:
            accept = s.players[p].can_pay(t.get)
            return [A.RespondTrade(True), A.RespondTrade(False)] if accept else [A.RespondTrade(False)]
        out: list[A.Action] = []
        if s.players[p].can_pay(t.give):
            out.extend(
                A.ConfirmTrade(o)
                for o, ok in t.responses.items()
                if ok and s.players[s.player_index(o)].can_pay(t.get)
            )
        out.append(A.CancelTrade())
        return out

    # ----- applying actions ---------------------------------------------------------------

    def apply(self, player_id: str, action: A.Action) -> None:
        s = self.state
        _require(s.phase != "finished", "gameOver")
        try:
            p = s.player_index(player_id)
        except KeyError:
            raise RuleError("unknownPlayer") from None
        is_withdrawal = (
            isinstance(action, A.CancelTrade) and s.trade is not None and s.trade.offerer == player_id
        )
        _require(player_id in self.pending_actors() or is_withdrawal, "notYourTurn")
        handler = getattr(self, f"_do_{action.type}", None)
        if handler is None:
            raise RuleError("unknownAction")
        handler(p, action)
        if self.history is not None:
            self.history.append((player_id, A.action_to_dict(action)))
        self._check_winner()

    def _check_winner(self) -> None:
        s = self.state
        if s.phase == "playing" and scoring.total_points(s, s.current) >= s.config.win_points:
            s.phase = "finished"
            s.step = "finished"
            s.winner = s.current
            s.trade = None

    def _pay(self, p: int, cost: dict[str, int]) -> None:
        pl = self.state.players[p]
        _require(pl.can_pay(cost), "cannotAfford")
        for r, n in cost.items():
            pl.resources[r] -= n
            self.state.bank[r] += n

    def _step(self, *steps: str) -> None:
        _require(self.state.step in steps, "wrongStep")

    def _no_open_trade(self) -> None:
        _require(self.state.trade is None, "tradeOpen")

    # setup

    def _do_placeSetupSettlement(self, p: int, a: A.PlaceSetupSettlement) -> None:
        s = self.state
        self._step("setupSettlement")
        _require(0 <= a.vertex < T.num_vertices and placement.distance_ok(s, a.vertex), "illegalPlacement")
        s.buildings[a.vertex] = (p, "settlement")
        s.players[p].settlements_left -= 1
        s.last_setup_vertex = a.vertex
        if s.setup_index >= len(s.players):
            production.setup_income(s, p, a.vertex)
        s.step = "setupRoad"

    def _do_placeSetupRoad(self, p: int, a: A.PlaceSetupRoad) -> None:
        s = self.state
        self._step("setupRoad")
        _require(a.edge in placement.setup_road_spots(s), "illegalPlacement")
        s.roads[a.edge] = p
        s.players[p].roads_left -= 1
        s.setup_index += 1
        order = _snake(len(s.players))
        if s.setup_index == len(order):
            s.phase = "playing"
            s.step = "roll"
            s.current = 0
            s.turn_number = 1
            s.last_setup_vertex = None
        else:
            s.current = order[s.setup_index]
            s.step = "setupSettlement"

    # rolling and the robber

    def _do_roll(self, p: int, a: A.Roll) -> None:
        s = self.state
        self._step("roll")
        self._no_open_trade()
        d = (s.rng.randint(1, 6), s.rng.randint(1, 6))
        s.dice = d
        total = d[0] + d[1]
        if total == 7:
            s.pending_discards = {
                i: pl.card_count() // 2 for i, pl in enumerate(s.players) if pl.card_count() > 7
            }
            s.return_step = "action"
            s.step = "discard" if s.pending_discards else "moveRobber"
        else:
            production.produce(s, total)
            s.step = "action"

    def _do_discard(self, p: int, a: A.Discard) -> None:
        s = self.state
        self._step("discard")
        cards = A.unbundle(a.resources)
        _require(p in s.pending_discards, "nothingToDiscard")
        _require(
            sum(cards.values()) == s.pending_discards[p] and all(n > 0 for n in cards.values()), "wrongAmount"
        )
        _require(all(r in RESOURCES for r in cards), "unknownResource")
        self._pay(p, cards)
        del s.pending_discards[p]
        if not s.pending_discards:
            s.step = "moveRobber"

    def _do_moveRobber(self, p: int, a: A.MoveRobber) -> None:
        s = self.state
        self._step("moveRobber")
        _require(0 <= a.hex < len(T.hexes) and a.hex != s.robber, "illegalRobberHex")
        victims = [s.players[v].id for v in placement.steal_victims(s, a.hex, p)]
        if victims:
            _require(a.steal_from in victims, "illegalVictim")
        else:
            _require(a.steal_from is None, "illegalVictim")
        s.robber = a.hex
        if a.steal_from is not None:
            victim = s.players[s.player_index(a.steal_from)]
            pool = [r for r in RESOURCES for _ in range(victim.resources[r])]
            card = s.rng.choice(pool)
            victim.resources[card] -= 1
            s.players[p].resources[card] += 1
        s.step = s.return_step

    # building

    def _do_buildRoad(self, p: int, a: A.BuildRoad) -> None:
        s = self.state
        self._step("action", "roadBuilding")
        self._no_open_trade()
        _require(0 <= a.edge < T.num_edges, "illegalPlacement")
        _require(s.players[p].roads_left > 0, "noPiecesLeft")
        _require(placement.road_connects(s, a.edge, p), "illegalPlacement")
        if s.step == "action":
            self._pay(p, COSTS["road"])
        s.roads[a.edge] = p
        s.players[p].roads_left -= 1
        awards.update_longest_road(s)
        if s.step == "roadBuilding":
            s.road_building_left -= 1
            if s.road_building_left == 0 or not placement.road_spots(s, p):
                s.road_building_left = 0
                s.step = s.return_step

    def _do_buildSettlement(self, p: int, a: A.BuildSettlement) -> None:
        s = self.state
        self._step("action")
        self._no_open_trade()
        _require(a.vertex in placement.settlement_spots(s, p), "illegalPlacement")
        self._pay(p, COSTS["settlement"])
        s.buildings[a.vertex] = (p, "settlement")
        s.players[p].settlements_left -= 1
        awards.update_longest_road(s)  # a settlement can break an opponent's road

    def _do_buildCity(self, p: int, a: A.BuildCity) -> None:
        s = self.state
        self._step("action")
        self._no_open_trade()
        _require(a.vertex in placement.city_spots(s, p), "illegalPlacement")
        self._pay(p, COSTS["city"])
        s.buildings[a.vertex] = (p, "city")
        s.players[p].settlements_left += 1
        s.players[p].cities_left -= 1

    # development cards

    def _do_buyDevCard(self, p: int, a: A.BuyDevCard) -> None:
        s = self.state
        self._step("action")
        self._no_open_trade()
        _require(bool(s.dev_deck), "deckEmpty")
        self._pay(p, COSTS["devCard"])
        s.players[p].new_dev_cards[s.dev_deck.pop()] += 1

    def _start_dev_play(self, p: int, card: str) -> None:
        s = self.state
        self._step("roll", "action")
        self._no_open_trade()
        _require(not s.dev_played_this_turn, "devCardAlreadyPlayed")
        _require(s.players[p].dev_cards[card] > 0, "noSuchCard")
        s.players[p].dev_cards[card] -= 1
        s.players[p].played_dev_cards[card] += 1
        s.dev_played_this_turn = True

    def _do_playKnight(self, p: int, a: A.PlayKnight) -> None:
        s = self.state
        self._start_dev_play(p, "knight")
        s.players[p].knights_played += 1
        awards.update_largest_army(s, p)
        s.return_step = s.step
        s.step = "moveRobber"

    def _do_playRoadBuilding(self, p: int, a: A.PlayRoadBuilding) -> None:
        s = self.state
        _require(bool(placement.road_spots(s, p)), "illegalPlacement")
        self._start_dev_play(p, "roadBuilding")
        s.road_building_left = min(2, s.players[p].roads_left)
        s.return_step = s.step
        s.step = "roadBuilding"

    def _do_playYearOfPlenty(self, p: int, a: A.PlayYearOfPlenty) -> None:
        s = self.state
        cards = A.unbundle(a.resources)
        _require(
            sum(cards.values()) == 2 and all(r in RESOURCES and n > 0 for r, n in cards.items()),
            "wrongAmount",
        )
        _require(all(s.bank[r] >= n for r, n in cards.items()), "bankEmpty")
        self._start_dev_play(p, "yearOfPlenty")
        for r, n in cards.items():
            s.bank[r] -= n
            s.players[p].resources[r] += n

    def _do_playMonopoly(self, p: int, a: A.PlayMonopoly) -> None:
        s = self.state
        _require(a.resource in RESOURCES, "unknownResource")
        self._start_dev_play(p, "monopoly")
        for i, other in enumerate(s.players):
            if i != p:
                s.players[p].resources[a.resource] += other.resources[a.resource]
                other.resources[a.resource] = 0

    # trading

    def _do_bankTrade(self, p: int, a: A.BankTrade) -> None:
        s = self.state
        self._step("action")
        self._no_open_trade()
        _require(a.give in RESOURCES and a.get in RESOURCES and a.give != a.get, "unknownResource")
        _require(s.bank[a.get] > 0, "bankEmpty")
        self._pay(p, {a.give: trading.trade_rates(s, p)[a.give]})
        s.bank[a.get] -= 1
        s.players[p].resources[a.get] += 1

    def _do_offerTrade(self, p: int, a: A.OfferTrade) -> None:
        s = self.state
        self._step("action")
        self._no_open_trade()
        _require(p == s.current, "notYourTurn")
        _require(self._may_offer(), "tooManyOffers")
        give, get = A.unbundle(a.give), A.unbundle(a.get)
        valid = all(r in RESOURCES and n > 0 for r, n in (*give.items(), *get.items()))
        _require(valid and bool(give) and bool(get) and not (give.keys() & get.keys()), "invalidOffer")
        _require(s.players[p].can_pay(give), "cannotAfford")
        others = {o.id for i, o in enumerate(s.players) if i != p}
        _require(bool(a.to) and len(set(a.to)) == len(a.to) and set(a.to) <= others, "invalidOffer")
        s.trade = TradeOffer(s.players[p].id, give, get, list(a.to), responses=dict.fromkeys(a.to))
        s.trade_offers_this_turn += 1

    def _do_respondTrade(self, p: int, a: A.RespondTrade) -> None:
        s = self.state
        t = s.trade
        if t is None:
            raise RuleError("noOpenTrade")
        pid = s.players[p].id
        _require(pid in t.responses and t.responses[pid] is None, "notAddressed")
        _require(not a.accept or s.players[p].can_pay(t.get), "cannotAfford")
        t.responses[pid] = a.accept
        if all(v is False for v in t.responses.values()):
            s.trade = None  # everyone declined

    def _do_confirmTrade(self, p: int, a: A.ConfirmTrade) -> None:
        s = self.state
        t = s.trade
        if t is None or t.offerer != s.players[p].id:
            raise RuleError("noOpenTrade")
        _require(t.responses.get(a.with_player) is True, "notAccepted")
        other = s.player_index(a.with_player)
        _require(s.players[p].can_pay(t.give) and s.players[other].can_pay(t.get), "cannotAfford")
        for r, n in t.give.items():
            s.players[p].resources[r] -= n
            s.players[other].resources[r] += n
        for r, n in t.get.items():
            s.players[other].resources[r] -= n
            s.players[p].resources[r] += n
        s.trade = None

    def _do_cancelTrade(self, p: int, a: A.CancelTrade) -> None:
        s = self.state
        _require(s.trade is not None and s.trade.offerer == s.players[p].id, "noOpenTrade")
        s.trade = None

    # end of turn

    def _do_endTurn(self, p: int, a: A.EndTurn) -> None:
        s = self.state
        self._step("action")
        pl = s.players[p]
        for card, n in pl.new_dev_cards.items():
            pl.dev_cards[card] += n
            pl.new_dev_cards[card] = 0
        s.trade = None
        s.current = (s.current + 1) % len(s.players)
        s.turn_number += 1
        s.step = "roll"
        s.dice = None
        s.dev_played_this_turn = False
        s.trade_offers_this_turn = 0
