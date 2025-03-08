import csv

from src.cls.game import BlackjackGame
from src.cls.hand import Hand
from src.helpers.simulation_logger import logger
from src.settings import (SHUFFLE_PERCENTAGE,
                          BET_AMOUNT,
                          MAX_RESHUFFLE,
                          ENABLE_CARD_COUNTING,
                          MIN_BET, MAX_BET,
                          NUM_PLAYERS, TOTAL_RUNS, MAX_SPLIT_ALLOWED)
from src.strategies.basic import get_blackjack_move, hi_lo_count


def print_cards(label, cards):
    # Build a string representation for a list of cards
    card_str = ' | '.join(str(card) for card in cards)
    logger.log(f"{label}: {card_str}")


def print_separator():
    logger.log("=" * 50)


def handle_split(player, hand_index, game, running_count):
    # Split the hand into two separate hands
    hand = player.hands[hand_index]
    # add new hand
    player.add_hand(hand=Hand(), bet=player.hands_bets[hand_index])
    # remove one card from current hand and add it to the new hand
    card = hand.cards.pop()
    player.hands[hand_index + 1].add_card(card)

    # deal a new card to each hand
    for i in range(hand_index, hand_index + 2):
        card = game.deck.deal()
        if card:
            player.hands[i].add_card(card)
            if ENABLE_CARD_COUNTING:
                running_count[0] += hi_lo_count(card.rank)
        else:
            break


def simulate_round(game, running_count, bet_histogram):
    print_separator()
    logger.log("New Round Starting")
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
                player.hands[0].add_card(card)

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
        logger.log(f"{player.name}'s Total: {player.hands[0].value}")
    print_cards("Dealer Upcard", dealer_hand[:1])

    if ENABLE_CARD_COUNTING:
        logger.log(f"Running Count: {running_count[0]}")

    # Player's turn for each hand
    for player in game.players:
        # Using while-loop to process any newly added hands (from splits)
        play_hand(player, player.hands[0], dealer_upcard, game, running_count)

    # Dealer's turn if any player hasn't busted
    if any(hand.value <= 21 for player in game.players for hand in player.hands):
        print_separator()
        logger.log("Dealer's Turn:")
        print_cards("Dealer's Hand", dealer_hand)
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
            print_cards("Dealer's Hand", dealer_hand)
            logger.log(f"Dealer's New Total: {dealer_total}")
    else:
        dealer_total = sum(card.value() for card in dealer_hand)
        logger.log("Dealer wins by all players bust.")

    # Determine outcome for each player's hand
    for player in game.players:
        for hand, bet in zip(player.hands, player.hands_bets):
            if hand.value > 21:
                outcome = "lose"
                player.money -= bet
            elif dealer_total > 21 or hand.value > dealer_total:
                outcome = "win"
                player.money += bet
            elif hand.value == dealer_total:
                outcome = "push"
            else:
                outcome = "lose"
                player.money -= bet
            print_separator()
            logger.log(f"{player.name}'s Round Summary:")
            print_cards("Final Hand", hand.cards)
            logger.log(f"Hand Total: {hand.value}")
            print_cards("Dealer's Final Hand", dealer_hand)
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
def play_hand(player, hand, dealer_upcard, game, running_count, split_count=0):
    while True:

        if hand.value > 21:
            logger.log("Player busts!")
            break

        player_hand_dict = [{'rank': card.rank, 'suit': card.suit.value} for card in hand.cards]

        move = get_blackjack_move(player_hand_dict, dealer_upcard, hand.value)

        if move == "split" and split_count > MAX_SPLIT_ALLOWED:
            move = "H"  # Change move to hit if split count exceeds MAX_SPLIT_ALLOWED
        if move == "split":
            logger.log("Player splits the hand.")

            # Find the index of the current hand by iterating over the hands
            hand_index = next(i for i, h in enumerate(player.hands) if h == hand)
            handle_split(player, hand_index, game, running_count)

            print_cards("Player's Hands", [hand.cards for hand in player.hands])

            # Recursive call to play the newly split hands
            old_hand = player.hands[hand_index]
            play_hand(player, old_hand, dealer_upcard, game, running_count, split_count + 1)

            new_hand = player.hands[hand_index + 1]
            play_hand(player, new_hand, dealer_upcard, game, running_count, split_count + 1)

            break

        logger.log(f"Suggested move: {move}")
        if move in ["S"]:  # Stand
            logger.log("Player stands.")
            break

        elif move in ["H"]:  # Hit
            card = game.deck.deal()
            if card:
                if ENABLE_CARD_COUNTING:
                    running_count[0] += hi_lo_count(card.rank)
                logger.log(f"Player hits and receives: {card}")
                hand.add_card(card)
                print_cards("Player's Hand", hand.cards)
            else:
                break

        elif move in ["D", "Ds"]:  # Double
            player.set_bet(player.hands_bets[0] * 2, hand_index=0)
            card = game.deck.deal()
            if card:
                if ENABLE_CARD_COUNTING:
                    running_count[0] += hi_lo_count(card.rank)
                logger.log(f"Player doubles and receives: {card}")
                hand.add_card(card)
            break
        else:
            logger.log("Unexpected move. Player stands by default.")
            break
    return hand.value


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
    logger.log(f"Starting game with {total_cards} cards in the deck.")
    round_num = 1
    while True:
        print_separator()
        logger.log(f"Round {round_num} beginning...")

        simulate_round(game, running_count, bet_histogram)

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
                logger.log(f"Reshuffling deck (reshuffle #{reshuffle_count})...")
                game.deck.reshuffle()
                total_cards = len(game.deck.cards)
                if ENABLE_CARD_COUNTING:
                    running_count[0] = 0
            else:
                print_separator()
                logger.log("Maximum reshuffles reached. Ending game.")
                break

    print_separator()
    logger.log("Game Over!")
    for p in game.players:
        logger.log(f"Final Money for {p.name}: {p.money}")
    # Compute overall minimum using the tracked values
    min_player_name, overall_min = min(min_reached.items(), key=lambda item: item[1])
    max_player = max(game.players, key=lambda p: p.money)
    logger.log(f"Player with Maximum Money: {max_player.name} ({max_player.money})")
    logger.log(f"Minimum Money Reached During Simulation: {overall_min} (by {min_player_name})")
    logger.log(f"Total Hands Played: {total_hands}")
    logger.log(f"Total Reshuffles: {reshuffle_count}")

    if ENABLE_CARD_COUNTING:
        logger.log(f"Final Running Count: {running_count[0]}")

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


def simulate_multiple_runs(num_runs, output_csv='src/outputs/simulation_results.csv'):
    results = []
    for i in range(num_runs):
        print_separator()
        logger.log(f"Starting simulation run #{i + 1}...")
        result = simulate_game()
        result['run'] = i + 1
        results.append(result)
    base_fields = results[0].keys()
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=base_fields)
        writer.writeheader()
        for res in results:
            writer.writerow(res)
    print_separator()
    logger.log(f"Simulation complete. Results saved to {output_csv}")


if __name__ == "__main__":
    # To run multiple simulations, adjust the number below
    simulate_multiple_runs(TOTAL_RUNS)
