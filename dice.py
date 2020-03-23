import random
import os
from PIL import Image


def roll_the_dice():
    set_matrix = [
        (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
        (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2),
        (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3),
        (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4),
        (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5),
        (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6)
    ]

    def roll():
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

    def get_nick(roll):
        nicks = {
            0: 'Snake eyes',
            1: 'Australian yo',
            2: 'Little Joe From Kokomo',
            3: 'No field five',
            4: 'Easy six',
            5: 'Six one you\'re done',
            6: 'Ace caught a deuce',
            7: 'Ballerina',
            8: 'The Fever',
            9: 'Jimmie Hicks',
            10: 'Benny Blue',
            11: 'Easy eight',
            12: 'Easy four',
            13: 'Michael Jordan',
            14: 'Brooklyn Forest',
            15: 'Big Red',
            16: 'Eighter from Decatur',
            17: 'Nina from Pasadena',
            18: 'Little Phoebe',
            19: 'Little number',
            20: 'Skinny McKinney',
            21: 'Square pair',
            22: 'Railroad nine',
            23: 'Big one on the end',
            24: 'Sixie from Dixie',
            25: 'Skinny Dugan',
            26: 'Easy eight',
            27: 'Jesse James',
            28: 'Puppy paws',
            29: 'Yo AKA lucky cuck',
            30: 'The Devil',
            31: 'Easy eight',
            32: 'Lou Brown',
            33: 'Tennessee',
            34: 'Six five no jive',
            35: 'MIDNIGHT SPACE BEARS'
        }

        for i in range(len(set_matrix)):
            if set_matrix[i][0] == roll[0] and set_matrix[i][1] == roll[1]:
                return nicks.get(i)

        return nicks.get(set_matrix.index(roll))

    def save_result():
        result = roll()

        die_1 = get_die_face(result[0])
        die_2 = get_die_face(result[1])

        nick = 'You rolled a ' + get_nick(result)

        images = [Image.open(x) for x in [die_1, die_2]]
        widths, heights = zip(*(i.size for i in images))

        total_width = sum(widths) + 10
        max_height = max(heights)

        result = Image.new('RGBA', (total_width, max_height))
        x_offset = 0

        for im in images:
            result.paste(im, (x_offset, 0))
            x_offset += im.size[0] + 10

        result_path = os.getcwd() + '/assets/dice/result.png'
        result.save(result_path)

        return result_path, nick

    return save_result()
