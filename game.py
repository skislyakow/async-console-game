import asyncio
import curses


async def blink(canvas, row, column, symbol="*"):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.border()

    asyncio.run(main(canvas))


async def main(canvas):
    asyncio.create_task(blink(canvas, 2, 2, "* * * * *"))

    phase_durations = [2.0, 0.3, 0.5, 0.3]
    curent_phase = 0

    while True:
        canvas.refresh()
        await asyncio.sleep(phase_durations[curent_phase])
        await asyncio.sleep(0)
        curent_phase = (curent_phase + 1) % len(phase_durations)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.wrapper(draw)
