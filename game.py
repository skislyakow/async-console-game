import asyncio
import curses
import random


async def blink(canvas, row, column, symbol="*"):
    for _ in range(random.randint(0, 2)):
        await asyncio.sleep(random.uniform(0, 2.0))

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(2.0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0.5)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0.3)


def draw(canvas):
    curses.curs_set(False)
    canvas.border()

    asyncio.run(main(canvas))


async def main(canvas):
    max_y, max_x = canvas.getmaxyx()
    used_coordinates = set()

    for _ in range(150):
        while True:
            row = random.randint(1, max_y - 2)
            column = random.randint(1, max_x - 2)

            if (row, column) not in used_coordinates:
                used_coordinates.add((row, column))
                break

        asyncio.create_task(blink(canvas, row, column, random.choice("+*.:")))

    while True:
        canvas.refresh()
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.wrapper(draw)
