import random


def roll():
    o = 'o'
    base = '╔═══════╗\n'
    row1 = '║       ║\n'
    row2 = '║       ║\n'
    row3 = '║       ║\n'
    bott = '╚═══════╝'

    row_1_chars = list(row1)
    row_2_chars = list(row2)
    row_3_chars = list(row3)

    rolled_number = random.randint(1, 6)

    if rolled_number == 1:
        row_2_chars[4] = o
        row2 = ''.join(row_2_chars)

    elif rolled_number == 2:
        row_1_chars[2] = o
        row_3_chars[6] = o

        row1 = ''.join(row_1_chars)
        row3 = ''.join(row_3_chars)

    elif rolled_number == 3:
        row_1_chars[2] = o
        row_2_chars[4] = o
        row_3_chars[6] = o

        row1 = ''.join(row_1_chars)
        row2 = ''.join(row_2_chars)
        row3 = ''.join(row_3_chars)

    elif rolled_number == 4:
        row_1_chars[2] = o
        row_1_chars[6] = o
        row_3_chars[2] = o
        row_3_chars[6] = o

        row1 = ''.join(row_1_chars)
        row3 = ''.join(row_3_chars)

    elif rolled_number == 5:
        row_1_chars[2] = o
        row_1_chars[6] = o
        row_2_chars[4] = o
        row_3_chars[2] = o
        row_3_chars[6] = o

        row1 = ''.join(row_1_chars)
        row2 = ''.join(row_2_chars)
        row3 = ''.join(row_3_chars)

    else:
        row_1_chars[2] = o
        row_1_chars[6] = o
        row_2_chars[2] = o
        row_2_chars[6] = o
        row_3_chars[2] = o
        row_3_chars[6] = o
        row1 = ''.join(row_1_chars)
        row2 = ''.join(row_2_chars)
        row3 = ''.join(row_3_chars)

    return base+row1+row2+row3+bott
