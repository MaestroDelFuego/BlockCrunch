import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions and colors
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 600
GRID_SIZE = 10  # 10x10 grid
CELL_SIZE = SCREEN_WIDTH // GRID_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
BORDER_COLOR = (50, 50, 50)  # Dark gray border for blocks
COLORS = [
    (70, 130, 180),  # Steel Blue
    (255, 99, 71),   # Tomato
    (50, 205, 50),   # Lime Green
    (255, 215, 0),   # Gold
    (138, 43, 226),  # Blue Violet
    (255, 105, 180), # Hot Pink
    (255, 165, 0),   # Orange
]

# Set up screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Block Blast Game")

# Create the game grid; each cell will store a color or None
grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Define block shapes excluding 7x1
BLOCK_SHAPES = [
    [(0, 0)],                         # 1x1 Block
    [(0, 0), (1, 0)],                 # 1x2 Block
    [(0, 0), (0, 1)],                 # 2x1 Block
    [(0, 0), (0, 1)],                 # L-shape
    [(0, 0), (1, 0), (0, 1), (1, 1)], # 2x2 Block
    [(0, 0), (1, 0), (2, 0)],         # 3x1 Block
    [(0, 0), (1, 0), (2, 0), (3, 0)], # 4x1 Block
    [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)],  # 6x1 Block
    [(0, 0), (0, 1), (0, 2)],         # 3x1 Vertical Block
    [(0, 0), (1, 0), (1, 1)],         # Square Block (2x2)
    [(0, 0), (1, 0), (1, 1), (1, 2)], # 2x3 Block
]

# Function to create a random block with a random color
def create_block():
    shape = random.choice(BLOCK_SHAPES)
    color = random.choice(COLORS)
    return {"shape": shape, "color": color, "pos": (0, 0)}

current_block = create_block()
score = 0
mouse_dragging = False  # Flag to indicate if the mouse is dragging the block

def draw_grid():
    """Draw the 10x10 game grid with blocks."""
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)  # Draw cell borders
            if grid[y][x] is not None:  # Draw cell with its color if occupied
                # Draw the block with a border
                block_rect = pygame.Rect(x * CELL_SIZE + 2, y * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4)
                pygame.draw.rect(screen, grid[y][x], block_rect)
                pygame.draw.rect(screen, BORDER_COLOR, block_rect, 1)  # Draw border

def draw_block(block):
    """Draw the current block on the screen."""
    for x, y in block["shape"]:
        rect = pygame.Rect((x + block["pos"][0]) * CELL_SIZE,
                           (y + block["pos"][1]) * CELL_SIZE,
                           CELL_SIZE, CELL_SIZE)
        # Draw the block with a border
        block_rect = pygame.Rect(rect.x + 2, rect.y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
        pygame.draw.rect(screen, block["color"], block_rect)
        pygame.draw.rect(screen, BORDER_COLOR, block_rect, 1)  # Draw border

def can_move_block(block, new_pos):
    """Check if the block can be moved to the new position (ignores occupied cells)."""
    for x, y in block["shape"]:
        grid_x = x + new_pos[0]
        grid_y = y + new_pos[1]
        if grid_x < 0 or grid_x >= GRID_SIZE or grid_y < 0 or grid_y >= GRID_SIZE:
            return False  # Out of bounds
    return True

def can_place_block(block, pos):
    """Check if the block can be placed at the specified position (respects occupied cells)."""
    for x, y in block["shape"]:
        grid_x = x + pos[0]
        grid_y = y + pos[1]
        if grid_y >= GRID_SIZE or grid_x < 0 or grid_x >= GRID_SIZE or grid[grid_y][grid_x] is not None:
            return False  # Collides with existing block or out of bounds
    return True

def place_block(block):
    """Place the block on the grid, with its color."""
    for x, y in block["shape"]:
        grid_y = y + block["pos"][1]
        grid_x = x + block["pos"][0]
        if 0 <= grid_x < GRID_SIZE and grid_y < GRID_SIZE:
            grid[grid_y][grid_x] = block["color"]  # Store the block's color in the grid

def clear_full_lines():
    """Clear completed rows and update the score."""
    global grid, score
    cleared_rows = 0
    
    # Clear full horizontal lines
    new_grid = [row for row in grid if any(cell is None for cell in row)]
    cleared_rows += GRID_SIZE - len(new_grid)

    # Extend new_grid to the full grid size with None rows
    while len(new_grid) < GRID_SIZE:
        new_grid.insert(0, [None] * GRID_SIZE)

    # Update the grid to the new grid
    grid[:] = new_grid

    score += cleared_rows * 10  # Award 10 points per cleared row

    # Clear full vertical lines
    for x in range(GRID_SIZE):
        if all(grid[y][x] is not None for y in range(GRID_SIZE)):
            cleared_rows += 1
            for y in range(GRID_SIZE):
                grid[y][x] = None  # Clear the vertical line

    score += cleared_rows * 10  # Award additional points for vertical clears

def check_game_over(block):
    """Check if the game is over (no more moves available for the new block)."""
    return not any(can_place_block(block, (x, 0)) for x in range(GRID_SIZE))

def main():
    global current_block, mouse_dragging
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(WHITE)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Try placing the block, but only if it doesn't overlap
                    if can_place_block(current_block, current_block["pos"]):
                        place_block(current_block)
                        clear_full_lines()
                        # Check if the new block can be placed; if not, game over
                        if check_game_over(current_block):
                            running = False  # End game loop
                        else:
                            current_block = create_block()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    mouse_dragging = False
                    # Attempt to place the block at the current mouse position
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid_x = mouse_x // CELL_SIZE
                    grid_y = mouse_y // CELL_SIZE
                    if can_place_block(current_block, (grid_x, grid_y)):
                        place_block(current_block)
                        clear_full_lines()
                        # Check if the new block can be placed; if not, game over
                        if check_game_over(current_block):
                            running = False  # End game loop
                        else:
                            current_block = create_block()
                elif event.button == 3:  # Right mouse button (to reset block position)
                    current_block["pos"] = (0, 0)
                    
        # Handle dragging
        if mouse_dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = mouse_x // CELL_SIZE
            grid_y = mouse_y // CELL_SIZE
            current_block["pos"] = (grid_x, grid_y)
            if not can_move_block(current_block, current_block["pos"]):
                current_block["pos"] = (0, 0)  # Reset to original position if invalid

        draw_grid()
        draw_block(current_block)

        # Display the score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, BLACK)
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
