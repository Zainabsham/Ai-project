import pygame # Main library for creating the GUI
import sys # System library for exiting the program
import random # For randomizing puzzle tiles during shuffling
from collections import deque # For implementing BFS using a double-ended queue
import heapq # For implementing UCS using a priority queue
import time # For delays and displaying solution steps sequentially
import os # For clearing the terminal during specific operations

# Clears the terminal screen
def clear_terminal():
    os.system('cls') # Using 'cls' for Windows

# Initialize Pygame
pygame.init()

# Constants for screen dimensions and puzzle settings
WIDTH = 400
HEIGHT = 500  # Extra space for buttons and messages
GRID_SIZE = 3  # Size of the puzzle grid (3x3 for an 8-puzzle)
SQUARE_SIZE = WIDTH // GRID_SIZE  # Calculate square size dynamically (400/3 = 133.3333 -> 133 only (floor value))
FONT = pygame.font.SysFont(None, 80)  # Large font for puzzle numbers
FONT_SMALL = pygame.font.SysFont(None, 20)  # Small font for button text

# Colors used in the UI
WHITE = (255, 255, 255) # White for drawing grid lines and buttons
BLACK = (0, 0, 0) # Black for text on buttons
BG_COLOR = (50, 50, 50) # Dark background color
TEXT_COLOR = (255, 255, 255) # White for puzzle tile numbers

# Set up the display screen
screen = pygame.display.set_mode((WIDTH, HEIGHT)) # Create a surface for rendering program elements
pygame.display.set_caption('8 Puzzle Solver')  # Title of the window

# Puzzle States
goal_state = [[1, 2, 3],  # The solved puzzle configuration (List with 3 lists for 3 rows)
              [4, 5, 6],
              [7, 8, 0]]  # 0 represents the blank tile

# Initialize the puzzle state to the goal state (deep copy of the puzzle configuration; to preserve goal state)
initial_state = [row[:] for row in goal_state]
# [:] -> slice notation; used for copying 'goal_state' rows without it getting modified in the future

# Function to draw the puzzle grid and tiles (rendering the puzzle)
def draw_puzzle(state, is_solution=False):
    for row in range(GRID_SIZE):      # Loop through each cell in the grid (2 for loops (rows, cols))
        for col in range(GRID_SIZE):
            value = state[row][col]  # Get the value at the current grid position
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 2)  # Draw the grid cell
            # (screen: the surface, WHITE: border color, rect: squares dimensions, 2: border thickness)
            if value != 0:  # Draw all tiles but the blank tile (tile with the value 0, not drawn)
                color = (0, 255, 0) if is_solution else TEXT_COLOR  # Green for solution state, otherwise, White
                text = FONT.render(str(value), True, color) # text to be rendered
                text_rect = text.get_rect(center=rect.center) # center text on tile
                screen.blit(text, text_rect)  # Draw the number on the tile

    if is_solution:
        # Pause to display the solved puzzle for a few seconds
        pygame.display.update() # Push changes from buffer to surface
        time.sleep(3) # wait for user to see changes (3 seconds)

# Function to find the position of the blank tile (0)
def find_zero(state):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if state[row][col] == 0:
                return (row, col)  # Return the coordinates of the blank tile
    return None

# Function to generate valid neighboring states by sliding tiles
def get_neighbors(state):
    zero_pos = find_zero(state)  # Get the blank tile's coordinates
    neighbors = [] # List that holds the new states
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    for dr, dc in directions: # dr: rows direction, dc: columns direction
        new_row, new_col = zero_pos[0] + dr, zero_pos[1] + dc
        if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:  # Check bounds
            new_state = [row[:] for row in state]  # Deep copy the current state
            # Swap the blank tile value with the adjacent tile, and vice versa
            new_state[zero_pos[0]][zero_pos[1]] = new_state[new_row][new_col]
            new_state[new_row][new_col] = 0
            neighbors.append(new_state)  # Add the new state to the neighbors list
    return neighbors

# Function to check if the puzzle is solvable
def is_solvable(state):
    # Flatten the puzzle grid, excluding the blank tile (0)
    flat_state = [num for row in state for num in row if num != 0]
    inversions = 0
    # Count the number of inversions
    for i in range(len(flat_state)):
        for j in range(i + 1, len(flat_state)): # Check the number after the current number
            if flat_state[i] > flat_state[j]:
                inversions += 1
    # Solvable if the number of inversions is even
    return inversions % 2 == 0

# Function to shuffle the puzzle
def shuffle_puzzle(state, moves=20):
    for _ in range(moves):
        neighbors = get_neighbors(state)  # Get valid moves
        state[:] = random.choice(neighbors)  # Choose a random move
    return state

# Function to reconstruct the path from start to goal
def reconstruct_path(came_from, current):
    path = []
    while current in came_from:  # Backtrack from the goal to the start
        path.append(current)
        current = came_from[current] # Using "current" as a key to get the state that led to current state
    path.reverse()  # Reverse the path to get start-to-goal order
    return path

# Breadth-First Search algorithm
def bfs(start, goal):
    # Initialize the queue, visited set, and parent mapping
    queue = deque([start])
    visited = set()
    visited.add(tuple(tuple(row) for row in start))  # Store states as tuples for immutability
    came_from = {}

    while queue:
        current = queue.popleft()
        if current == goal:  # Check if goal state is reached
            return reconstruct_path(came_from, tuple(tuple(row) for row in current))
        
        for neighbor in get_neighbors(current):
            neighbor_tuple = tuple(tuple(row) for row in neighbor)
            if neighbor_tuple not in visited:
                queue.append(neighbor)
                visited.add(neighbor_tuple)
                came_from[neighbor_tuple] = tuple(tuple(row) for row in current) # Record that the neighbor state was reached from the current state
    return None  # No solution found

def dfs(start, goal, depth_limit=50):
    stack = [(start, [], 0)]  # (current_state, path_taken, depth)
    visited = set()

    while stack:
        current, path, depth = stack.pop()
        current_tuple = tuple(tuple(row) for row in current)

        # If depth exceeds limit, skip further exploration
        if depth > depth_limit:
            continue

        if current_tuple in visited:
            continue
        visited.add(current_tuple)

        # If the goal is reached, return the path
        if current == goal:
            return path + [current]

        # Add neighbors to the stack
        for neighbor in reversed(get_neighbors(current)):
            neighbor_tuple = tuple(tuple(row) for row in neighbor)
            if neighbor_tuple not in visited:
                stack.append((neighbor, path + [current], depth + 1))

    return None  # No solution found

def ucs(start, goal):
    priority_queue = []
    heapq.heappush(priority_queue, (0, start))
    visited = set()
    came_from = {}
    cost_so_far = {tuple(tuple(row) for row in start): 0} # Enables optimality and prevents revisiting states with higher costs

    while priority_queue:
        current_cost, current = heapq.heappop(priority_queue)

        if current == goal:
            return reconstruct_path(came_from, tuple(tuple(row) for row in current))
        
        current_tuple = tuple(tuple(row) for row in current)
        if current_tuple in visited:
            continue
        visited.add(current_tuple)

        for neighbor in get_neighbors(current):
            neighbor_tuple = tuple(tuple(row) for row in neighbor)
            new_cost = current_cost + 1 # Update cost
            if neighbor_tuple not in cost_so_far or new_cost < cost_so_far[neighbor_tuple]: # Compare costs
                cost_so_far[neighbor_tuple] = new_cost # Update cost with the cheaper cost
                heapq.heappush(priority_queue, (new_cost, neighbor))
                came_from[neighbor_tuple] = current_tuple
    return None

def solve_puzzle(method='BFS'):
    clear_terminal()  # Clear terminal before displaying the solution
    if not is_solvable(initial_state):
        print("Puzzle is not solvable!")
        return

    start = [row[:] for row in initial_state]
    goal = [row[:] for row in goal_state]

    if method == 'BFS':
        path = bfs(start, goal)
    elif method == 'DFS':
        path = dfs(start, goal)
    elif method == 'UCS':
        path = ucs(start, goal)
    else:
        print("Unknown method")
        return

    if path:
        display_path(path)
    else:
        print("No solution found")

def draw_buttons():
    button_width = 90
    button_height = 40
    spacing = 10  # Space between buttons
    start_x = (WIDTH - (4 * button_width + 3 * spacing)) // 2
    start_y = HEIGHT - 60
    
    buttons = [
        {"label": "Shuffle", "method": None},
        {"label": "Solve BFS", "method": "BFS"},
        {"label": "Solve DFS", "method": "DFS"},
        {"label": "Solve UCS", "method": "UCS"},
    ]

    button_rects = []
    for i, button in enumerate(buttons): # Get button index and data (for calculations)
        x = start_x + i * (button_width + spacing)
        rect = pygame.Rect(x, start_y, button_width, button_height)
        pygame.draw.rect(screen, WHITE, rect)
        text = FONT_SMALL.render(button["label"], True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
        button_rects.append((rect, button["method"])) # Add buttons rects and methods to "button_rects" list for handling mouse clicks

    return button_rects

def reset_puzzle():
    clear_terminal()  # Clear terminal before displaying the shuffled puzzle
    global initial_state # global: to modify the state in generel (not local to some function)
    initial_state = [row[:] for row in goal_state]
    shuffle_puzzle(initial_state, moves=30)

def display_path(path): # Show the actual swaps on the windows, and the path in the terminal
    for i, state in enumerate(path):
        screen.fill(BG_COLOR)
        draw_puzzle(state, is_solution=(i == len(path) - 1))  # Check if it's the last state
        draw_buttons()
        pygame.display.update()
        time.sleep(0.5) # Delay for 0.5 seconds (between swaps)
        
        # Print the path to the solution in the terminal
        print(f"Step {i + 1}:")
        for row in state:
            print(row)
        print()  # Add a newline for better readability

# Shuffle Initially
shuffle_puzzle(initial_state, moves=30)

# Main Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN: # Listen for left mouse click
            x, y = event.pos # Get cursor coordinates
            button_rects = draw_buttons() # Holds each button index and methods
            for rect, method in button_rects:
                if rect.collidepoint(x, y):
                    if method:
                        solve_puzzle(method=method)
                    else:
                        reset_puzzle()

    # Draw Puzzle and Buttons
    screen.fill(BG_COLOR)
    draw_puzzle(initial_state)
    draw_buttons()
    pygame.display.update()



def draw_puzzle(state, is_solution=False):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            value = state[row][col]
            if value != 0:
                text = FONT.render(str(value), True, TEXT_COLOR)
                rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(screen, WHITE, rect, 2)
                screen.blit(text, text.get_rect(center=rect.center))

