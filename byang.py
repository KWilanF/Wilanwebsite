import pygame as pg
import numpy as np

class Matrix:
    def __init__(self, app, font_size=12, image_path="vi.png"):
        self.app = app
        self.FONT_SIZE = font_size
        self.SIZE = self.ROWS, self.COLS = app.HEIGHT // font_size, app.WIDTH // font_size
        self.katakana = np.array([chr(int('0x30a0', 16) + i) for i in range(96)] + ['' for i in range(10)])
        self.font = pg.font.SysFont('Arial', font_size, bold=True)

        self.matrix = np.random.choice(self.katakana, self.SIZE)
        self.char_intervals = np.random.randint(25, 50, size=self.SIZE)  # Controls frequency of character change
        self.cols_speed = np.random.randint(1, 500, size=self.SIZE)  # Controls speed of column shift
        self.prerendered_chars = self.get_prerendered_chars()

        # Load the image of the face and convert to binary (1 or 0) based on pixel color
        self.image = self.get_image(image_path)
        self.face_pattern = self.convert_image_to_binary(self.image)

    def get_image(self, path_to_file):
        # Resizing the image to fit smaller mobile screens (adjust the size accordingly)
        image = pg.image.load(path_to_file)
        image = pg.transform.scale(image, (self.COLS, self.ROWS))  # Resize image to matrix size
        return image

    def convert_image_to_binary(self, image):
        # Convert the image to grayscale and then binary (1 for light, 0 for dark)
        width, height = image.get_size()
        binary_pattern = np.zeros((height, width), dtype=int)
        for y in range(height):
            for x in range(width):
                pixel = image.get_at((x, y))  # Get RGBA value
                # Check if pixel is light (part of the face)
                # If the pixel is light, mark it as 1 (visible), else 0 (not visible)
                if pixel[0] > 128 and pixel[1] > 128 and pixel[2] > 128:  # Light pixels (white)
                    binary_pattern[y, x] = 1
        return binary_pattern

    def get_prerendered_chars(self):
        char_colors = [(0, green, 0) for green in range(256)]  # Green color for matrix rain
        prerendered_chars = {}
        for char in self.katakana:
            for color in char_colors:
                prerendered_chars[(char, color)] = self.font.render(char, True, color)
        return prerendered_chars

    def run(self):
        frames = pg.time.get_ticks()
        self.change_chars(frames)
        self.shift_column(frames)
        self.draw()

    def shift_column(self, frames):
        num_cols = np.argwhere(frames % self.cols_speed == 0)  # Find columns to shift
        num_cols = num_cols[:, 1]
        num_cols = np.unique(num_cols)
        self.matrix[:, num_cols] = np.roll(self.matrix[:, num_cols], shift=1, axis=0)

    def change_chars(self, frames):
        mask = np.argwhere(frames % self.char_intervals == 0)  # Randomly change characters
        new_chars = np.random.choice(self.katakana, mask.shape[0])
        self.matrix[mask[:, 0], mask[:, 1]] = new_chars

    def draw(self):
        for y, row in enumerate(self.matrix):
            for x, char in enumerate(row):
                if char and self.face_pattern[y, x] == 1:  # Only draw where there is part of the face
                    pos = x * self.FONT_SIZE, y * self.FONT_SIZE
                    color = (0, 255, 0)  # Green for Matrix effect
                    char_surface = self.prerendered_chars[(char, color)]
                    self.app.surface.blit(char_surface, pos)


class MatrixVision:
    def __init__(self):
        # Adjust screen resolution for mobile devices (lower resolution for better performance)
        self.RES = self.WIDTH, self.HEIGHT = 800, 480  # Smaller resolution for mobile
        pg.init()
        self.screen = pg.display.set_mode(self.RES)
        self.surface = pg.Surface(self.RES)
        self.clock = pg.time.Clock()
        self.matrix = Matrix(self)

    def draw(self):
        self.surface.fill(pg.Color('black'))  # Clear screen with black
        self.matrix.run()
        self.screen.blit(self.surface, (0, 0))  # Update screen

    def run(self):
        while True:
            self.draw()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
            pg.display.flip()
            self.clock.tick(30)  # Frame rate limit (adjust as needed)


if __name__ == '__main__':
    app = MatrixVision()
    app.run()
