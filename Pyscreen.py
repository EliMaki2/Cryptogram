import pygame

pygame.init()

desktop_sizes = pygame.display.get_desktop_sizes()
user_width, user_height = desktop_sizes[0]
user_width -= 30
user_height -= 30
target_width = 1920
target_height = 1080
width_ratio = user_width / target_width
height_ratio = user_height / target_height
print(f"User screen size: width={user_width}, height={user_height}, target_width={target_width}, target_height={target_height}, width_ratio={width_ratio}, height_ratio={height_ratio}")

screen = pygame.display.set_mode((target_width*width_ratio, target_height*height_ratio))

screen_background: pygame.Surface = pygame.image.load("assets/screen_background.png")
screen_background.set_colorkey((1, 1, 1))
window_leftbar: pygame.Surface = pygame.image.load("assets/window_leftbar.png")
window_leftbar.set_colorkey((1, 1, 1))
window_rightbar: pygame.Surface = pygame.image.load("assets/window_rightbar.png")
window_rightbar.set_colorkey((1, 1, 1))
window_bottombar: pygame.Surface = pygame.image.load("assets/window_bottombar.png")
window_bottombar.set_colorkey((1, 1, 1))
window_topbar: pygame.Surface = pygame.image.load("assets/window_topbar.png")
window_topbar.set_colorkey((1, 1, 1))
window_close_button: pygame.Surface = pygame.image.load("assets/window_close_button.png")
window_close_button.set_colorkey((1, 1, 1))
window_resize: pygame.Surface = pygame.image.load("assets/window_resize.png")
window_resize.set_colorkey((1, 1, 1))

mouse_clicked = False

def point_to_logical(point):
    return (point[0] / width_ratio, point[1] / height_ratio)

def put_item_on_top(list, item):
    if item in list:
        list.remove(item)
    list.append(item)

class Window:
    def __init__(self, width, height, x, y, draggable=True, resizable=True, closable=True, ui_tint=(100,100,100)):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.screen = pygame.Surface((self.width, self.height))
        self.sprites = []
        self.closing = False
        self.closable = closable
        self.selected = False
        self.dragging = False
        self.resizing = False
        self.draggable = draggable
        self.resizable = resizable
        self.drag_offset = (0, 0)
        self.animation_frame = 0
        self.ui_tint = ui_tint

    def get_screen(self):
        return self.screen

    def is_in_screen(self, position):
        local_x, local_y = self.get_position_local(position)
        if local_x < 0 or local_y < 0 or local_x >= self.width or local_y >= self.height:
            return False
        return True

    def is_in_topbar(self, position):
        if not self.is_in_screen(position):
            return False
        local_x, local_y = self.get_position_local(position)
        if local_y < 0 or local_y >= 30:  # Assuming top bar height is 30 pixels
            return False
        return True

    def is_in_close_button(self, position):
        if not self.is_in_screen(position):
            return False
        if not self.is_in_topbar(position):
            return False
        local_x, local_y = self.get_position_local(position)
        if local_x < self.width - 30 or local_x >= self.width:  # Assuming close button is 30x30 pixels at top-right
            return False
        return True

    def is_in_resize_button(self, position):
        if not self.is_in_screen(position):
            return False
        local_x, local_y = self.get_position_local(position)
        if local_x < self.width - 30 or local_x >= self.width:  # Assuming resize button is 30x30 pixels at bottom-right
            return False
        if local_y < self.height - 30 or local_y >= self.height:
            return False
        return True

    def get_position_local(self, position):
        local_x = position[0] - self.x
        local_y = position[1] - self.y
        return (local_x, local_y)

    def draw_loop(self, target_surface):
        ui = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        for width in range(1+(self.width//500)):
            ui.blit(window_topbar, (width*500, 0))
            ui.blit(window_bottombar, (width*500, self.height - window_bottombar.get_height()))
        for height in range(1+(self.height//500)):
            ui.blit(window_leftbar, (0, height*500))
            ui.blit(window_rightbar, (self.width - window_rightbar.get_width(), height*500))
        if self.closable:
            ui.blit(window_close_button, (self.width - window_close_button.get_width(), 0))
        if self.resizable:
            ui.blit(window_resize, (self.width - window_resize.get_width(), self.height - window_resize.get_height()))
        ui.fill(self.ui_tint, special_flags=pygame.BLEND_RGB_MULT)
        selection = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        selection.fill((255, 255, 200, 50))  # Semi-transparent overlay for selection effect

        if self.animation_frame > 100:
            self.animation_frame = 0
        self.animation_frame += .5
        for x in range(2+(self.width)//50):
            for y in range(2+(self.height)//50):
                self.screen.blit(screen_background, ((x-2)*50+self.animation_frame, (y-2)*50+1/2*self.animation_frame))
        for sprite in self.sprites:
            sprite.draw(self.screen)

        self.screen.blit(ui, (0, 0))
        if self.selected:
            self.screen.blit(selection, (0, 0))
        target_surface.blit(self.screen, (0, 0))

    def update_loop(self):
        if self.dragging:
            print("Dragging window with offset:", self.drag_offset)
            mouse_pos = pygame.mouse.get_pos()
            mouse_x, mouse_y = point_to_logical(mouse_pos)
            self.x = mouse_x - self.drag_offset[0]
            self.y = mouse_y - self.drag_offset[1]
        if self.resizing:
            mouse_pos = pygame.mouse.get_pos()
            mouse_x, mouse_y = point_to_logical(mouse_pos)
            self.width = round(max(60, mouse_x - self.x+3))
            self.height = round(max(60, mouse_y - self.y+3))
            self.screen = pygame.Surface((self.width, self.height))
        if self.x < 0 or self.x + self.width > target_width:
            self.x = max(0, min(self.x, target_width - self.width))
        if self.y < 0 or self.y + self.height > target_height:
            self.y = max(0, min(self.y, target_height - self.height))

    def event_loop(self, event):
        global selected_window, mouse_clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = point_to_logical(event.pos)
            if self.is_in_screen(pos):
                if self.closable and self.is_in_close_button(pos):
                    self.closing = True
                elif self.draggable and self.is_in_topbar(pos):
                    if self.dragging:
                        self.dragging = False
                    else:
                        self.dragging = True
                        self.drag_offset = (pos[0] - self.x, pos[1] - self.y)
                if self.resizable and self.is_in_resize_button(pos):
                    if self.resizing:
                        self.resizing = False
                    else:
                        self.resizing = True
                self.selected = True
                selected_window = self
                put_item_on_top(windows, self)
            else:
                self.selected = False
                if selected_window == self:
                    selected_window = None

windows:list[Window] = []
selected_window: Window | None = None

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def subtract(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def multiply(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def normalise(self):
        magnitude = self.magnitude()
        if magnitude == 0:
            return Vector(0, 0)
        return Vector(self.x / magnitude, self.y / magnitude)

    def magnitude(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def to_tuple(self):
        return (self.x, self.y)


class Sprite:
    def __init__(self, image, x, y, hitboxes:list[pygame.Rect]=[], scale=1, rotation=0, pivot:tuple[int,int]=(0,0)):
        self.image = image
        self.x = x
        self.y = y
        self.scale = scale
        self.rotation = rotation
        self.hitboxes = hitboxes
        self.pivot = (self.x + pivot[0], self.y + pivot[1])

    def draw(self, target_surface):
        rotated_image = pygame.transform.rotozoom(self.image, self.rotation, self.scale)
        pivot_offset = pygame.math.Vector2(self.pivot[0] - self.x, self.pivot[1] - self.y)
        rotated_offset = pivot_offset.rotate(-self.rotation)
        rect = rotated_image.get_rect(center=(self.pivot[0] + rotated_offset[0], self.pivot[1] + rotated_offset[1]))
        target_surface.blit(rotated_image, rect.topleft)

    def rotate(self, angle):
        rotated_hitboxes = []
        self.rotation += angle
        for hitbox in self.hitboxes:
            pivot_offset = pygame.math.Vector2(self.pivot[0] - self.x, self.pivot[1] - self.y)
            rotated_offset = pivot_offset.rotate(-(self.rotation))
            rect = hitbox.copy()
            rect.center = (self.pivot[0] + rotated_offset[0], self.pivot[1] + rotated_offset[1])
            rotated_hitboxes.append(rect)
        self.hitboxes = rotated_hitboxes

    def scale(self, factor):
        self.scale *= factor
        scaled_hitboxes = []
        for hitbox in self.hitboxes:
            rect = hitbox.copy()
            rect.width = int(rect.width * factor)
            rect.height = int(rect.height * factor)
            rect.center = (self.pivot[0] + (rect.centerx - self.pivot[0]) * factor,
                           self.pivot[1] + (rect.centery - self.pivot[1]) * factor)
            scaled_hitboxes.append(rect)
        self.hitboxes = scaled_hitboxes
        self.pivot = (self.x + (self.pivot[0] - self.x) * factor, self.y + (self.pivot[1] - self.y) * factor)

    def collide_point(self, point):
        for hitbox in self.hitboxes:
            if hitbox.collidepoint(point):
                return True
        return False

def update_screen_loop():
    for window in windows:
        window.update_loop()
        if window.closing:
            windows.remove(window)

def event_screen_loop(event):
    global mouse_clicked
    mouse_clicked = False
    for window in windows:
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_clicked == False:
            window.event_loop(event)
            mouse_clicked = True
        else:
            window.event_loop(event)

def draw_screen_loop(target_surface, width_scale, height_scale):
    target_surface.fill((50, 50, 50))
    for window in windows:
        window_surface = pygame.Surface((window.width, window.height))
        window.draw_loop(window_surface)
        scaled_surface = pygame.transform.scale(
            window_surface,
            (int(window.width * width_scale), int(window.height * height_scale))
        )
        target_surface.blit(
            scaled_surface,
            (int(window.x * width_scale), int(window.y * height_scale))
        )

if __name__ == "__main__":
    running = True
    clock = pygame.time.Clock()
    windows.append(Window(500, 500, 500, 500, ui_tint=(150,150,150)))
    windows.append(Window(100, 100, 100, 100, ui_tint=(200,100,100)))
    windows.append(Window(200, 200, 150, 150, ui_tint=(100,200,100)))
    windows.append(Window(300, 300, 200, 200, ui_tint=(100,100,200)))
    while running:
        update_screen_loop()
        draw_screen_loop(screen, width_ratio, height_ratio)
        pygame.display.flip()
        mouse_clicked = False
        for event in pygame.event.get():
            event_screen_loop(event)
            if event.type == pygame.QUIT:
                running = False
        clock.tick(60)
    pygame.quit()