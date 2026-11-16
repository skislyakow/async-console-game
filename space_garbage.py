import asyncio

from curses_tools import draw_frame, get_frame_size
from explosion import explode
from obstacles import Obstacle


async def fly_garbage(
    canvas, column, garbage_frame, obstacles, obstacles_in_last_collisions, speed=0.5
):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0
    row_size, column_size = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, row_size, column_size)
    obstacles.append(obstacle)

    try:
        while row < rows_number:
            if obstacle in obstacles_in_last_collisions:
                obstacles_in_last_collisions.remove(obstacle)
                center_row = row + row_size / 2
                center_column = column + column_size / 2
                await explode(canvas, center_row, center_column)
                return

            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            obstacle.row = row
    finally:
        obstacles.remove(obstacle)
