import csv

from src.cls.game import BlackjackGame
from src.cls.hand import Hand
from src.strategies.basic import get_blackjack_move, hi_lo_count
from src.cls.card import Card  # for type checking deck cards
from src.settings import SHUFFLE_PERCENTAGE, BET_AMOUNT, MAX_RESHUFFLE, ENABLE_CARD_COUNTING, MIN_BET, MAX_BET, \
    INITIAL_BALANCE, NUM_PLAYERS


def print_cards(label, cards):
    # Build a string representation for a list of cards
    card_str = ' | '.join(str(card) for card in cards)
    print(f"{label}: {card_str}")


def print_separator():
    print("=" * 50)


def handle_split(player, hand_index, game):
    # Split the hand into two separate hands
    hand = player.hands[hand_index]
    # add new hand
    player.add_hand(hand=Hand(), bet=player.hands_bets[hand_index])
    # remove one card from current hand and add it to the new hand
    card = hand.cards.pop()
    player.hands[hand_index + 1].add_card(card)


def simulate_round(game, running_count, bet_histogram):
    print_separator()
    print("New Round Starting")
    # Reinitialize players for new round
    for player in game.players:
        player.hands = [Hand()]
        adjusted_bet = get_bet_amount(running_count)
        bet_histogram[adjusted_bet] = bet_histogram.get(adjusted_bet, 0) + 1
        player.hands_bets = [adjusted_bet]
    # Dealer hand is local (list of cards)
    dealer_hand = []
    # Deal initial cards for each player
    for player in game.players:
        for _ in range(2):
            card = game.deck.deal()
            if card:
                if ENABLE_CARD_COUNTING:
                    running_count[0] += hi_lo_count(card.rank)
                player.hit(card)
    # Deal dealer two cards
    for _ in range(2):
        card = game.deck.deal()
        if card:
            if ENABLE_CARD_COUNTING:
                running_count[0] += hi_lo_count(card.rank)
            dealer_hand.append(card)
    dealer_upcard = {'rank': dealer_hand[0].rank, 'suit': dealer_hand[0].suit.value}
    # Show initial state for each player
    for player in game.players:
        print_cards(f"{player.name}'s Hand", player.hands[0].cards)
        print(f"{player.name}'s Total: {player.hands[0].get_value()}")
    print_cards("Dealer Upcard", dealer_hand[:1])
    if ENABLE_CARD_COUNTING:
        print(f"Running Count: {running_count[0]}")
    # Player's turn for each hand
    for player in game.players:
        # Using while-loop to process any newly added hands (from splits)
        i = 0
        while i < len(player.hands):
            hand = player.hands[i]
            player_total = play_hand(player, hand, dealer_upcard, game, running_count)
            i += 1
    # Dealer's turn if any player hasn't busted
    if any(hand.get_value() <= 21 for player in game.players for hand in player.hands):
        print_separator()
        print("Dealer's Turn:")
        print_cards("Dealer's Hand", dealer_hand)
        dealer_total = sum(card.value() for card in dealer_hand)
        print(f"Dealer's Total: {dealer_total}")
        while dealer_total < 17:
            card = game.deck.deal()
            if not card:
                break
            if ENABLE_CARD_COUNTING:
                running_count[0] += hi_lo_count(card.rank)
            dealer_hand.append(card)
            dealer_total = sum(card.value() for card in dealer_hand)
            print(f"Dealer hits and receives: {card}")
            print_cards("Dealer's Hand", dealer_hand)
            print(f"Dealer's New Total: {dealer_total}")
    else:
        dealer_total = sum(card.value() for card in dealer_hand)
        print("Dealer wins by all players bust.")
    # Determine outcome for each player's hand
    for player in game.players:
        for hand, bet in zip(player.hands, player.hands_bets):
            hand_value = hand.get_value()
            if hand_value > 21:
                outcome = "lose"
                player.money -= bet
            elif dealer_total > 21 or hand_value > dealer_total:
                outcome = "win"
                player.money += bet
            elif hand_value == dealer_total:
                outcome = "push"
            else:
                outcome = "lose"
                player.money -= bet
            print_separator()
            print(f"{player.name}'s Round Summary:")
            print_cards("Final Hand", hand.cards)
            print(f"Hand Total: {hand_value}")
            print_cards("Dealer's Final Hand", dealer_hand)
            print(f"Dealer Total: {dealer_total}")
            print(f"Outcome: {outcome}, Bet: {bet}, Player Money: {player.money}\n")
    return None


def get_bet_amount(running_count):
    # Compute adjusted bet based on the running count if card counting is enabled
    if ENABLE_CARD_COUNTING:
        # Increase bet for positive count, reduce for negative, using an increment of 2 per count point
        adjusted_bet = BET_AMOUNT + running_count[0] * 2
        return max(MIN_BET, min(adjusted_bet, MAX_BET))
    return BET_AMOUNT


# New function to play a single hand
def play_hand(player, hand, dealer_upcard, game, running_count):
    while True:
        total = hand.get_value()
        if total > 21:
            print("Player busts!")
            break
        player_hand_dict = [{'rank': card.rank, 'suit': card.suit.value} for card in hand.cards]
        move = get_blackjack_move(player_hand_dict, dealer_upcard, total)
        if move == "split":
            print("Player splits the hand.")
            handle_split(player, 0, game)
            print_cards("Player's Hands", [hand.cards for hand in player.hands])
            break
        print(f"Suggested move: {move}")
        if move in ["S"]:  # Stand
            print("Player stands.")
            break
        elif move in ["H"]:  # Hit
            card = game.deck.deal()
            if card:
                if ENABLE_CARD_COUNTING:
                    running_count[0] += hi_lo_count(card.rank)
                print(f"Player hits and receives: {card}")
                player.hit(card)
                print_cards("Player's Hand", hand.cards)
            else:
                break
        elif move in ["D", "Ds"]:  # Double
            player.set_bet(player.hands_bets[0] * 2, hand_index=0)
            card = game.deck.deal()
            if card:
                if ENABLE_CARD_COUNTING:
                    running_count[0] += hi_lo_count(card.rank)
                print(f"Player doubles and receives: {card}")
                player.hit(card)
                print_cards("Player's Hand", hand.cards)
            break
        else:
            print("Unexpected move. Player stands by default.")
            break
    return hand.get_value()


def simulate_game():
    # Initialize game with NUM_PLAYERS players using dynamically generated names
    player_names = [f"Player{i}" for i in range(1, NUM_PLAYERS + 1)]
    game = BlackjackGame(player_names)
    player = game.players[0]
    max_money = player.money
    min_money = player.money
    total_hands = 0
    reshuffle_count = 0
    running_count = [0]  # define once outside of rounds
    bet_histogram = {}  # initialize bet amounts histogram

    total_cards = len(game.deck.cards)
    print(f"Starting game with {total_cards} cards in the deck.")
    round_num = 1
    while True:
        print_separator()
        print(f"Round {round_num} beginning...")
        simulate_round(game, running_count, bet_histogram)
        total_hands += 1
        max_money = max(max_money, player.money)
        min_money = min(min_money, player.money)
        round_num += 1

        # Check deck percentage and reshuffle if needed
        remaining_pct = 100 * len(game.deck.cards) / total_cards
        if remaining_pct <= 100 - SHUFFLE_PERCENTAGE:
            if reshuffle_count < MAX_RESHUFFLE:
                reshuffle_count += 1
                print_separator()
                print(f"Reshuffling deck (reshuffle #{reshuffle_count})...")
                game.deck.reshuffle()
                total_cards = len(game.deck.cards)
                # Reset running count only upon deck reshuffle
                if ENABLE_CARD_COUNTING:
                    running_count[0] = 0
            else:
                print_separator()
                print("Maximum reshuffles reached. Ending game.")
                break

    print_separator()
    print("Game Over!")
    for p in game.players:
        print(f"Final Money for {p.name}: {p.money}")
    # New: Determine which player reached max and min money during simulation
    max_player = max(game.players, key=lambda p: p.money)
    min_player = min(game.players, key=lambda p: p.money)
    print(f"Player with Maximum Money: {max_player.name} ({max_player.money})")
    print(f"Player with Minimum Money: {min_player.name} ({min_player.money})")
    print(f"Maximum Money Reached: {max_player.money}")
    print(f"Minimum Money Reached: {min_player.money}")
    print(f"Total Hands Played: {total_hands}")
    print(f"Total Reshuffles: {reshuffle_count}")
    if ENABLE_CARD_COUNTING:
        print(f"Final Running Count: {running_count[0]}")
    print("Bet Histogram:")
    for bet, count in bet_histogram.items():
        print(f"Bet: {bet} => {count} time(s)")

    # Compute total money won (profit) for first player as example
    money_won = game.players[0].money - INITIAL_BALANCE

    # Build a summary dictionary and include the max/min player info
    histogram_str = "; ".join(f"{bet}:{count}" for bet, count in bet_histogram.items())
    summary = {
        'final_money': game.players[0].money,
        'max_money': max_player.money,
        'min_money': min_player.money,
        'max_money_player': max_player.name,
        'min_money_player': min_player.name,
        'total_hands': total_hands,
        'total_reshuffles': reshuffle_count,
        'final_running_count': running_count[0] if ENABLE_CARD_COUNTING else None,
        'money_won': money_won
    }
    return summary


def simulate_multiple_runs(num_runs, output_csv='simulation_results.csv'):
    results = []
    for i in range(num_runs):
        print_separator()
        print(f"Starting simulation run #{i + 1}...")
        summary = simulate_game()
        summary['run'] = i + 1
        results.append(summary)
    # Write results to CSV file
    fieldnames = ['run', 'final_money', 'max_money', 'min_money', 'total_hands',
                  'total_reshuffles', 'final_running_count', 'money_won']
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for res in results:
            writer.writerow(res)
    print_separator()
    print(f"Simulation complete. Results saved to {output_csv}")


if __name__ == "__main__":
    # To run multiple simulations, adjust the number below
    simulate_multiple_runs(100)
