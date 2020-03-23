import random
import os
import numpy as np
from PIL import Image


def roll_the_dice():
    def roll():
        set_matrix = np.array([
            (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
            (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2),
            (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3),
            (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4),
            (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5),
            (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6)
        ])
        return random.choice(set_matrix)

    def get_die_face(i):
        img_dir = os.getcwd() + '/assets/dice/'
        faces = {
            1: img_dir + '1.png',
            2: img_dir + '2.png',
            3: img_dir + '3.png',
            4: img_dir + '4.png',
            5: img_dir + '5.png',
            6: img_dir + '6.png'
        }
        return faces.get(i)

    def save_result():
        die_1 = get_die_face(roll()[0])
        die_2 = get_die_face(roll()[1])

        images = [Image.open(x) for x in [die_1, die_2]]
        widths, heights = zip(*(i.size for i in images))

        total_width = sum(widths) + 10
        max_height = max(heights)

        result = Image.new('RGBA', (total_width, max_height))
        x_offset = 0

        for im in images:
            result.paste(im, (x_offset, 0))
            x_offset += im.size[0]

        result_path = os.getcwd() + '/assets/dice/result.png'
        result.save(result_path)

        return result_path

    return save_result()
