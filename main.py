from src.cls.game import BlackjackGame
from src.strategies.basic import get_blackjack_move
from src.cls.card import Card  # for type checking deck cards
from src.settings import SHUFFLE_PERCENTAGE, BET_AMOUNT

def print_cards(label, cards):
    # Build a string representation for a list of cards
    card_str = ' | '.join(str(card) for card in cards)
    print(f"{label}: {card_str}")

def print_separator():
    print("=" * 50)

def simulate_round(game):
    print_separator()
    print("New Round Starting")
    player = game.players[0]
    # Reset player's hand for the round
    player.hands[0].cards = []
    # Set default bet
    player.set_bet(BET_AMOUNT, hand_index=0)

    # Dealer hand is local (list of cards)
    dealer_hand = []

    # Deal initial cards:
    # player gets two cards
    for _ in range(2):
        card = game.deck.deal()
        if card:
            player.hit(card)
    # Dealer gets two cards
    for _ in range(2):
        card = game.deck.deal()
        if card:
            dealer_hand.append(card)

    # Dealer upcard (first card shown)
    dealer_upcard = {'rank': dealer_hand[0].rank, 'suit': dealer_hand[0].suit.value}

    # Show initial state:
    print_cards("Player's Hand", player.hands[0].cards)
    print(f"Player's Total: {player.hands[0].get_value()}")
    print_cards("Dealer Upcard", dealer_hand[:1])

    # Player's turn:
    hand = player.hands[0]
    move = None
    while True:
        total = hand.get_value()
        if total > 21:
            print("Player busts!")
            break

        player_hand_dict = [{'rank': card.rank, 'suit': card.suit.value} for card in hand.cards]
        move = get_blackjack_move(player_hand_dict, dealer_upcard, total)
        print(f"Suggested move: {move}")

        if move in ["S"]:  # Stand
            print("Player stands.")
            break
        elif move in ["H"]:  # Hit
            card = game.deck.deal()
            if card:
                print(f"Player hits and receives: {card}")
                player.hit(card)
                print_cards("Player's Hand", hand.cards)
            else:
                break
        elif move in ["D", "Ds"]:  # Double: double bet, hit one card, then stand
            player.set_bet(player.hands_bets[0] * 2, hand_index=0)
            card = game.deck.deal()
            if card:
                print(f"Player doubles and receives: {card}")
                player.hit(card)
                print_cards("Player's Hand", hand.cards)
            break
        else:
            print("Unexpected move. Player stands by default.")
            break

    player_total = hand.get_value()
    print(f"Player's Final Total: {player_total}")

    # Dealer's turn if player hasn't busted
    dealer_total = sum(card.value() for card in dealer_hand)
    if player_total <= 21:
        print_separator()
        print("Dealer's Turn:")
        print_cards("Dealer's Hand", dealer_hand)
        print(f"Dealer's Total: {dealer_total}")
        while dealer_total < 17:
            card = game.deck.deal()
            if not card:
                break
            dealer_hand.append(card)
            dealer_total = sum(card.value() for card in dealer_hand)
            print(f"Dealer hits and receives: {card}")
            print_cards("Dealer's Hand", dealer_hand)
            print(f"Dealer's New Total: {dealer_total}")
    else:
        print("Dealer wins by player bust.")

    # Determine outcome:
    bet = player.hands_bets[0]
    if player_total > 21:
        outcome = "lose"
        player.money -= bet
    elif dealer_total > 21 or player_total > dealer_total:
        outcome = "win"
        player.money += bet
    elif player_total == dealer_total:
        outcome = "push"  # no money exchanged
    else:
        outcome = "lose"
        player.money -= bet

    print_separator()
    print("Round Summary:")
    print_cards("Player's Final Hand", hand.cards)
    print(f"Player Total: {player_total}")
    print_cards("Dealer's Final Hand", dealer_hand)
    print(f"Dealer Total: {dealer_total}")
    print(f"Outcome: {outcome}, Bet: {bet}, Player Money: {player.money}\n")
    return outcome

def simulate_game():
    game = BlackjackGame(["Alice"])
    total_cards = len(game.deck.cards)
    print(f"Starting game with {total_cards} cards in the deck.")
    round_num = 1
    while 100 * len(game.deck.cards) / total_cards > 100 - SHUFFLE_PERCENTAGE:
        print_separator()
        print(f"Round {round_num} beginning...")
        simulate_round(game)
        round_num += 1

    print_separator()
    print("Game Over!")
    print("Final Player Money:", game.players[0].money)

if __name__ == "__main__":
    simulate_game()
