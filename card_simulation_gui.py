# %%
import os

os.environ['SDL_AUDIODRIVER'] = 'dummy'  # disable sound to avoid ALSA errors
import re, pygame, sys

# %%
# --- Configuration ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
BACKGROUND_COLOR = (0, 100, 0)
FPS = 30
CARDS_FOLDER = os.path.join(os.getcwd(), "cards")  # Place your card images here
LOG_FILE = os.path.join(os.getcwd(), "src/outputs/simulation_log.txt")


# %%
# --- Utility: map card text to image filename ---
def get_card_image_filename(card_str):
    # card_str example: "10 of ♣️" or "A of ♥️"
    card_str = card_str.strip()
    m = re.match(r"(.+?)\s+of\s+(.+)", card_str)
    if not m:
        return None
    rank, suit = m.groups()
    suit_map = {"♣️": "clubs", "♦️": "diamonds", "♥️": "hearts", "♠️": "spades"}
    suit = suit_map.get(suit, "unknown")
    # Updated filename format to use lower case rank to match png filenames in the cards folder
    filename = f"{suit}_{rank}.png"
    return os.path.join(CARDS_FOLDER, filename)


# --- Parse simulation_log.txt into rounds ---
def parse_simulation_log():
    rounds = []
    current_round = {}
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        # Detect round beginning
        if re.match(r"^Round\s+\d+\s+beginning", line):
            if current_round:
                rounds.append(current_round)
            current_round = {"round": line}
        elif line.startswith("Player1's Round Summary:"):
            # Reset hand data for player1
            current_round["player1"] = {}
        elif line.startswith("Player2's Round Summary:"):
            current_round["player2"] = {}
        elif line.startswith("Dealer's Final Hand:"):
            current_round["dealer_final"] = line.split("Dealer's Final Hand:")[-1].strip()
        elif line.startswith("Final Hand:"):
            # Depending on context, assign to current player
            if "player1" in current_round and "final_hand" not in current_round["player1"]:
                current_round["player1"]["final_hand"] = line.split("Final Hand:")[-1].strip()
            elif "player2" in current_round and "final_hand" not in current_round["player2"]:
                current_round["player2"]["final_hand"] = line.split("Final Hand:")[-1].strip()
    if current_round:
        rounds.append(current_round)
    return rounds


# --- Render a set of cards horizontally ---
def render_cards(screen, card_str_list, start_pos, card_size=(100, 145), gap=10):
    x, y = start_pos
    for card_str in card_str_list:
        img_file = get_card_image_filename(card_str)
        if img_file and os.path.exists(img_file):
            card_img = pygame.image.load(img_file).convert_alpha()
            card_img = pygame.transform.smoothscale(card_img, card_size)
        else:
            # fallback: render a placeholder rectangle with text
            print(f"Card image not found: {card_str}")
            card_img = pygame.Surface(card_size)
            card_img.fill((255, 255, 255))
            font = pygame.font.SysFont(None, 24)
            text_surf = font.render(card_str, True, (0, 0, 0))
            card_img.blit(text_surf, (5, 5))
        screen.blit(card_img, (x, y))
        x += card_size[0] + gap


# %%
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Card Simulation Viewer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    rounds = parse_simulation_log()
    if not rounds:
        print("No rounds found in log.")
        sys.exit()

    current_index = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Left/right arrow to change round
                if event.key == pygame.K_RIGHT:
                    current_index = (current_index + 1) % len(rounds)
                elif event.key == pygame.K_LEFT:
                    current_index = (current_index - 1) % len(rounds)

        screen.fill(BACKGROUND_COLOR)
        cr = rounds[current_index]
        round_text = f"Round: {current_index + 1}"
        text_surf = font.render(round_text, True, (255, 255, 0))
        screen.blit(text_surf, (20, 20))

        # Parse hand strings into lists
        def get_hand_list(hand_str):
            # assuming cards in hand are separated by " | "
            return [s.strip() for s in hand_str.split("|") if s.strip()]

        # Render Player1 final hand
        if "player1" in cr and "final_hand" in cr["player1"]:
            p1_hand = get_hand_list(cr["player1"]["final_hand"])
            text = font.render("Player1:", True, (255, 255, 255))
            screen.blit(text, (20, 80))
            render_cards(screen, p1_hand, (20, 120))
            # Render Player1 bet and money
            if "bet" in cr["player1"] and "money" in cr["player1"]:
                bet_text = font.render(f"Bet: {cr['player1']['bet']}", True, (255, 255, 255))
                money_text = font.render(f"Money: {cr['player1']['money']}", True, (255, 255, 255))
                screen.blit(bet_text, (20, 270))
                screen.blit(money_text, (20, 310))

        # Render Player2 final hand
        if "player2" in cr and "final_hand" in cr["player2"]:
            p2_hand = get_hand_list(cr["player2"]["final_hand"])
            text = font.render("Player2:", True, (255, 255, 255))
            screen.blit(text, (20, 300))
            render_cards(screen, p2_hand, (20, 340))
            # Render Player2 bet and money
            if "bet" in cr["player2"] and "money" in cr["player2"]:
                bet_text = font.render(f"Bet: {cr['player2']['bet']}", True, (255, 255, 255))
                money_text = font.render(f"Money: {cr['player2']['money']}", True, (255, 255, 255))
                screen.blit(bet_text, (20, 490))
                screen.blit(money_text, (20, 530))

        # Render Dealer final hand
        if "dealer_final" in cr:
            dealer_hand = get_hand_list(cr["dealer_final"])
            text = font.render("Dealer:", True, (255, 255, 255))
            screen.blit(text, (20, 520))
            render_cards(screen, dealer_hand, (20, 560))

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
