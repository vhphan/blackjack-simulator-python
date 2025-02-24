def card_lookup_value(rank):
    try:
        return int(rank)
    except ValueError:
        if rank in ['J', 'Q', 'K']:
            return 10
        elif rank == 'A':
            return 'A'

# Added hi_lo_count function for basic card counting using the Hi-Lo system
def hi_lo_count(rank):
    if rank in ['2', '3', '4', '5', '6']:
        return 1
    elif rank in ['10', 'J', 'Q', 'K', 'A']:
        return -1
    else:
        return 0

# Combined strategy table for hard and soft totals
blackjack_strategy = {
    'hard': {
        21: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 'A': "S"},
        20: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 'A': "S"},
        19: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 'A': "S"},
        18: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 'A': "S"},
        17: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 'A': "S"},
        16: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        15: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        14: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        13: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        12: {2: "H", 3: "H", 4: "S", 5: "S", 6: "S", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        11: {2: "D", 3: "D", 4: "D", 5: "D", 6: "D", 7: "D", 8: "D", 9: "D", 10: "D", 'A': "D"},
        10: {2: "D", 3: "D", 4: "D", 5: "D", 6: "D", 7: "D", 8: "D", 9: "D", 10: "H", 'A': "H"},
        9: {2: "H", 3: "D", 4: "D", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        8: {2: "H", 3: "H", 4: "H", 5: "H", 6: "H", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        7: {2: "H", 3: "H", 4: "H", 5: "H", 6: "H", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        6: {2: "H", 3: "H", 4: "H", 5: "H", 6: "H", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        5: {2: "H", 3: "H", 4: "H", 5: "H", 6: "H", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        4: {2: "H", 3: "H", 4: "H", 5: "H", 6: "H", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        3: {2: "H", 3: "H", 4: "H", 5: "H", 6: "H", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        2: {2: "H", 3: "H", 4: "H", 5: "H", 6: "H", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
    },
    'soft': {
        "A,9": {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 'A': "S"},
        "A,8": {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 'A': "S"},
        "A,7": {2: "Ds", 3: "Ds", 4: "Ds", 5: "Ds", 6: "Ds", 7: "S", 8: "S", 9: "H", 10: "H", 'A': "H"},
        "A,6": {2: "H", 3: "D", 4: "D", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        "A,5": {2: "H", 3: "H", 4: "D", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        "A,4": {2: "H", 3: "H", 4: "D", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        "A,3": {2: "H", 3: "H", 4: "H", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        "A,2": {2: "H", 3: "H", 4: "H", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},
        "A,A": {2: "H", 3: "H", 4: "H", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", 'A': "H"},  # until split is implemented, modify later
    },
    'pairSplitting': {
        "A,A": {2: "Y", 3: "Y", 4: "Y", 5: "Y", 6: "Y", 7: "Y", 8: "Y", 9: "Y", 10: "Y", 'A': "Y"},
        "T,T": {2: "N", 3: "N", 4: "N", 5: "N", 6: "N", 7: "N", 8: "N", 9: "N", 10: "N", 'A': "N"},
        "9,9": {2: "Y", 3: "Y", 4: "Y", 5: "Y", 6: "Y", 7: "N", 8: "Y", 9: "Y", 10: "N", 'A': "N"},
        "8,8": {2: "Y", 3: "Y", 4: "Y", 5: "Y", 6: "Y", 7: "Y", 8: "Y", 9: "Y", 10: "Y", 'A': "Y"},
        "7,7": {2: "Y", 3: "Y", 4: "Y", 5: "Y", 6: "Y", 7: "Y", 8: "N", 9: "N", 10: "N", 'A': "N"},
        "6,6": {2: "Y", 3: "Y", 4: "Y", 5: "Y", 6: "Y", 7: "N", 8: "N", 9: "N", 10: "N", 'A': "N"},
        "5,5": {2: "N", 3: "N", 4: "N", 5: "N", 6: "N", 7: "N", 8: "N", 9: "N", 10: "N", 'A': "N"},
        "4,4": {2: "N", 3: "N", 4: "N", 5: "Y", 6: "Y", 7: "N", 8: "N", 9: "N", 10: "N", 'A': "N"},
        "3,3": {2: "Y", 3: "Y", 4: "Y", 5: "Y", 6: "Y", 7: "N", 8: "N", 9: "N", 10: "N", 'A': "N"},
        "2,2": {2: "Y", 3: "Y", 4: "Y", 5: "Y", 6: "Y", 7: "N", 8: "N", 9: "N", 10: "N", 'A': "N"}
    }
}

# Ds = Double if possible, otherwise stand
# H = Hit
# S = Stand
# D = Double if possible, otherwise hit

# Function to get the move for hard or soft totals
def get_blackjack_move(player_hand, dealer_upcard, player_total):

    # Check for pair splitting if exactly 2 cards and both have the same rank.
    # if len(player_hand) == 2 and player_hand[0]['rank'] == player_hand[1]['rank']:
    #     upcard_value = 10 if dealer_upcard['rank'] in ['J', 'Q', 'K'] else card_lookup_value(dealer_upcard['rank'])
    #     action = blackjack_strategy['pairSplitting'].get(f"{player_hand[0]['rank']},{player_hand[1]['rank']}", {}).get(upcard_value, "Invalid")
    #     if action != "Invalid" and action == "Y":
    #         return "split"

    if player_total == 21:
        return "S"

    upcard = 'A' if dealer_upcard['rank'] == 'A' else dealer_upcard['rank']
    has_ace = any(card['rank'] == 'A' for card in player_hand)
    upcard_value = 10 if upcard in ['J', 'Q', 'K'] else card_lookup_value(upcard)

    result = None
    # Handle soft totals
    if len(player_hand) == 2 and player_hand[0]['rank'] == 'A' and player_hand[1]['rank'] == 'A':
        # print('A,A')
        result = blackjack_strategy['soft'].get('A,A', {}).get(upcard_value, "Invalid")
    elif has_ace and player_total < 21 and len(player_hand) == 2:
        # print('Soft')
        result = blackjack_strategy['soft'].get(f"A,{player_total - 11}", {}).get(upcard_value, "Invalid")
    else:
        # print('Hard')
        result = blackjack_strategy['hard'].get(player_total, {}).get(upcard_value, "Invalid")

    if result == 'Invalid':
        print(player_hand, dealer_upcard)

    return result

# Example usage:
# player_hand = [{'rank': 'A', 'suit': '♠️'}, {'rank': '7', 'suit': '♣️'}]
# dealer_upcard = {'rank': '3', 'suit': '♦️'}
# print(get_blackjack_move(player_hand, dealer_upcard, 18))  # "Ds"