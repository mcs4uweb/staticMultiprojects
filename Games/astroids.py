import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen settings
WIDTH, HEIGHT = 1000, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Fonts
font = pygame.font.SysFont('Arial', 24)

# Game clock
clock = pygame.time.Clock()

# Player class
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.speed = 0
        self.rotation_speed = 3
        self.thrust = 0.2
        self.radius = 15
        self.bullets = []
        self.shoot_cooldown = 0

    def update(self):
        # Rotate left/right
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.angle -= self.rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle += self.rotation_speed

        # Thrust forward
        if keys[pygame.K_UP]:
            self.speed += self.thrust
        else:
            self.speed *= 0.98  # Friction

        # Move
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y -= math.sin(rad) * self.speed

        # Wrap around screen
        self.x %= WIDTH
        self.y %= HEIGHT

        # Shoot
        self.shoot_cooldown -= 1
        if keys[pygame.K_SPACE] and self.shoot_cooldown <= 0:
            self.shoot_cooldown = 15  # Cooldown frames
            rad = math.radians(self.angle)
            bullet_x = self.x + math.cos(rad) * self.radius
            bullet_y = self.y - math.sin(rad) * self.radius
            self.bullets.append(Bullet(bullet_x, bullet_y, self.angle))

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.lifetime <= 0:
                self.bullets.remove(bullet)

    def draw(self, surface):
        # Draw ship as triangle
        rad = math.radians(self.angle)
        points = [
            (self.x + math.cos(rad) * self.radius, self.y - math.sin(rad) * self.radius),
            (self.x + math.cos(rad + 2.5) * self.radius, self.y - math.sin(rad + 2.5) * self.radius),
            (self.x + math.cos(rad - 2.5) * self.radius, self.y - math.sin(rad - 2.5) * self.radius)
        ]
        pygame.draw.polygon(surface, WHITE, points, 2)

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(surface)

# Bullet class
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.radius = 2
        self.lifetime = 60  # Frames before disappearing

    def update(self):
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y -= math.sin(rad) * self.speed
        self.x %= WIDTH
        self.y %= HEIGHT
        self.lifetime -= 1

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)

# Asteroid class
class Asteroid:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size  # 3=large, 2=medium, 1=small
        self.radius = size * 20
        self.angle = random.randint(0, 359)
        self.speed = random.uniform(1, 3)
        self.rotation_speed = random.uniform(-2, 2)
        self.points = self.generate_points()

    def generate_points(self):
        points = []
        for i in range(8):
            angle = math.radians(i * 45 + random.randint(-15, 15))
            distance = self.radius + random.randint(-10, 10)
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            points.append((x, y))
        return points

    def update(self):
        # Move
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y -= math.sin(rad) * self.speed
        self.x %= WIDTH
        self.y %= HEIGHT

        # Rotate
        self.angle += self.rotation_speed

    def draw(self, surface):
        # Draw asteroid as polygon
        rotated_points = [(self.x + p[0], self.y + p[1]) for p in self.points]
        pygame.draw.polygon(surface, WHITE, rotated_points, 2)

    def split(self):
        if self.size > 1:
            new_size = self.size - 1
            # Create two smaller asteroids
            return [
                Asteroid(self.x, self.y, new_size),
                Asteroid(self.x, self.y, new_size)
            ]
        return []

# Game state
player = Player()
asteroids = []
score = 0
game_over = False

# Spawn initial asteroids
for _ in range(5):
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    asteroids.append(Asteroid(x, y, 3))

# Main game loop
running = True
while running:
    dt = clock.tick(60)  # 60 FPS

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                # Restart game
                player = Player()
                asteroids = []
                score = 0
                game_over = False
                for _ in range(5):
                    x = random.randint(50, WIDTH - 50)
                    y = random.randint(50, HEIGHT - 50)
                    asteroids.append(Asteroid(x, y, 3))

    if not game_over:
        # Update
        player.update()

        # Check bullet-asteroid collisions
        for bullet in player.bullets[:]:
            for asteroid in asteroids[:]:
                dx = bullet.x - asteroid.x
                dy = bullet.y - asteroid.y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance < asteroid.radius + bullet.radius:
                    # Remove bullet
                    player.bullets.remove(bullet)
                    # Split asteroid
                    new_asteroids = asteroid.split()
                    asteroids.remove(asteroid)
                    asteroids.extend(new_asteroids)
                    score += 10 * asteroid.size
                    break

        # Update asteroids
        for asteroid in asteroids[:]:
            asteroid.update()

        # Check player-asteroid collision
        for asteroid in asteroids:
            dx = player.x - asteroid.x
            dy = player.y - asteroid.y
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < asteroid.radius + player.radius:
                game_over = True

    # Draw
    screen.fill(BLACK)

    if not game_over:
        player.draw(screen)
        for asteroid in asteroids:
            asteroid.draw(screen)

        # Draw score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
    else:
        # Game over screen
        game_over_text = font.render("GAME OVER - Press R to Restart", True, RED)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))

    pygame.display.flip()

pygame.quit()
sys.exit()
