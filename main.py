import csv
import os  # NEW import

from src.cls.game import BlackjackGame
from src.cls.hand import Hand
from src.strategies.basic import get_blackjack_move, hi_lo_count
from src.cls.card import Card  # for type checking deck cards
from src.settings import SHUFFLE_PERCENTAGE, BET_AMOUNT, MAX_RESHUFFLE, ENABLE_CARD_COUNTING, MIN_BET, MAX_BET, \
    INITIAL_BALANCE, NUM_PLAYERS
from src.helpers.simulation_logger import SimulationLogger  # NEW import


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


def simulate_round(game, running_count, bet_histogram, logger):
    print_separator()
    logger.log("="*50)
    logger.log("New Round Starting")
    # Reinitialize players for new round
    for player in game.players:
        player.hands = [Hand()]
        adjusted_bet = get_bet_amount(running_count)
        bet_histogram[adjusted_bet] = bet_histogram.get(adjusted_bet, 0) + 1
        player.hands_bets = [adjusted_bet]
    dealer_hand = []
    # Deal initial cards for each player
    for player in game.players:
        for _ in range(2):
            card = game.deck.deal()
            if card:
                if ENABLE_CARD_COUNTING:
                    running_count[0] += hi_lo_count(card.rank)
                player.hit(card)
                logger.log(f"{player.name} receives: {card}")
    # Dealer deal
    for _ in range(2):
        card = game.deck.deal()
        if card:
            if ENABLE_CARD_COUNTING:
                running_count[0] += hi_lo_count(card.rank)
            dealer_hand.append(card)
            logger.log(f"Dealer receives: {card}")
    dealer_upcard = {'rank': dealer_hand[0].rank, 'suit': dealer_hand[0].suit.value}
    # Log initial state
    for player in game.players:
        logger.log(f"{player.name}'s Hand: " +
                   ' | '.join(str(c) for c in player.hands[0].cards))
        logger.log(f"{player.name}'s Total: {player.hands[0].get_value()}")
    logger.log("Dealer Upcard: " + str(dealer_hand[0]))
    if ENABLE_CARD_COUNTING:
        logger.log(f"Running Count: {running_count[0]}")
    # Process player's turns
    for player in game.players:
        i = 0
        while i < len(player.hands):
            hand = player.hands[i]
            play_hand(player, hand, dealer_upcard, game, running_count, logger)
            i += 1
    # Dealer turn
    if any(hand.get_value() <= 21 for player in game.players for hand in player.hands):
        logger.log("="*50)
        logger.log("Dealer's Turn:")
        logger.log("Dealer's Hand: " + ' | '.join(str(c) for c in dealer_hand))
        dealer_total = sum(card.value() for card in dealer_hand)
        logger.log(f"Dealer's Total: {dealer_total}")
        while dealer_total < 17:
            card = game.deck.deal()
            if not card:
                break
            if ENABLE_CARD_COUNTING:
                running_count[0] += hi_lo_count(card.rank)
            dealer_hand.append(card)
            dealer_total = sum(card.value() for card in dealer_hand)
            logger.log(f"Dealer hits and receives: {card}")
            logger.log("Dealer's Hand: " + ' | '.join(str(c) for c in dealer_hand))
            logger.log(f"Dealer's New Total: {dealer_total}")
    else:
        dealer_total = sum(card.value() for card in dealer_hand)
        logger.log("Dealer wins by all players bust.")
    # Outcome determination (logging similar to print statements)
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
            logger.log("="*50)
            logger.log(f"{player.name}'s Round Summary:")
            logger.log("Final Hand: " + ' | '.join(str(c) for c in hand.cards))
            logger.log(f"Hand Total: {hand_value}")
            logger.log("Dealer's Final Hand: " + ' | '.join(str(c) for c in dealer_hand))
            logger.log(f"Dealer Total: {dealer_total}")
            logger.log(f"Outcome: {outcome}, Bet: {bet}, Player Money: {player.money}\n")
    return None


def get_bet_amount(running_count):
    # Compute adjusted bet based on the running count if card counting is enabled
    if ENABLE_CARD_COUNTING:
        # Increase bet for positive count, reduce for negative, using an increment of 2 per count point
        adjusted_bet = BET_AMOUNT + running_count[0] * 2
        return max(MIN_BET, min(adjusted_bet, MAX_BET))
    return BET_AMOUNT


# New function to play a single hand
def play_hand(player, hand, dealer_upcard, game, running_count, logger):
    while True:
        total = hand.get_value()
        if total > 21:
            logger.log("Player busts!")
            break
        player_hand_dict = [{'rank': card.rank, 'suit': card.suit.value} for card in hand.cards]
        move = get_blackjack_move(player_hand_dict, dealer_upcard, total)
        if move == "split":
            logger.log("Player splits the hand.")
            handle_split(player, 0, game)
            logger.log("Player's Hands after split: " +
                       str([str(h.cards) for h in player.hands]))
            break
        logger.log(f"Suggested move: {move}")
        if move in ["S"]:
            logger.log("Player stands.")
            break
        elif move in ["H"]:
            card = game.deck.deal()
            if card:
                if ENABLE_CARD_COUNTING:
                    running_count[0] += hi_lo_count(card.rank)
                logger.log(f"Player hits and receives: {card}")
                player.hit(card)
                logger.log("Player's Hand: " + ' | '.join(str(c) for c in hand.cards))
            else:
                break
        elif move in ["D", "Ds"]:
            player.set_bet(player.hands_bets[0] * 2, hand_index=0)
            card = game.deck.deal()
            if card:
                if ENABLE_CARD_COUNTING:
                    running_count[0] += hi_lo_count(card.rank)
                logger.log(f"Player doubles and receives: {card}")
                player.hit(card)
                logger.log("Player's Hand: " + ' | '.join(str(c) for c in hand.cards))
            break
        else:
            logger.log("Unexpected move. Player stands by default.")
            break
    return hand.get_value()


def simulate_game():
    # Initialize game with NUM_PLAYERS players using dynamically generated names
    player_names = [f"Player{i}" for i in range(1, NUM_PLAYERS + 1)]
    game = BlackjackGame(player_names)
    total_hands = 0
    reshuffle_count = 0
    running_count = [0]  # define once outside of rounds
    bet_histogram = {}  # initialize bet amounts histogram

    # Initialize each player's minimum reached money
    min_reached = {p.name: p.money for p in game.players}

    total_cards = len(game.deck.cards)
    print(f"Starting game with {total_cards} cards in the deck.")
    round_num = 1
    logger = SimulationLogger(os.path.join(os.getcwd(), "simulation_log.txt"))  # Updated logger file path
    while True:
        logger.log("="*50)
        logger.log(f"Round {round_num} beginning...")
        simulate_round(game, running_count, bet_histogram, logger)
        total_hands += 1

        # Update min_reached for each player
        for p in game.players:
            if p.money < min_reached[p.name]:
                min_reached[p.name] = p.money

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
    # Compute overall minimum using the tracked values
    min_player_name, overall_min = min(min_reached.items(), key=lambda item: item[1])
    max_player = max(game.players, key=lambda p: p.money)
    print(f"Player with Maximum Money: {max_player.name} ({max_player.money})")
    print(f"Minimum Money Reached During Simulation: {overall_min} (by {min_player_name})")
    print(f"Total Hands Played: {total_hands}")
    print(f"Total Reshuffles: {reshuffle_count}")
    if ENABLE_CARD_COUNTING:
        print(f"Final Running Count: {running_count[0]}")
    print("Bet Histogram:")
    for bet, count in bet_histogram.items():
        print(f"Bet: {bet} => {count} time(s)")

    # Build a dictionary for each player's final money
    players_stats = {f"final_money_{p.name}": p.money for p in game.players}
    # Build a summary dictionary including the minimum reached money
    summary = {
        'total_hands': total_hands,
        'total_reshuffles': reshuffle_count,
        'final_running_count': running_count[0] if ENABLE_CARD_COUNTING else None,
        'max_money': max_player.money,
        'max_money_player': max_player.name,
        'min_money_reached': overall_min,
        'min_money_player': min_player_name,
    }
    summary.update(players_stats)
    return summary


def simulate_multiple_runs(num_runs, output_csv='simulation_results.csv'):
    results = []
    for i in range(num_runs):
        print_separator()
        print(f"Starting simulation run #{i + 1}...")
        summary = simulate_game()
        summary['run'] = i + 1
        results.append(summary)
    # Update fieldnames to include all players' final money
    base_fields = results[0].keys()
    # Assuming player names are "Player1", "Player2", ..., based on NUM_PLAYERS
    # extra_fields = [f'final_money_Player{i}' for i in range(1, NUM_PLAYERS + 1)]
    # fieldnames = base_fields + extra_fields
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=base_fields)
        writer.writeheader()
        for res in results:
            writer.writerow(res)
    print_separator()
    print(f"Simulation complete. Results saved to {output_csv}")


if __name__ == "__main__":
    # To run multiple simulations, adjust the number below
    simulate_multiple_runs(100)

