#!/usr/bin/env python
import asyncio
import random
from js import document
from pyodide.ffi import create_proxy

# Global flag to capture flap input from key events.
flap_requested = False

def keydown_handler(event):
    global flap_requested
    # Check if the pressed key is either space or 'f'
    if event.key == ' ' or event.key.lower() == 'f':
        flap_requested = True

# Create a proxy for the keydown event handler.
keydown_proxy = create_proxy(keydown_handler)
document.addEventListener("keydown", keydown_proxy)

async def main():
    # Disable the command input field while the game is running.
    commandInput = document.getElementById("command")
    commandInput.disabled = True

    # Game settings.
    board_width = 60
    board_height = 20
    bird_x = 5
    bird_y = board_height // 2
    velocity = 0
    gravity = 0.8
    # Reduced jump strength for a less aggressive flap.
    flap_strength = -2

    # Pipe settings.
    pipes = []  # Each pipe is a dict with keys 'x' and 'gap_y'
    pipe_gap = 8
    pipe_distance = 30  # Minimum distance between pipes
    score = 0

    # Create the initial pipe at the right edge.
    pipes.append({
        'x': board_width,
        'gap_y': random.randint(1, board_height - pipe_gap - 1)
    })

    # Create a <pre> element for game output.
    game_div = document.createElement("pre")
    game_div.style.fontFamily = "monospace"
    game_div.style.whiteSpace = "pre"
    terminal = document.getElementById("terminal")
    terminal.appendChild(game_div)

    game_over = False

    while not game_over:
        # Update bird position.
        bird_y += velocity
        velocity += gravity

        # Check vertical boundaries.
        if bird_y < 0 or bird_y >= board_height:
            game_over = True

        # Move pipes leftward.
        for pipe in pipes:
            pipe['x'] -= 1

        # Add a new pipe when the last one is far enough.
        if pipes[-1]['x'] < board_width - pipe_distance:
            pipes.append({
                'x': board_width,
                'gap_y': random.randint(1, board_height - pipe_gap - 1)
            })

        # Remove pipes that have left the screen and update score.
        if pipes[0]['x'] < -1:
            pipes.pop(0)
            score += 1

        # Check for collisions.
        for pipe in pipes:
            if pipe['x'] == bird_x:
                if not (pipe['gap_y'] <= bird_y < pipe['gap_y'] + pipe_gap):
                    game_over = True

        # Handle user input for a flap.
        global flap_requested
        if flap_requested:
            velocity = flap_strength
            flap_requested = False

        # Build the game board.
        board = [[' ' for _ in range(board_width)] for _ in range(board_height)]
        for pipe in pipes:
            x = pipe['x']
            if 0 <= x < board_width:
                for y in range(board_height):
                    if not (pipe['gap_y'] <= y < pipe['gap_y'] + pipe_gap):
                        board[y][x] = '#'
        if 0 <= int(bird_y) < board_height:
            board[int(bird_y)][bird_x] = '>'

        # Convert board to string and update the game display.
        board_lines = ["".join(row) for row in board]
        board_str = "\n".join(board_lines)
        game_div.textContent = board_str + f"\nScore: {score}\nPress 'f' or Space to flap."

        await asyncio.sleep(0.1)

    # Game over: display final score.
    game_div.textContent += "\nGame Over!"
    game_div.textContent += f"\nFinal Score: {score}"
    # Wait a moment to let the user see the final score.
    await asyncio.sleep(2)
    # Clean up the game display.
    game_div.remove()

    # Re-enable the command input field.
    commandInput.disabled = False

    # Remove the keydown event listener.
    document.removeEventListener("keydown", keydown_proxy)

    return f"Final Score: {score}"

# Schedule the main game loop as a task.
asyncio.create_task(main())
