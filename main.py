import pygame as pg
import math
from queue import PriorityQueue

WIDTH = 800
ROWS = 50

WIN = pg.display.set_mode((WIDTH, WIDTH))
pg.display.set_caption("A * Path Finding Algorithm")


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (220, 220, 220)
TURQUOISE = (0, 206, 209)


class Spot :
    def __init__(self, row, col, width, total_rows) :
        self.row = row
        self.col = col
        # cube coordinates
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.width = width
        self.total_rows = total_rows

    def get_pos(self) :
        return self.row, self.row

    # true if Spot in closed state
    def is_closed(self) :
        return self.color == RED

    def is_open(self) :
        return self.color == GREEN

    def is_barrier(self) :
        return self.color == BLACK

    def is_start(self) :
        return self.color == ORANGE

    def is_end(self) :
        return self.color == TURQUOISE

    def reset(self) :
        self.color = WHITE

    def make_closed(self) :
        self.color = RED

    def make_open(self) :
        self.color = GREEN

    def make_barrier(self) :
        self.color = BLACK

    def make_start(self) :
        self.color = ORANGE

    def make_end(self) :
        self.color = TURQUOISE

    def make_path(self) :
        self.color = PURPLE

    def draw(self, win) :
        pg.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid) :
        self.neighbors = []
        # check if is not the last row and then check if the LOWWER neighbour is not barrier
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier() :
            self.neighbors.append(grid[self.row + 1][self.col])
        # check if is not the first row and then check if the UPPER neighbour is not barrier
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier() :
            self.neighbors.append(grid[self.row - 1][self.col])
        # check if is not the last right row and then check if the RIGHT neighbour is not barrier
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier() :
            self.neighbors.append(grid[self.row][self.col + 1])
        # check if is not the first left row and then check if the LEFT neighbour is not barrier
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier() :
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other) :
        return False


# Heuristic function we will use for pathfinder

# Manhattan distance between 2 points
def h(p1, p2) :
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def algorithm(draw, grid, start, end) :
    count = 0
    open_set = PriorityQueue()
    # add the start node to open_set
    open_set.put((0, count, start))
    came_from = {}
    # adding the g_score for spots, default set to infinity
    g_score = {spot : float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot : float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty() :
        for event in pg.event.get() :
            if event.type == pg.QUIT :
                pg.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end :
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors :
            # adding one to g score, neighbor 1 spot away.
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


def reconstruct_path(came_from, current, draw) :
    while current in came_from :
        current = came_from[current]
        current.make_path()
        draw()


# Setting up board
def make_grid(rows, width) :
    grid = []
    gap = width // rows
    for i in range(rows) :
        grid.append([])
        for j in range(rows) :
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid


def draw_grid(win, rows, width) :
    gap = width // rows
    for i in range(rows) :
        # horizontal lines
        pg.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        # vertical lines
        pg.draw.line(win, GREY, (i * gap, 0), (i * gap, width))


def draw(wing, grid, rows, width) :
    WIN.fill(WHITE)
    # draw all of the spots
    for row in grid :
        for spot in row :
            spot.draw(WIN)

    draw_grid(WIN, rows, width)
    pg.display.update()


# mouse support
def get_clicked_pos(pos, rows, width) :
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap
    return row, col


# main loop
def main(win, width) :
    grid = make_grid(ROWS, WIDTH)
    start = None
    end = None

    run = True
    finished = False
    while run :
        draw(win, grid, ROWS, width)
        for event in pg.event.get() :
            if event.type == pg.QUIT :
                run = False

            # LMB event - draw the Spot
            if pg.mouse.get_pressed()[0] :
                pos = pg.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end :
                    start = spot
                    start.make_start()
                elif not end and spot != start :
                    end = spot
                    end.make_end()

                elif spot != end and spot != start :
                    spot.make_barrier()
            # RMB event - reset the Spot
            elif pg.mouse.get_pressed()[2] :
                pos = pg.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start :
                    start = None
                elif spot == end :
                    end = None

            if event.type == pg.KEYDOWN :
                if event.key == pg.K_SPACE and start and end and not finished:
                    for row in grid :
                        for spot in row :
                            spot.update_neighbors(grid)

                    algorithm(lambda : draw(win, grid, ROWS, width), grid, start, end)
                    finished = True

                if event.key == pg.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
                    finished = False

    pg.quit()


main(WIN, WIDTH)
