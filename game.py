import asyncio
import curses
import random
import time

from curses_tools import draw_frame, get_frame_size, read_controls
from space_garbage import fly_garbage


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


def draw(canvas, rocket_frames, garbage_frames):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    coroutines = asyncio.run(main(canvas, rocket_frames, garbage_frames))

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


async def main(canvas, rocket_frames, garbage_frames):
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
    coroutines.append(
        fly_garbage(canvas, column=10, garbage_frame=random.choice(garbage_frames))
    )

    return coroutines


if __name__ == "__main__":
    garbage_frames_list = (
        "duck.txt",
        "hubble.txt",
        "lamp.txt",
        "trash_large.txt",
        "trash_small.txt",
        "trash_xl.txt",
    )
    garbage_frames = []
    for file in garbage_frames_list:
        with open(f"frames/{file}", "r", encoding="utf-8") as f:
            frame = f.read()
            garbage_frames.append(frame)
    with open("frames/rocket_frame_1.txt", "r", encoding="utf-8") as f:
        frame_1 = f.read()
    with open("frames/rocket_frame_2.txt", "r", encoding="utf-8") as f:
        frame_2 = f.read()
    rocket_frames = [frame_1, frame_2]
    curses.update_lines_cols()
    curses.wrapper(draw, rocket_frames, garbage_frames)
