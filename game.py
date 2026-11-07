import asyncio
import curses
import random
import time


async def blink(canvas, row, column, symbol="*"):
    await sleep(random.randint(0, 20))

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
    """Display animation of gun shot, direction and speed can be specified."""

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

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await sleep(1)
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed


async def sleep(ticks=1):
    for _ in range(ticks):
        await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.border()

    # asyncio.run(main(canvas))

    coroutines = asyncio.run(main(canvas))

    while True:
        actice_coroutines = []

        for coroutine in coroutines:
            try:
                coroutine.send(None)
                actice_coroutines.append(coroutine)
            except StopIteration:
                pass

        coroutines = actice_coroutines

        canvas.refresh()
        time.sleep(0.1)


async def main(canvas):
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

        coroutines.append(blink(canvas, row, column, random.choice("+*.:")))

        # asyncio.create_task(blink(canvas, row, column, random.choice("+*.:")))

    start_row = max_y // 2
    start_column = max_x // 2
    coroutines.append(fire(canvas, start_row, start_column))

    return coroutines

    while True:
        canvas.refresh()
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.wrapper(draw)
