from catan_engine import actions as A
from catan_engine.board import TOPOLOGY as T
from catan_engine.rules import awards
from tests.conftest import give, place, playing


def path(start: int, n: int) -> list[int]:
    """n connected edges forming a simple path (no vertex twice) from vertex `start`."""

    def dfs(v: int, seen: set[int], edges: list[int]) -> list[int] | None:
        if len(edges) == n:
            return edges
        for e in T.vertex_edges[v]:
            w = next(x for x in T.edge_vertices[e] if x != v)
            if w not in seen:
                found = dfs(w, seen | {w}, [*edges, e])
                if found:
                    return found
        return None

    result = dfs(start, {start}, [])
    assert result is not None
    return result


def test_longest_road_needs_five_segments() -> None:
    g = playing()
    roads = path(T.hex_vertices[0][0], 5)
    place(g, 0, roads=roads[:4])
    awards.update_longest_road(g.state)
    assert g.state.longest_road is None
    place(g, 0, roads=roads[4:])
    awards.update_longest_road(g.state)
    assert g.state.longest_road == 0
    assert awards.longest_road_length(g.state, 0) == 5


def test_tie_keeps_the_holder_and_longer_road_takes_it() -> None:
    g = playing()
    place(g, 0, roads=path(T.hex_vertices[0][0], 5))
    awards.update_longest_road(g.state)
    far = path(T.hex_vertices[18][3], 6)
    place(g, 1, roads=far[:5])
    awards.update_longest_road(g.state)
    assert g.state.longest_road == 0  # tie: holder keeps it
    place(g, 1, roads=far[5:])
    awards.update_longest_road(g.state)
    assert g.state.longest_road == 1


def test_opponent_settlement_breaks_a_road() -> None:
    g = playing()
    roads = path(T.hex_vertices[0][0], 6)
    place(g, 0, roads=roads)
    awards.update_longest_road(g.state)
    assert g.state.longest_road == 0
    middle = set(T.edge_vertices[roads[2]]) & set(T.edge_vertices[roads[3]])
    place(g, 1, settlements=list(middle))
    awards.update_longest_road(g.state)
    assert awards.longest_road_length(g.state, 0) == 3
    assert g.state.longest_road is None


def test_largest_army_at_three_knights_and_must_be_beaten() -> None:
    g = playing()
    g.state.players[0].knights_played = 3
    awards.update_largest_army(g.state, 0)
    assert g.state.largest_army == 0
    g.state.players[1].knights_played = 3
    awards.update_largest_army(g.state, 1)
    assert g.state.largest_army == 0
    g.state.players[1].knights_played = 4
    awards.update_largest_army(g.state, 1)
    assert g.state.largest_army == 1


def test_ten_points_on_your_own_turn_wins() -> None:
    g = playing()
    corners = [T.hex_vertices[h][0] for h in (0, 2, 7, 11, 16)]
    place(g, 0, cities=corners[:4], settlements=corners[4:])  # 9 points
    g.state.dev_deck.append("victoryPoint")
    give(g, 0, wool=1, grain=1, ore=1)
    g.apply("p1", A.BuyDevCard())  # 10th point, hidden
    assert g.finished
    assert g.winner_id == "p1"
    assert g.pending_actors() == []


def test_points_count_only_on_your_own_turn() -> None:
    g = playing()
    corners = [T.hex_vertices[h][0] for h in (0, 2, 7, 11, 16)]
    place(g, 1, cities=corners)  # p2 has 10 points, but it's p1's turn
    give(g, 0, lumber=4)
    g.apply("p1", A.BankTrade("lumber", "ore"))
    assert not g.finished
    g.apply("p1", A.EndTurn())  # p2's turn starts with 10 points: p2 wins
    assert g.finished and g.winner_id == "p2"
