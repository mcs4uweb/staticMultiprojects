import random
import sys
import pygame


WIDTH = 900
HEIGHT = 520
FPS = 60

STEP_TOTAL = 2.2
RESULT_AT = 0.7
CARRY_AT = 1.2

BG_COLOR = (245, 244, 238)
TEXT_COLOR = (30, 30, 30)
CARRY_COLOR = (190, 60, 60)
HIGHLIGHT_COLOR = (255, 220, 150, 120)
LINE_COLOR = (50, 50, 50)
INFO_COLOR = (70, 70, 70)


def build_steps(a_value, b_value):
    a_str = str(a_value)
    b_str = str(b_value)
    result = a_value + b_value
    result_str = str(result)

    num_cols = max(len(a_str), len(b_str), len(result_str))
    calc_a = [int(ch) for ch in a_str.zfill(num_cols)]
    calc_b = [int(ch) for ch in b_str.zfill(num_cols)]

    display_a = [None] * num_cols
    display_b = [None] * num_cols

    start_a = num_cols - len(a_str)
    start_b = num_cols - len(b_str)

    for i, ch in enumerate(a_str):
        display_a[start_a + i] = int(ch)
    for i, ch in enumerate(b_str):
        display_b[start_b + i] = int(ch)

    steps = []
    carry = 0
    for col in range(num_cols - 1, -1, -1):
        total = calc_a[col] + calc_b[col] + carry
        sum_digit = total % 10
        carry_out = total // 10
        steps.append(
            {
                "col": col,
                "a": calc_a[col],
                "b": calc_b[col],
                "carry_in": carry,
                "sum_digit": sum_digit,
                "carry_out": carry_out,
                "total": total,
            }
        )
        carry = carry_out

    return {
        "num_cols": num_cols,
        "display_a": display_a,
        "display_b": display_b,
        "steps": steps,
        "result": result,
    }


def draw_digit(surface, font, digit, pos, color):
    if digit is None:
        return
    text = font.render(str(digit), True, color)
    rect = text.get_rect(center=pos)
    surface.blit(text, rect)


def generate_problem():
    for _ in range(80):
        digits_a = random.randint(4, 5)
        digits_b = random.randint(4, 5)
        a_value = random.randint(10 ** (digits_a - 1), (10 ** digits_a) - 1)
        b_value = random.randint(10 ** (digits_b - 1), (10 ** digits_b) - 1)

        max_digits = max(digits_a, digits_b)
        carry = 0
        has_carry = False
        for i in range(max_digits):
            a_digit = (a_value // (10 ** i)) % 10
            b_digit = (b_value // (10 ** i)) % 10
            if a_digit + b_digit + carry >= 10:
                has_carry = True
            carry = 1 if a_digit + b_digit + carry >= 10 else 0

        if has_carry:
            return a_value, b_value

    return a_value, b_value


def configure_problem(a_value, b_value, spacing):
    data = build_steps(a_value, b_value)
    num_cols = data["num_cols"]
    display_a = data["display_a"]
    display_b = data["display_b"]
    steps = data["steps"]

    results = [None] * num_cols
    carry_display = [None] * num_cols
    carry_anim = {}

    total_width = (num_cols - 1) * spacing
    left_x = (WIDTH - total_width) / 2
    col_x = [left_x + i * spacing for i in range(num_cols)]

    plus_x = col_x[0] - spacing * 0.8
    line_start = plus_x - 15
    line_end = col_x[-1] + spacing * 0.45

    return (
        num_cols,
        display_a,
        display_b,
        steps,
        results,
        carry_display,
        carry_anim,
        col_x,
        plus_x,
        line_start,
        line_end,
    )


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Old School Addition")
    clock = pygame.time.Clock()

    big_font = pygame.font.SysFont("Consolas", 64)
    carry_font = pygame.font.SysFont("Consolas", 36)
    info_font = pygame.font.SysFont("Consolas", 28)

    spacing = 80
    carry_y = 80
    top_y = 160
    second_y = 240
    line_y = 280
    result_y = 360
    info_y = 440

    highlight_top = carry_y - 30
    highlight_height = result_y - carry_y + 70
    highlight_width = spacing * 0.9

    a_value = 1129
    b_value = 147
    (
        num_cols,
        display_a,
        display_b,
        steps,
        results,
        carry_display,
        carry_anim,
        col_x,
        plus_x,
        line_start,
        line_end,
    ) = configure_problem(a_value, b_value, spacing)

    step_index = 0
    step_start = pygame.time.get_ticks() / 1000.0
    step_result_written = False
    step_carry_written = False

    running = True
    while running:
        now = pygame.time.get_ticks() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    if step_index >= len(steps):
                        a_value, b_value = generate_problem()
                    (
                        num_cols,
                        display_a,
                        display_b,
                        steps,
                        results,
                        carry_display,
                        carry_anim,
                        col_x,
                        plus_x,
                        line_start,
                        line_end,
                    ) = configure_problem(a_value, b_value, spacing)
                    step_index = 0
                    step_start = now
                    step_result_written = False
                    step_carry_written = False

        if step_index < len(steps):
            step = steps[step_index]
            elapsed = now - step_start

            if (not step_result_written) and elapsed >= RESULT_AT:
                results[step["col"]] = step["sum_digit"]
                step_result_written = True

            if (not step_carry_written) and elapsed >= CARRY_AT:
                if step["carry_out"] > 0 and step["col"] - 1 >= 0:
                    carry_display[step["col"] - 1] = step["carry_out"]
                    carry_anim[step["col"] - 1] = now
                step_carry_written = True

            if elapsed >= STEP_TOTAL:
                step_index += 1
                step_start = now
                step_result_written = False
                step_carry_written = False

        screen.fill(BG_COLOR)

        if step_index < len(steps):
            current_col = steps[step_index]["col"]
            highlight = pygame.Surface((highlight_width, highlight_height), pygame.SRCALPHA)
            highlight.fill(HIGHLIGHT_COLOR)
            highlight_rect = highlight.get_rect(
                center=(col_x[current_col], highlight_top + highlight_height / 2)
            )
            screen.blit(highlight, highlight_rect)

        pygame.draw.line(
            screen,
            LINE_COLOR,
            (line_start, line_y),
            (line_end, line_y),
            3,
        )

        for i in range(num_cols):
            draw_digit(screen, carry_font, carry_display[i], (col_x[i], carry_y), CARRY_COLOR)
            draw_digit(screen, big_font, display_a[i], (col_x[i], top_y), TEXT_COLOR)
            draw_digit(screen, big_font, display_b[i], (col_x[i], second_y), TEXT_COLOR)
            draw_digit(screen, big_font, results[i], (col_x[i], result_y), TEXT_COLOR)

        for col, start_time in list(carry_anim.items()):
            delta = now - start_time
            if delta <= 0.5:
                drop = max(0, 1 - (delta / 0.5))
                y_offset = -18 * drop
                draw_digit(
                    screen,
                    carry_font,
                    carry_display[col],
                    (col_x[col], carry_y + y_offset),
                    CARRY_COLOR,
                )
            else:
                carry_anim.pop(col, None)

        plus_text = big_font.render("+", True, TEXT_COLOR)
        plus_rect = plus_text.get_rect(center=(plus_x, second_y))
        screen.blit(plus_text, plus_rect)

        if step_index < len(steps):
            step = steps[step_index]
            if step["carry_in"] > 0:
                equation = f"{step['a']} + {step['b']} + {step['carry_in']} = {step['total']}"
            else:
                equation = f"{step['a']} + {step['b']} = {step['total']}"
            info = info_font.render(equation, True, INFO_COLOR)
            info_rect = info.get_rect(center=(WIDTH / 2, info_y))
            screen.blit(info, info_rect)
        else:
            done_text = info_font.render("Press R to replay", True, INFO_COLOR)
            done_rect = done_text.get_rect(center=(WIDTH / 2, info_y))
            screen.blit(done_text, done_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
