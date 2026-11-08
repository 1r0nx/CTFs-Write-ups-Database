# Haybales — Pwny-CTF (script de solve)
from badgeio import badge
import time
CHAR_HEIGHT_PX = 8
CHAR_WIDTH_PX = 5


class MenuItem:
    def __init__(self, label, action):
        self.label = label
        self.action = action

class ScreenController:
    def __init__(self):
        self.screen_stack = []
        self.draw_disabled = False
        self.last_tick = 0

    def push_screen(self, screen):
        """
            Add a screen to the screen stack.
            The top screen will be drawn and receive button presses.
        """
        self.screen_stack.append(screen)
        screen.on_enter()

    def pop_screen(self):
        if len(self.screen_stack) > 1:
            self.screen_stack[-1].on_leave()
            self.screen_stack.pop()
            self.draw_disabled = False
    
    def pop_to_bottom(self):
        while len(self.screen_stack) > 1:
            self.pop_screen()

    def disable_draw(self):
        self.draw_disabled = True
    
    
    def loop(self):
        while True:
            t = time.ticks_ms()
            # Update button states
            badge.tick()

            if not self.draw_disabled:
                # Wipe screen
                badge.display.fill(0)

                # Draw the current menu / screen + do all login

                self.screen_stack[-1].draw()

                # Update the screen
                badge.display.show()

            # Delegate button presses to the current menu / screen
            if badge.B.pressed:
                self.screen_stack[-1].b()

            if badge.A.pressed:
                self.screen_stack[-1].a()

            if badge.down.pressed:
                self.screen_stack[-1].down()

            if badge.up.pressed:
                self.screen_stack[-1].up()

            if badge.left.pressed:
                self.screen_stack[-1].left()

            if badge.right.pressed:
                self.screen_stack[-1].right()
            self.last_tick = time.ticks_diff(time.ticks_ms(), t)

class Screen:
    def draw(self):
        badge.display.fill(0)
        # badge.display.text("All your codebase are belong to us", 0, 0)

    def up(self):
        pass

    def down(self):
        pass

    def left(self):
        pass

    def right(self):
        pass

    def a(self):
        pass

    def b(self):
        global screen_controller
        """
        This default implementation of b() will return to the previous screen
        """
        screen_controller.pop_screen()
    
    def on_enter(self):
        """
        Called whenever a menu is initially popped onto the screen
        """
        pass
    def on_leave(self):
        """
        Called whenever a menu leaves the screen
        """
        pass

"""
A menu that displays a list of items, one per row
"""
class RowMenu(Screen):
    def __init__(self, items=[]):
        self.items = items
        self.selected_idx = 0
        self.rows = 8

    def draw(self):
        output_i = 0
        item_i = max(0, self.selected_idx - 3)

        badge.display.fill(0)

        for i in range(item_i, min(self.rows + item_i, len(self.items))):
            if i == self.selected_idx:
                badge.display.text(f"> {self.items[i].label}", 0, output_i*CHAR_HEIGHT_PX, 1)
            else:
                badge.display.text(f"  {self.items[i].label}", 0, output_i*CHAR_HEIGHT_PX, 1)
            output_i += 1

    def up(self):
        self.selected_idx = (self.selected_idx - 1) % len(self.items)
        self.draw()

    def down(self):
        self.selected_idx = (self.selected_idx + 1) % len(self.items)
        self.draw()

    def a(self):
        """
        Will be called by the menu controller when the A button is pressed
        """
        if self.selected_idx >= len(self.items):
            print("Out of bounds")
            return

        self.items[self.selected_idx].action()

class TableMenu(Screen):
    def __init__(self, items):
        self.items = items
        # (x, y)
        self.selected_idx = (0, 0)
        self.rows = 4
        self.columns = 4

    def draw(self):
        output_i = 0
        item_i = max(0, self.selected_idx - 3)

        badge.display.fill(0)

        for i in range(item_i, min(self.rows + item_i, len(self.items))):
            if i == self.selected_idx:
                badge.display.text(f"> {self.items[i].label}", 0, output_i*CHAR_HEIGHT_PX, 1)
            else:
                badge.display.text(f"  {self.items[i].label}", 0, output_i*CHAR_HEIGHT_PX, 1)

    def up(self):
        self.selected_idx = (self.selected_idx[0], max(0, self.selected_idx - 1))

    def down(self):
        self.selected_idx = (self.selected_idx[0], min(len(self.items) - 1, self.selected_idx + 1))

    def right(self):
        self.selected_idx = (max(0, self.selected_idx - 1), self.selected_idx[1])

    def left(self):
        self.selected_idx = (min(len(self.items) - 1, self.selected_idx + 1), self.selected_idx[1])

    def a(self):
        """
        Will be called by the menu controller when the A button is pressed
        """
        x, y = self.selected_idx

        self.items[x][y].action()

screen_controller = ScreenController()
