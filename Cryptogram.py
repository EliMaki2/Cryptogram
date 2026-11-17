import pygame
import random
import time

windows = []
max_cooldown = 10
cooldown = 10
difficulty = 1
reward = 1
timer = 10
streak = 1
coins = 0

class PygameWindow:
    def __init__(self, width, height, name="Pygame Window", color = (150, 150, 150), difficulty=1, reward=1, time=60):
        self.width = width
        self.height = height
        self.name = name
        self.color = color
        self.difficulty = difficulty
        self.reward = reward
        self.time = time
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.name)
        self.shutoff = False
        self.finish_countdown = 0

    def update_loop(self):
        pass

    def draw_loop(self):
        self.screen.fill(self.color)
        pygame.display.flip()

    def event_loop(self, event):
        pass

    def close(self, finished):
        self.shutoff = True
        if finished:
            return self.reward
        else:
            return False

    def brighten_color(self, factor):
        r, g, b = self.color
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return (r, g, b)

    def shift_color(self, color, r_shift = 0, g_shift = 0, b_shift = 0):
        r, g, b = color
        r = max(0, min(255, r + r_shift))
        g = max(0, min(255, g + g_shift))
        b = max(0, min(255, b + b_shift))
        return (r, g, b)


class Moonpanel(PygameWindow):
    def __init__(self, width, height, name="Cryptogram", color=(150, 150, 150), difficulty=1, reward=1, time=60):
        super().__init__(width, height, name, color, difficulty, reward, time)
        self.x = 2+difficulty*2
        self.y = 2+difficulty*2
        self.grid = []
        self.dots = []
        self.visited = []
        self.position = (0, 0)
        self.possible_moves = []
        self.animation_frames = 0

    def check_available_moves(self, visited, position):
        row, col = position
        moves = []
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < self.y 
                and 0 <= new_col < self.x 
                and (new_row, new_col) not in visited
                ):
                moves.append((new_row, new_col))
        return moves

    def positive_move(self, position, move):
        row, col = position
        new_row, new_col = move
        if (row < new_row or col < new_col):
            return True
        return False

    def forward_cell(self, previous, position):
        pre_row, pre_col = previous
        row, col = position
        dr = row - pre_row
        dc = col - pre_col
        next_row = row + dr
        next_col = col + dc
        return (next_row, next_col)

    def can_reach_target(self, move, path, target):
        # Simple BFS to check if the target is reachable from the move
        queue = [move]
        visited = set(path)
        while queue:
            current = queue.pop(0)
            if current == target:
                return True
            for next_move in self.check_available_moves(visited, current):
                if next_move not in visited:
                    visited.add(next_move)
                    queue.append(next_move)
        return False

    def generate_path(self, print_test=False):
        path = []
        position = (0, 0)
        target = (self.y-1, self.x-1)

        while position != target:
            path.append(position)

            if print_test:
                print(f"Current position: {position}")

            available_moves = self.check_available_moves(path, position)

            if print_test:
                print(f"Available moves: {available_moves}")

            # Remove moves that would make the target unreachable
            reachable_moves = [
                move for move in available_moves
                if self.can_reach_target(move, path, target)
            ]

            if print_test:
                print(f"Reachable moves: {reachable_moves}")

            available_moves = reachable_moves

            if len(available_moves) == 0:
                raise ValueError(
                    f"No reachable moves from position: {position}"
                )

            # Original two-option movement preference
            if len(available_moves) == 2 and len(path) > 1:
                previous_position = path[-2]
                forward = self.forward_cell(previous_position, position)

                if print_test:
                    print(f"Previous position: {previous_position}")
                    print(f"Forward cell: {forward}")

                if forward not in available_moves:
                    if forward in path:
                        preferred_moves = [
                            move for move in available_moves
                            if not self.positive_move(position, move)
                        ]
                    else:
                        preferred_moves = [
                            move for move in available_moves
                            if self.positive_move(position, move)
                        ]

                    # Only apply the preference if it leaves an option
                    if preferred_moves:
                        available_moves = preferred_moves

            # Always prioritize reaching the target if possible
            if target in available_moves:
                available_moves = [target]

            random.shuffle(available_moves)

            # Original randomized movement selection
            selected_move = None

            for move in available_moves:
                if (
                    not self.positive_move(position, move)
                    and len(available_moves) > 1
                ):
                    if random.random() < 0.5:
                        if print_test:
                            print(f"Skipping move to: {move}")
                        continue

                selected_move = move
                break

            # Ensure a move is selected even if all were skipped
            if selected_move is None:
                selected_move = random.choice(available_moves)

            position = selected_move

            if print_test:
                print(f"Moving to: {position}")

        path.append(target)
        return path

    def generate_grid(self, print_test = False):
        self.grid = []
        for row in range(self.y):
            row = []
            for col in range(self.x):
                row.append(" ")
            self.grid.append(row)
        path = self.generate_path(print_test = False)
        if print_test:
            print(f"Generated path: {path}")
        for row in range(self.y):
            for col in range(self.x):
                if print_test:
                    print(f"Generating grid cell at: ({row}, {col})")
                if (row, col) in path:
                    if print_test:
                        print(f"Marking path cell at: ({row}, {col})")
                    self.grid[row][col] = random.choice([" ", " ", "o"])
                    if self.grid[row][col] == "o":
                        self.dots.append((row, col))
                else:
                    if print_test:
                        print(f"Marking non-path cell at: ({row}, {col})")
                    self.grid[row][col] = random.choice([" ", " ", " ", " ", "x"])

        self.grid[0][0] = "S"
        self.grid[self.y-1][self.x-1] = "E"

    def draw_loop(self):
        self.screen.fill(self.brighten_color(.6))
        x_spacing = self.width // self.x
        y_spacing = self.height // self.y
        for row in range(self.y):
            for col in range(self.x):
                pygame.draw.circle(
                    self.screen,
                    self.brighten_color(1.3),
                    (col * x_spacing + x_spacing // 2, row * y_spacing + y_spacing // 2),
                    min(x_spacing, y_spacing) // 9
                )

                for next_row, next_col in ((row, col + 1), (row + 1, col)):
                    if next_row < self.y and next_col < self.x:
                        if self.grid[row][col] != "x" and self.grid[next_row][next_col] != "x":
                            pygame.draw.line(
                                self.screen,
                                self.brighten_color(1.3),
                                (col * x_spacing + x_spacing // 2, row * y_spacing + y_spacing // 2),
                                (next_col * x_spacing + x_spacing // 2, next_row * y_spacing + y_spacing // 2),
                                16
                            )
                        else:
                            pygame.draw.line(
                                self.screen,
                                self.brighten_color(1.3),
                                (col * x_spacing + x_spacing // 2, row * y_spacing + y_spacing // 2),
                                ((col * x_spacing + x_spacing // 2)+((next_col * x_spacing + x_spacing // 2)-(col * x_spacing + x_spacing // 2))*.3,
                                 (row * y_spacing + y_spacing // 2)+((next_row * y_spacing + y_spacing // 2)-(row * y_spacing + y_spacing // 2))*.3),
                                16
                            )
                            pygame.draw.line(
                                self.screen,
                                self.brighten_color(1.3),
                                (next_col * x_spacing + x_spacing // 2, next_row * y_spacing + y_spacing // 2),
                                ((next_col * x_spacing + x_spacing // 2)+((col * x_spacing + x_spacing // 2)-(next_col * x_spacing + x_spacing // 2))*.3,
                                 (next_row * y_spacing + y_spacing // 2)+((row * y_spacing + y_spacing // 2)-(next_row * y_spacing + y_spacing // 2))*.3),
                                16
                            )

                if self.grid[row][col] == "o":
                    pygame.draw.circle(
                        self.screen,
                        self.shift_color(self.brighten_color(.1),g_shift=30),
                        (col * x_spacing + x_spacing // 2, row * y_spacing + y_spacing // 2),
                        min(x_spacing, y_spacing) // 16
                    )

                if self.grid[row][col] == "S":
                    pygame.draw.circle(
                        self.screen,
                        self.shift_color(self.brighten_color(3)),
                        (col * x_spacing + x_spacing // 2, row * y_spacing + y_spacing // 2),
                        min(x_spacing, y_spacing) // 6
                    )

                if self.grid[row][col] == "E":
                    center_x = col * x_spacing + x_spacing // 2
                    center_y = row * y_spacing + y_spacing // 2
                    diamond = [
                        (center_x, center_y - y_spacing // 4),
                        (center_x + x_spacing // 4, center_y),
                        (center_x, center_y + y_spacing // 4),
                        (center_x - x_spacing // 4, center_y)
                    ]
                    pygame.draw.polygon(
                        self.screen,
                        self.shift_color(self.brighten_color(1.3)),
                        diamond
                    )

        for row, col in self.visited:
            pygame.draw.circle(
                self.screen,
                self.brighten_color(3),
                (col * x_spacing + x_spacing // 2, row * y_spacing + y_spacing // 2),
                min(x_spacing, y_spacing) // 8
            )

            if self.visited.index((row, col)) + 1 < len(self.visited):
                next_row, next_col = self.visited[(self.visited.index((row, col)) + 1)]
                pygame.draw.line(
                    self.screen,
                    self.brighten_color(3),
                    (col * x_spacing + x_spacing // 2, row * y_spacing + y_spacing // 2),
                    (next_col * x_spacing + x_spacing // 2, next_row * y_spacing + y_spacing // 2),
                    16
                )

            if self.grid[row][col] == "E":
                center_x = col * x_spacing + x_spacing // 2
                center_y = row * y_spacing + y_spacing // 2
                diamond = [
                    (center_x, center_y - y_spacing // 4),
                    (center_x + x_spacing // 4, center_y),
                    (center_x, center_y + y_spacing // 4),
                    (center_x - x_spacing // 4, center_y)
                ]
                pygame.draw.polygon(
                    self.screen,
                    self.shift_color(self.brighten_color(3)),
                    diamond
                )

        for cell in self.possible_moves:
            row, col = cell
            if not self.grid[row][col] == "x":
                pygame.draw.circle(
                    self.screen,
                    self.shift_color(self.brighten_color(1.8),g_shift=50),
                    (col * x_spacing + x_spacing // 2, row * y_spacing + y_spacing // 2),
                    (min(x_spacing, y_spacing) // 8)*(self.animation_frames/40),
                    2
                )

        if len(self.visited) > 1:
            pygame.draw.circle(
                self.screen,
                self.shift_color(self.brighten_color(1.8),r_shift=50),
                (self.visited[-2][1] * x_spacing + x_spacing // 2, self.visited[-2][0] * y_spacing + y_spacing // 2),
                (min(x_spacing, y_spacing) // 8)*(self.animation_frames/40),
                2
            )

        font = pygame.font.SysFont(None, 36)
        time_text = font.render(f"Time: {round(self.time, 2)}", True, (255, 255, 255))
        self.screen.blit(time_text, (10, 10))

        if self.finish_countdown > 0:
            tint_surface = pygame.Surface((self.width, self.height))
            tint_surface.set_alpha(128)  # Adjust the alpha value as needed
            tint_surface.fill((0, 255, 0))  # green tint
            self.screen.blit(tint_surface, (0, 0))

        pygame.display.flip()

    def update_loop(self):
        self.animation_frames += 1
        if self.animation_frames > 40:
            self.animation_frames = 0
        self.possible_moves = self.check_available_moves(self.visited, self.position)
        if self.position not in self.visited:
            self.visited.append(self.position)
        if self.grid[self.position[0]][self.position[1]] == "E" and self.finish_countdown == 0:
            dot_missed = False
            for dot in self.dots:
                if not dot in self.visited:
                    dot_missed = True
            if not dot_missed:
                self.finish_countdown = 5
        self.time -= 1/60
        if self.time <= 0:
            return self.close(False)
        if self.finish_countdown > 0:
            self.finish_countdown -= 1
        if self.finish_countdown == 1:
            return self.close(True)
        

    def event_loop(self, event):
        if self.finish_countdown == 0:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                col = mouse_pos[0] // (self.width // self.x)
                row = mouse_pos[1] // (self.height // self.y)
                if (row, col) in self.possible_moves:
                    if self.grid[row][col] == "x":
                        return
                    self.position = (row, col)
                    self.visited.append(self.position)
                if len(self.visited) > 1:
                    if (row, col) == self.visited[-2]:
                        self.position = (row, col)
                        self.visited.pop()
                        self.visited.pop()


class Sigilboard(PygameWindow):
    def __init__(self, width, height, name="Cryptogram", color=(150, 150, 150), difficulty=1, reward=1, time=60):
        super().__init__(width, height, name, color, difficulty, reward, time) 
        self.sigils = []
        self.sigil_amount = difficulty+3
        self.grid_size = 12+difficulty*4
        self.x = random.randint(3,(self.grid_size)//3)
        self.y = int(self.grid_size/self.x)
        self.grid = []

    def avalible_positions(self, path, position):
        col, row = position
        possibles = [(col+1,row),(col-1,row),(col,row+1),(col,row-1)]
        for option in possibles[:]:
            new_col, new_row = option
            if new_col < 0 or new_col >= self.x or new_row < 0 or new_row >= self.y:
                possibles.remove(option)
            elif option in path:
                possibles.remove(option)
            elif self.grid[new_row][new_col] != " ":
                possibles.remove(option)
        return possibles

    def generate_grid(self):
        self.grid = []
        for row in range(self.y):
            row_list = []
            for col in range(self.x):
                row_list.append(" ")
            self.grid.append(row_list)

        sigil_id = 1
        max_total_attempts = 100
        total_attempts = 0
        
        while len(self.sigils) < self.sigil_amount and total_attempts < max_total_attempts:
            total_attempts += 1
            
            # Find an empty starting position
            start_col = None
            start_row = None
            for row in range(self.y):
                for col in range(self.x):
                    if self.grid[row][col] == " ":
                        start_col = col
                        start_row = row
                        break
                if start_col is not None:
                    break
            
            # If no empty position found, we're done
            if start_col is None:
                break
            
            # Build a tetrinomino starting from this position
            tetrinomino = [(start_col, start_row)]
            max_attempts = 20
            attempt = 0
            
            while len(tetrinomino) < 4 and attempt < max_attempts:
                attempt += 1
                # Get available positions from all current cells in tetrinomino
                all_possibles = []
                for cell in tetrinomino:
                    possibles = self.avalible_positions(tetrinomino, cell)
                    all_possibles.extend(possibles)
                
                # Remove duplicates
                all_possibles = list(set(all_possibles))
                
                if not all_possibles:
                    # Dead end - reset and try again
                    break
                
                # Pick a random next cell
                next_cell = random.choice(all_possibles)
                tetrinomino.append(next_cell)

            if attempt == max_attempts:
                self.sigils.append(tetrinomino)
                self.sigil_amount += 1
            
            # Only add if we completed a tetrinomino
            if len(tetrinomino) == 4:
                self.sigils.append(tetrinomino)
                for col, row in tetrinomino:
                    self.grid[row][col] = sigil_id
                sigil_id += 1

        for row in range(self.y):
            for col in range(self.x):
                if self.grid[row][col] != " ":
                    self.grid[row][col] = " "

    def draw_loop(self):
        self.screen.fill(self.brighten_color(.6))
        grid_height = self.height*.7
        grid_x_scale = self.width / (self.x+1)
        grid_y_scale = grid_height / (self.y+1)
        grid_scale = min(grid_x_scale, grid_y_scale)
        rect = pygame.Rect(0, grid_height, self.width, self.height - grid_height)
        pygame.draw.rect(self.screen, self.brighten_color(1.1), rect)
        for row in range(self.y+1):
            if row == 0:
                continue
            for col in range(self.x+1):
                if col == 0:
                    continue
                rect = pygame.Rect(col * grid_scale, row * grid_scale, grid_scale, grid_scale)
                pygame.draw.rect(self.screen, self.brighten_color(1.3), rect, 2)

        for sigil in self.sigils:
            for col, row in sigil:
                rect = pygame.Rect(col * grid_scale, row * grid_scale, grid_scale, grid_scale)
                pygame.draw.rect(self.screen, self.brighten_color(1.5), rect)
        
        pygame.display.flip()
        

def create_moonpanel(width, height, title, color, difficulty, reward, time):
    panel = Moonpanel(width, height, title, color, difficulty, reward, time)
    panel.generate_grid()
    windows.append(panel)
    print(f"\nCreated Moonpanel with difficulty {difficulty} and reward {reward}")
    return panel

def create_sigilboard(width, height, title, color, difficulty, reward, time):
    board = Sigilboard(width, height, title, color, difficulty, reward, time)
    board.generate_grid()
    windows.append(board)
    print(f"\nCreated Sigilboard with difficulty {difficulty} and reward {reward}")
    return board

def run_pygame_loop():
    global max_cooldown, cooldown, difficulty, reward, timer, streak, coins
    clock = pygame.time.Clock()
    for window in windows:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                window.shutoff = True
                print("Try Again!\n")
                reward = max(1, reward - streak)
                streak = 1
                max_cooldown = max_cooldown * .9
                difficulty = max(1, difficulty - .4)
                cooldown = max_cooldown
            window.event_loop(event)
        result = window.update_loop()
        if result is not None:
            window.shutoff = True
            if result:
                coins += reward
                print("Good Work!")
                print(f"Cryptocoins: {coins}\n")
                streak += 1
                difficulty += .1*streak
                max_cooldown = max_cooldown * (1+(streak/5))
                reward += streak
                cooldown = max_cooldown
            else:
                print("Try Again!\n")
                reward = max(1, reward - streak)
                streak = 1
                max_cooldown = max_cooldown * .9
                difficulty = max(1, difficulty - .4)
                cooldown = max_cooldown
        window.draw_loop()
        for window in windows:
            if window.shutoff:
                windows.remove(window)
    clock.tick(60)

def create_cryptogram(difficulty, reward, timer):
    difficulty = round(difficulty)
    cryprogram = random.choice(["Moonpanel", "Sigilboard"])
    color = random.choice([(70, 70, 130), (70, 130, 70), (130, 70, 70),
                           (130, 130, 70), (130, 70, 130), (70, 130, 130), 
                           (70, 70, 70), (110, 110, 110), (130, 130, 130),
                           (110, 130, 70), (130, 110, 70), (110, 110, 70),
                           (110, 70, 130), (110, 70, 130), (110, 70, 110),
                           (70, 110, 130), (70, 130, 110), (70, 110, 110)])
    if cryprogram == "Moonpanel":
        create_moonpanel(600, 600, "Moonpanel Window", color, difficulty, reward*difficulty, 15+(difficulty*timer))
    elif cryprogram == "Sigilboard":
        create_sigilboard(600, 700, "Sigilboard Window", color, difficulty, reward*difficulty, 25+(difficulty*timer))


if __name__ == '__main__':    
    running = True
    pygame_initialized = False

    while running:
        if windows:
            if not pygame_initialized:
                pygame.init()
                pygame_initialized = True
            run_pygame_loop()
        else:
            if pygame_initialized:
                pygame.quit()
                pygame_initialized = False
            if cooldown <= 60:
                print(f"\rCooldown: {round(cooldown)} Seconds                         ", end="", flush=True)
            elif cooldown <= 3600:
                print(f"\rCooldown: {round(cooldown//60)} Minutes, {round(cooldown%60)} Seconds                   ", end="", flush=True)
            else:
                print(f"\rCooldown: {round(cooldown//3600)} Hours, {round((cooldown%3600)//60)} Minutes, {round(cooldown%60)} Seconds    ", end="", flush=True)
            cooldown -= 1
            time.sleep(1)
            if cooldown <= 0:
                create_cryptogram(difficulty, reward, timer)