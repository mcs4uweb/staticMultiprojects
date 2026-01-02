import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
BACKGROUND_COLOR = (30, 30, 50)
TEXT_COLOR = (240, 240, 240)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 160, 210)
QUIT_BUTTON_COLOR = (180, 60, 60)
QUIT_HOVER_COLOR = (220, 80, 80)
INPUT_BOX_COLOR = (50, 50, 70)
INPUT_ACTIVE_COLOR = (60, 60, 90)
CORRECT_COLOR = (100, 255, 100)
INCORRECT_COLOR = (255, 100, 100)
FONT = pygame.font.SysFont(None, 36)
SMALL_FONT = pygame.font.SysFont(None, 30)
FEEDBACK_DISPLAY_TIME = 1500

SENTENCES = [
    "The cat sat down",
    "She likes ice cream",
    "Birds fly in sky",
    "My dog runs fast",
    "We eat pizza Friday"
]

class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.hovered = False
        self.color = color
        self.hover_color = hover_color

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, border_radius=8)
        text_surf = FONT.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class InputBox:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ''
        self.active = False
        self.txt_surface = FONT.render(self.text, True, TEXT_COLOR)

    def handle_event(self, event, go_button, done_button, quit_button=None):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Deactivate only if click is outside input AND not on any button
            if not self.rect.collidepoint(event.pos):
                buttons = [go_button, done_button]
                if quit_button:
                    buttons.append(quit_button)
                clicked_button = any(btn.rect.collidepoint(event.pos) for btn in buttons)
                if not clicked_button:
                    self.active = False
            else:
                self.active = True

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            else:
                self.text += event.unicode
            self.txt_surface = FONT.render(self.text, True, TEXT_COLOR)
        return False

    def clear(self):
        self.text = ''
        self.txt_surface = FONT.render(self.text, True, TEXT_COLOR)

    def draw(self, surface):
        color = INPUT_ACTIVE_COLOR if self.active else INPUT_BOX_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, (180, 180, 180), self.rect, 2, border_radius=6)
        surface.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 8))

def draw_sentence(surface, sentence, y):
    text_surf = FONT.render(sentence, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=(WIDTH // 2, y))
    surface.blit(text_surf, text_rect)

def process_answer(user_input, current_idx, correct_count, sentences):
    correct = sentences[current_idx].lower() == user_input.lower()
    if correct:
        return True, correct_count + 1
    else:
        return False, correct_count

def format_time(seconds):
    """Format seconds into mm:ss"""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Memory Learning Game - Easy Level")
    clock = pygame.time.Clock()

    current_sentence_index = 0
    sentence_shown = True
    timer_started = False
    round_start_time = 0
    total_time_accumulated = 0
    done = False
    correct_count = 0
    feedback = ""
    feedback_timer = 0
    feedback_color = TEXT_COLOR

    go_button = Button(50, 100, 100, 50, "Go")
    done_button = Button(WIDTH - 300, 350, 120, 50, "Done")
    quit_button = Button(WIDTH - 160, 350, 120, 50, "Quit", QUIT_BUTTON_COLOR, QUIT_HOVER_COLOR)
    input_box = InputBox(100, 280, 600, 60)

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        submit = False
        quit_game = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if go_button.is_clicked(mouse_pos, event):
                if sentence_shown:
                    sentence_shown = False
                    timer_started = True
                    round_start_time = pygame.time.get_ticks()
                    input_box.clear()
                    input_box.active = True
                    feedback = ""

            if done_button.is_clicked(mouse_pos, event):
                if timer_started:
                    submit = True

            if quit_button.is_clicked(mouse_pos, event):
                # Stop current timer and finalize
                if timer_started:
                    round_time = (pygame.time.get_ticks() - round_start_time) // 1000
                    total_time_accumulated += round_time
                quit_game = True

            if input_box.handle_event(event, go_button, done_button, quit_button) and timer_started:
                submit = True

        # Handle answer submission
        if submit:
            user_input = input_box.text.strip()
            input_box.clear()
            input_box.active = True

            correct, new_correct_count = process_answer(
                user_input, current_sentence_index, correct_count, SENTENCES
            )

            round_time = (pygame.time.get_ticks() - round_start_time) // 1000
            total_time_accumulated += round_time

            if correct:
                correct_count = new_correct_count
                feedback = "Good job! ✅"
                feedback_color = CORRECT_COLOR
                feedback_timer = current_time + FEEDBACK_DISPLAY_TIME
                pygame.time.delay(800)
                current_sentence_index += 1
                if current_sentence_index >= len(SENTENCES):
                    done = True
                else:
                    sentence_shown = True
                    timer_started = False
                    input_box.active = False
            else:
                feedback = "Incorrect! Try again. ❌"
                feedback_color = INCORRECT_COLOR
                feedback_timer = current_time + FEEDBACK_DISPLAY_TIME
                # Restart timer for retry (so retries don't add extra time)
                timer_started = True
                round_start_time = pygame.time.get_ticks()

        # Handle quit
        if quit_game:
            done = True

        # Update button hover states
        go_button.check_hover(mouse_pos)
        done_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)

        # Clear feedback after timeout
        if feedback and current_time > feedback_timer:
            feedback = ""

        # Draw everything
        screen.fill(BACKGROUND_COLOR)

        # ✅ Score display
        score_text = SMALL_FONT.render(f"Correct: {correct_count}/5", True, CORRECT_COLOR)
        screen.blit(score_text, (WIDTH - score_text.get_width() - 20, 15))

        if done:
            total_time_str = format_time(total_time_accumulated)
            final_text1 = FONT.render(f"🎉 You got {correct_count}/5 correct!", True, CORRECT_COLOR)
            final_text2 = FONT.render(f"Total time: {total_time_str}", True, TEXT_COLOR)
            final_text3 = FONT.render("Thanks for playing!", True, TEXT_COLOR)
            screen.blit(final_text1, final_text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
            screen.blit(final_text2, final_text2.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            screen.blit(final_text3, final_text3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))
        else:
            if sentence_shown:
                draw_sentence(screen, SENTENCES[current_sentence_index], 120)
                go_button.draw(screen)
            else:
                # Show current round timer
                elapsed = (pygame.time.get_ticks() - round_start_time) // 1000
                timer_text = SMALL_FONT.render(f"Time: {elapsed}s", True, TEXT_COLOR)
                screen.blit(timer_text, (WIDTH - 150, 50))

                input_box.draw(screen)
                done_button.draw(screen)
                quit_button.draw(screen)  # ✅ Quit button beside Done

            if feedback:
                fb_surf = SMALL_FONT.render(feedback, True, feedback_color)
                screen.blit(fb_surf, (WIDTH // 2 - fb_surf.get_width() // 2, 430))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()