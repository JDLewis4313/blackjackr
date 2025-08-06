import pytest
from flask import session
from app import create_app
from domains.game.logic import Deck, evaluate_hand
from domains.game.routes import BlackjackGame

def test_deck_initialization():
    deck = Deck()
    assert len(deck.cards) == 52
    assert len(set(deck.cards)) == 52


def test_deck_deal_removes_cards():
    deck = Deck()
    dealt = deck.deal(5)
    assert len(dealt) == 5
    assert len(deck.cards) == 47


def test_deck_deal_default_one_card():
    deck = Deck()
    dealt = deck.deal()
    assert isinstance(dealt, list)
    assert len(dealt) == 1

@pytest.mark.parametrize("hand,expected", [
    (['5♠', '7♦'], 12),
    (['K♣', 'J♦'], 20),
    (['A♠', '7♦'], 18),
    (['A♠', '9♦', '5♥'], 15),
    (['A♠', 'A♦', '8♥'], 20),
    (['A♠', 'A♦', '8♥', 'A♣'], 21),
])
def test_evaluate_hand_variants(hand, expected):
    assert evaluate_hand(hand) == expected


def test_game_initial_state():
    game = BlackjackGame()
    assert len(game.player_hand) == 2
    assert len(game.dealer_hand) == 2
    assert not game.game_over
    assert game.result is None


def test_player_hit_adds_card_or_busts():
    game = BlackjackGame()
    prev_len = len(game.player_hand)
    game.player_hit()
    # Either 1 more card, or game is over due to bust
    assert len(game.player_hand) >= prev_len
    if evaluate_hand(game.player_hand) > 21:
        assert game.game_over
        assert game.result == 'Player Busts – Dealer Wins'


def test_player_stand_triggers_dealer_play():
    game = BlackjackGame()
    game.player_stand()
    assert game.game_over
    assert game.result in {
        'Player Wins',
        'Dealer Wins',
        'Tie Game',
        'Dealer Busts – Player Wins',
        'Player Busts – Dealer Wins',
    }


def test_get_game_state_keys():
    game = BlackjackGame()
    state = game.get_game_state()
    assert 'player_hand' in state
    assert 'dealer_hand' in state
    assert 'player_score' in state
    assert 'dealer_score' in state
    assert 'game_over' in state
    assert 'result' in state
