import random

class Deck:  # Creates and shuffles a 52 card deck
    def __init__(self):
        self.cards = [r + s for r in '23456789TJQKA' for s in '♠♥♦♣']
        random.shuffle(self.cards)

    def deal(self, num=1):
        return [self.cards.pop() for _ in range(num)]


# Calculates the value of each player's hand
def evaluate_hand(cards):
    value = 0
    aces = 0
    for card in cards:
        rank = card[0]
        if rank in 'TJQK':
            value += 10
        elif rank == 'A':  # Checks for aces, counts them as 11
            value += 11
            aces += 1
        else:
            value += int(rank)
    while value > 21 and aces:  # if above 21 handles aces going from 11 to 1
        value -= 10
        aces -= 1
    return value


# Basically a class defining the game itself
class BlackjackGame:
    def __init__(self):
        self.deck = Deck()  # creates deck
        self.player_hand = self.deck.deal(2)  # deals cards to each player
        self.dealer_hand = self.deck.deal(2)
        self.game_over = False  # ends the game
        self.result = None  # should store the result, hopefully for db implementation

    def player_hit(self):
        # Player wants another card
        if not self.game_over:
            self.player_hand.append(self.deck.deal()[0])
            if evaluate_hand(self.player_hand) > 21:
                self.game_over = True
                self.result = 'Player Busts – Dealer Wins'

    def player_stand(self):
        # player ends turn and now it goes to dealer
        if not self.game_over:
            self.dealer_play()

    def dealer_play(self):
        # dealer hits when below 17
        while evaluate_hand(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.deal()[0])
        self.game_over = True
        self.check_winner()

    def check_winner(self):
        # compares hands and delivers the result
        player_score = evaluate_hand(self.player_hand)
        dealer_score = evaluate_hand(self.dealer_hand)

        if player_score > 21:
            self.result = 'Player Busts – Dealer Wins'
        elif dealer_score > 21:
            self.result = 'Dealer Busts – Player Wins'
        elif player_score > dealer_score:
            self.result = 'Player Wins'
        elif dealer_score > player_score:
            self.result = 'Dealer Wins'
        else:
            self.result = 'Tie Game'

    def get_game_state(self):
        # This just displays the status of the game,
        # Might not be useful in final app but helpful while developing
        return {
            "player_hand": self.player_hand,
            "player_score": evaluate_hand(self.player_hand),
            "dealer_hand": self.dealer_hand if self.game_over else [self.dealer_hand[0], 'Hidden'],
            "dealer_score": evaluate_hand(self.dealer_hand) if self.game_over else '?',
            "game_over": self.game_over,
            "result": self.result
        }
