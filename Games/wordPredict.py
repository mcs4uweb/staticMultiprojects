import pygame
import sys
import random

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen setup
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Word Prediction Trainer")

# Colors
BACKGROUND = (240, 245, 255)
TEXT = (30, 30, 50)
HIGHLIGHT = (70, 130, 230)
INPUT_BG = (255, 255, 255)
SUGGEST_BG = (230, 240, 255)
CORRECT = (46, 184, 46)
MISTAKE = (220, 60, 60)

# Font
FONT_LARGE = pygame.font.SysFont('Arial', 48, bold=True)
FONT_MEDIUM = pygame.font.SysFont('Arial', 32)
FONT_SMALL = pygame.font.SysFont('Arial', 28)

# Sample word list (use grade-appropriate words)
WORD_LIST = [
    "necessary", "separate", "definitely", "because", "friend", 
    "believe", "receive", "their", "weather", "library",
    "February", "government", "immediately", "recommend", "pronunciation"
]

# Simplified dictionary for prediction (you can expand this)
DICTIONARY = set(WORD_LIST + [
    "need", "neck", "near", "neat", "seem", "seen", "seat", "defend", "define",
    "beach", "beak", "bear", "friar", "fried", "brief", "belong", "relieve",
    "receipt", "recipe", "there", "they", "them", "then", "wet", "web", "wed"
])

class WordPredictionGame:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.target_word = random.choice(WORD_LIST).lower()
        self.current_input = ""
        self.keystrokes = 0
        self.completed = False
        self.message = ""
        self.message_color = TEXT
        self.suggestions = self.get_suggestions("")

    def get_suggestions(self, prefix, max_suggestions=5):
        """Return up to 5 words that start with prefix"""
        if not prefix:
            return []
        matches = [word for word in DICTIONARY if word.startswith(prefix)]
        return matches[:max_suggestions]
    
    def handle_key(self, key):
        if self.completed:
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                self.reset()
            return

        if key == pygame.K_BACKSPACE:
            if self.current_input:
                self.current_input = self.current_input[:-1]
                self.keystrokes += 1  # Backspace counts as a keystroke
        elif key == pygame.K_RETURN:
            # Try to submit
            if self.current_input.lower() == self.target_word:
                self.finish_success()
            else:
                self.message = "Not quite! Keep typing or use suggestions."
                self.message_color = MISTAKE
                self.keystrokes += 1
        elif 97 <= key <= 122:  # a-z
            char = chr(key)
            self.current_input += char
            self.keystrokes += 1
            
            # Check if target is in suggestions
            self.suggestions = self.get_suggestions(self.current_input)
            if self.target_word in self.suggestions:
                self.finish_success()
            elif len(self.current_input) > len(self.target_word) + 2:
                self.message = "Too many letters! Try fewer."
                self.message_color = MISTAKE
        
    def finish_success(self):
        self.completed = True
        optimal = self.find_min_keystrokes()
        if self.keystrokes <= optimal:
            self.message = f"Perfect! ✨ ({self.keystrokes} keystrokes)"
            self.message_color = CORRECT
        elif self.keystrokes <= optimal + 2:
            self.message = f"Great! ({self.keystrokes} keystrokes)"
            self.message_color = CORRECT
        else:
            self.message = f"Good! Try fewer keystrokes next time. ({self.keystrokes})"
            self.message_color = TEXT
        self.message += " — Press ENTER for next word"

    def find_min_keystrokes(self):
        """Find the fewest letters needed to make target appear in suggestions"""
        for i in range(1, len(self.target_word) + 1):
            prefix = self.target_word[:i]
            suggestions = self.get_suggestions(prefix)
            if self.target_word in suggestions:
                return i
        return len(self.target_word)

    def draw(self, surface):
        surface.fill(BACKGROUND)
        
        # Title
        title = FONT_LARGE.render("Word Prediction Trainer", True, TEXT)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        
        # Instructions
        instr = FONT_SMALL.render("Type the target word using as FEW keystrokes as possible!", True, TEXT)
        surface.blit(instr, (WIDTH//2 - instr.get_width()//2, 100))
        
        # Target word
        target_text = FONT_MEDIUM.render(f"Target: {self.target_word}", True, TEXT)
        surface.blit(target_text, (50, 160))
        
        # Input box
        input_rect = pygame.Rect(50, 220, 700, 60)
        pygame.draw.rect(surface, INPUT_BG, input_rect)
        pygame.draw.rect(surface, HIGHLIGHT if not self.completed else CORRECT, input_rect, 3)
        
        input_text = FONT_MEDIUM.render(self.current_input, True, TEXT)
        surface.blit(input_text, (60, 235))
        
        # Suggestions
        if self.suggestions and not self.completed:
            suggest_title = FONT_SMALL.render("Predictions:", True, TEXT)
            surface.blit(suggest_title, (50, 300))
            
            y = 340
            for word in self.suggestions:
                color = CORRECT if word == self.target_word else TEXT
                bg = SUGGEST_BG if word == self.target_word else BACKGROUND
                word_surf = FONT_MEDIUM.render(word, True, color)
                word_rect = pygame.Rect(50, y, 300, 40)
                pygame.draw.rect(surface, bg, word_rect, border_radius=5)
                surface.blit(word_surf, (60, y + 5))
                y += 50
        
        # Message
        if self.message:
            msg_surf = FONT_MEDIUM.render(self.message, True, self.message_color)
            surface.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT - 100))
        
        # Keystroke counter
        if not self.completed:
            counter = FONT_SMALL.render(f"Keystrokes: {self.keystrokes}", True, TEXT)
            surface.blit(counter, (WIDTH - counter.get_width() - 20, 20))

# Main game
def main():
    game = WordPredictionGame()
    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                game.handle_key(event.key)
        
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()