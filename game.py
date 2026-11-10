import asyncio
import curses
import random
import time

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def read_controls(canvas):
    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


async def blink(canvas, row, column, symbol="*", start_delay=0):
    await sleep(start_delay)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), "*")
    await sleep(1)

    canvas.addstr(round(row), round(column), "O")
    await sleep(1)
    canvas.addstr(round(row), round(column), " ")

    row += rows_speed
    column += columns_speed

    symbol = "-" if columns_speed else "|"

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 1 < round(row) < max_row - 1 and 1 < round(column) < max_column - 1:
        canvas.addstr(round(row), round(column), symbol)
        await sleep(1)
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed


async def sleep(ticks=1):
    for _ in range(ticks):
        await asyncio.sleep(0)


async def animate_spaceship(canvas, start_row, start_column, frames):
    row, column = start_row, start_column
    frame_1, frame_2 = frames

    ship_rows, ship_columns = get_frame_size(frame_1)

    while True:
        for frame in (frame_1, frame_1, frame_2, frame_2):
            max_y, max_x = canvas.getmaxyx()

            rows_direction, columns_direction, _ = read_controls(canvas)

            row += rows_direction
            column += columns_direction

            row = max(1, min(row, max_y - 1 - ship_rows))
            column = max(1, min(column, max_x - 1 - ship_columns))

            draw_frame(canvas, row, column, frame)

            await sleep(1)

            draw_frame(canvas, row, column, frame, negative=True)


def draw_frame(canvas, start_row, start_column, text, negative=False):
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == " ":
                continue

            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else " "
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def draw(canvas, rocket_frames):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    coroutines = asyncio.run(main(canvas, rocket_frames))

    while True:
        active_coroutines = []

        for coroutine in coroutines:
            try:
                coroutine.send(None)
                active_coroutines.append(coroutine)
            except StopIteration:
                pass

        coroutines = active_coroutines

        canvas.refresh()
        time.sleep(0.1)


async def main(canvas, rocket_frames):
    coroutines = []

    max_y, max_x = canvas.getmaxyx()
    used_coordinates = set()

    for _ in range(150):
        while True:
            row = random.randint(1, max_y - 2)
            column = random.randint(1, max_x - 2)

            if (row, column) not in used_coordinates:
                used_coordinates.add((row, column))
                break

        delay = random.randint(0, 20)

        coroutines.append(blink(canvas, row, column, random.choice("+*.:"), delay))

    ship_row = max_y // 2
    ship_column = max_x // 2
    _, ship_columns = get_frame_size(rocket_frames[0])
    fire_row = ship_row
    fire_column = ship_column + (ship_columns // 2)

    coroutines.append(fire(canvas, fire_row, fire_column))
    coroutines.append(animate_spaceship(canvas, ship_row, ship_column, rocket_frames))

    return coroutines


if __name__ == "__main__":
    with open("frames/rocket_frame_1.txt", "r", encoding="utf-8") as f:
        frame_1 = f.read()
    with open("frames/rocket_frame_2.txt", "r", encoding="utf-8") as f:
        frame_2 = f.read()
    rocket_frames = [frame_1, frame_2]
    curses.update_lines_cols()
    curses.wrapper(draw, rocket_frames)
