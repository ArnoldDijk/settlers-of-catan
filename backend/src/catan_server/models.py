"""API wire models. Responses are serialized through these models, so they act as an allowlist:
a field that isn't declared here can never reach a browser."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Resource = Literal["lumber", "brick", "wool", "grain", "ore"]
Terrain = Literal["forest", "hills", "pasture", "fields", "mountains", "desert"]
PlayerColor = Literal["red", "blue", "orange", "white"]
Step = Literal[
    "setupSettlement", "setupRoad", "roll", "discard", "moveRobber", "action", "roadBuilding", "finished"
]
Count = Annotated[int, Field(ge=0, le=19)]
Bundle = dict[Resource, Count]
PlayerId = Annotated[str, StringConstraints(pattern=r"^p[1-4]$")]
Index6 = Annotated[int, Field(ge=0, le=5)]
Coord = Annotated[int, Field(ge=-3, le=3)]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


# ----- board refs ---------------------------------------------------------------------------


class HexCoord(Model):
    q: Coord
    r: Coord


class VertexRef(HexCoord):
    corner: Index6


class EdgeRef(HexCoord):
    edge: Index6


# ----- actions (request bodies and legalActions) --------------------------------------------


class PlaceSetupSettlement(Model):
    type: Literal["placeSetupSettlement"]
    at: VertexRef


class PlaceSetupRoad(Model):
    type: Literal["placeSetupRoad"]
    at: EdgeRef


class Roll(Model):
    type: Literal["roll"]


class Discard(Model):
    type: Literal["discard"]
    resources: Bundle


class MoveRobber(Model):
    type: Literal["moveRobber"]
    to: HexCoord
    stealFrom: PlayerId | None = None


class BuildRoad(Model):
    type: Literal["buildRoad"]
    at: EdgeRef


class BuildSettlement(Model):
    type: Literal["buildSettlement"]
    at: VertexRef


class BuildCity(Model):
    type: Literal["buildCity"]
    at: VertexRef


class BuyDevCard(Model):
    type: Literal["buyDevCard"]


class PlayKnight(Model):
    type: Literal["playKnight"]


class PlayRoadBuilding(Model):
    type: Literal["playRoadBuilding"]


class PlayYearOfPlenty(Model):
    type: Literal["playYearOfPlenty"]
    resources: Bundle


class PlayMonopoly(Model):
    type: Literal["playMonopoly"]
    resource: Resource


class BankTrade(Model):
    type: Literal["bankTrade"]
    give: Resource
    get: Resource


class OfferTrade(Model):
    type: Literal["offerTrade"]
    give: Bundle
    get: Bundle
    to: Annotated[list[PlayerId], Field(min_length=1, max_length=3)]


class RespondTrade(Model):
    type: Literal["respondTrade"]
    accept: bool


class ConfirmTrade(Model):
    type: Literal["confirmTrade"]
    withPlayer: PlayerId


class CancelTrade(Model):
    type: Literal["cancelTrade"]


class EndTurn(Model):
    type: Literal["endTurn"]


Action = Annotated[
    PlaceSetupSettlement | PlaceSetupRoad | Roll | Discard | MoveRobber | BuildRoad | BuildSettlement
    | BuildCity | BuyDevCard | PlayKnight | PlayRoadBuilding | PlayYearOfPlenty | PlayMonopoly | BankTrade
    | OfferTrade | RespondTrade | ConfirmTrade | CancelTrade | EndTurn,
    Field(discriminator="type"),
]  # fmt: skip


# ----- the player view ----------------------------------------------------------------------


class Tile(HexCoord):
    terrain: Terrain
    number: Annotated[int, Field(ge=2, le=12)] | None


class Harbor(HexCoord):
    edge: Index6
    kind: Resource | Literal["any"]


class Board(Model):
    tiles: list[Tile]
    harbors: list[Harbor]
    robber: HexCoord


class Building(Model):
    owner: str
    kind: Literal["settlement", "city"]
    at: VertexRef


class Road(Model):
    owner: str
    at: EdgeRef


class DevCards(Model):
    knight: int
    roadBuilding: int
    yearOfPlenty: int
    monopoly: int
    victoryPoint: int


class PiecesLeft(Model):
    roads: int
    settlements: int
    cities: int


class PublicPlayer(Model):
    id: str
    name: str
    color: PlayerColor
    resourceCount: int
    devCardCount: int
    knightsPlayed: int
    playedDevCards: DevCards
    piecesLeft: PiecesLeft
    victoryPoints: int


class Hand(Model):
    resources: dict[Resource, int]
    devCards: DevCards
    newDevCards: DevCards


class Turn(Model):
    number: int
    currentPlayerId: str
    step: Step


class Bank(Model):
    resources: dict[Resource, int]
    devCardsLeft: int


class Awards(Model):
    longestRoad: str | None
    largestArmy: str | None


class TradeOfferView(Model):
    offerer: str
    give: dict[Resource, int]
    get: dict[Resource, int]
    to: list[str]
    responses: dict[str, bool | None]


class PlayerView(Model):
    """One player's view of the game: public information plus their own hand."""

    gameId: str
    viewerId: str
    version: int
    phase: Literal["setup", "playing", "finished"]
    turn: Turn
    dice: list[int] | None
    board: Board
    buildings: list[Building]
    roads: list[Road]
    players: list[PublicPlayer]
    hand: Hand
    bank: Bank
    awards: Awards
    winnerId: str | None
    trade: TradeOfferView | None
    pendingDiscards: dict[str, int]
    devCardPlayedThisTurn: bool
    roadBuildingLeft: int
    #: Everything the viewer may do right now. Trade offers are a sample of simple 1:1 offers;
    #: any valid offer is accepted.
    legalActions: list[Action]


# ----- other requests and responses ---------------------------------------------------------

PlayerName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=24)]


class CreateGameRequest(Model):
    players: Annotated[list[PlayerName], Field(min_length=2, max_length=4)]


class Seat(Model):
    playerId: str
    name: str
    color: PlayerColor
    #: Share this link with the player. The token sits in the URL fragment, which browsers never
    #: send to the server, so it doesn't end up in logs.
    joinUrl: str


class CreateGameResponse(Model):
    gameId: str
    seats: list[Seat]


class JoinRequest(Model):
    token: Annotated[str, StringConstraints(min_length=20, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")]


class JoinResponse(Model):
    gameId: str
    playerId: str


class ActionRequest(Model):
    expectedVersion: Annotated[int, Field(ge=0)]
    action: Action


class ErrorBody(Model):
    code: str
    detail: str
