import pygame
import random
import time
import sqlite3
import tkinter as tk
from tkinter import simpledialog, messagebox

conn = sqlite3.connect("snake_game.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_score (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    score INTEGER,
    level INTEGER,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
""")
conn.commit()

root = tk.Tk()
root.withdraw()
username = simpledialog.askstring("Username", "Enter your username:")

cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
row = cursor.fetchone()
if row:
    user_id = row[0]
    cursor.execute("SELECT score, level FROM user_score WHERE user_id = ? ORDER BY saved_at DESC LIMIT 1", (user_id,))
    data = cursor.fetchone()
    score, level = data if data else (0, 1)
else:
    cursor.execute("INSERT INTO user(username) VALUES (?)", (username,))
    user_id = cursor.lastrowid
    conn.commit()
    score = 0
    level = 1

pygame.init()
BLOCK_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
WIDTH = BLOCK_SIZE * GRID_WIDTH
HEIGHT = BLOCK_SIZE * GRID_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game with Timed Food")

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

font = pygame.font.SysFont("Verdana", 20)
clock = pygame.time.Clock()
speed = 5 + (level - 1) * 2
snake = [(5, 5)]
snake_dir = (1, 0)
walls = [(10, y) for y in range(5, 15)] + [(20, y) for y in range(5, 15)]

def generate_food():
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in snake and pos not in walls:
            weight = random.randint(1, 3)
            timer = time.time() + random.randint(5, 10)
            return {"pos": pos, "weight": weight, "expires": timer}

food = generate_food()
running = True
paused = False

def show_leaderboard():
    cursor.execute("""
        SELECT u.username, MAX(us.score) as max_score FROM user_score us
        JOIN user u ON us.user_id = u.id
        GROUP BY us.user_id
        ORDER BY max_score DESC
        LIMIT 10
    """)
    rows = cursor.fetchall()
    leaderboard = "Top 10 Players:\n"
    for i, (user, max_score) in enumerate(rows, 1):
        leaderboard += f"{i}. {user}: {max_score}\n"
    messagebox.showinfo("Leaderboard", leaderboard)

while running:
    if not paused:
        clock.tick(speed)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_dir != (0, 1):
                snake_dir = (0, -1)
            elif event.key == pygame.K_DOWN and snake_dir != (0, -1):
                snake_dir = (0, 1)
            elif event.key == pygame.K_LEFT and snake_dir != (1, 0):
                snake_dir = (-1, 0)
            elif event.key == pygame.K_RIGHT and snake_dir != (-1, 0):
                snake_dir = (1, 0)
            elif event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_s:
                cursor.execute("INSERT INTO user_score(user_id, score, level) VALUES (?, ?, ?)", (user_id, score, level))
                conn.commit()
                print("Game saved.")

    if not paused:
        head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])

        if head[0] < 0 or head[0] >= GRID_WIDTH or head[1] < 0 or head[1] >= GRID_HEIGHT:
            print("Game Over: Hit the wall")
            cursor.execute("INSERT INTO user_score(user_id, score, level) VALUES (?, ?, ?)", (user_id, score, level))
            conn.commit()
            show_leaderboard()
            break
        if head in snake or head in walls:
            print("Game Over: Collision")
            cursor.execute("INSERT INTO user_score(user_id, score, level) VALUES (?, ?, ?)", (user_id, score, level))
            conn.commit()
            show_leaderboard()
            break

        snake.insert(0, head)

        if head == food["pos"]:
            score += food["weight"]
            if score % 3 == 0:
                level += 1
                speed += 2
            food = generate_food()
        else:
            snake.pop()

        if time.time() > food["expires"]:
            food = generate_food()

        screen.fill(BLACK)

        for wall in walls:
            pygame.draw.rect(screen, BLUE, (wall[0] * BLOCK_SIZE, wall[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        for segment in snake:
            pygame.draw.rect(screen, GREEN, (segment[0] * BLOCK_SIZE, segment[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        green_value = min(100 * food["weight"], 255)
        food_color = (255, green_value, 100)
        pygame.draw.rect(screen, food_color, (food["pos"][0] * BLOCK_SIZE, food["pos"][1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        score_text = font.render(f"User: {username}  Score: {score}  Level: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

pygame.quit()
conn.close()
