from PIL import Image
from plate_const import *
import cv2
import numpy as np
import os
import shutil
import random
import argparse

PLATE_STYLE_BLUE = 0
PLATE_STYLE_YELLOW = 1
PLATE_STYLE_NEW_ENERGY = 2
PLATE_STYLE_POLICE = 3
PLATE_STYLE_EMBASSY = 4
PLATE_STYLE_HK = 5
PLATE_STYLE_MC = 6
PLATE_STYLE_COACH = 7

PLATE_TYPE_NORMAL = 0
PLATE_TYPE_POLICE = 1
PLATE_TYPE_EMBASSY = 2
PLATE_TYPE_HK = 3
PLATE_TYPE_MC = 4
PLATE_TYPE_COACH = 5

def generate_random_plate_string(type):
    plate_string = ''
    area_count = 31
    city_count = 26

    if type == PLATE_TYPE_NORMAL:
        style_index = random.randint(0, len(plate_style_5) - 1)
        style = plate_style_5[style_index]
        area_index = random.randint(0, area_count - 1)
        area = zh_array[area_index]
        plate_string += area
        city_index = random.randint(0, city_count - 1)
        city = en_array[city_index]

        while city in area_black_list[area]:
            city_index = random.randint(0, city_count - 1)
            city = en_array[city_index]
        plate_string += city

        i = 0
        while i < len(style):
            if style[i] == '0':  # number
                number = random.randint(0, 9)
                plate_string += str(number)
                i += 1
            else:  # en
                item_index = random.randint(0, city_count - 1)
                en_word = en_array[item_index]
                if not(en_word == 'I' or en_word == 'O'):
                    plate_string += en_word
                    i += 1
    elif type == PLATE_TYPE_POLICE:
        area_index = random.randint(0, area_count - 1)
        area = zh_array[area_index]
        plate_string += area

        if area in area_police:
            polices = area_police[area]
            city_index = random.randint(0, len(polices) - 1)
            city = polices[city_index]
        else:
            city_index = random.randint(0, city_count - 1)
            city = en_array[city_index]
            while city in area_black_list[area]:
                city_index = random.randint(0, city_count - 1)
                city = en_array[city_index]
        plate_string += city

        category = random.randint(0, len(police_codes))
        left_count = 3
        if category == len(police_codes):
            left_count += 1
        else:
            plate_string += police_codes[category]
        i = 0
        while i < left_count:
            number = random.randint(0, 9)
            plate_string += str(number)
            i += 1
        plate_string += '警'
    elif type == PLATE_TYPE_EMBASSY:

        plate_string += '使'
        part_index = random.randint(0, len(embassy_range) - 1)
        start, end = embassy_range[part_index]
        code = random.randint(start, end)
        plate_string += str(code)

        i = 0
        while i < 3:
            number = random.randint(0, 9)
            plate_string += str(number)
            i += 1
    elif type == PLATE_TYPE_HK or type == PLATE_TYPE_MC:
        style_index = random.randint(0, len(plate_style_4) - 1)
        style = plate_style_4[style_index]
        plate_string += '粤Z'
        i = 0
        while i < len(style):
            if style[i] == '0':  # number
                number = random.randint(0, 9)
                plate_string += str(number)
                i += 1
            else:  # en
                item_index = random.randint(0, city_count - 1)
                en_word = en_array[item_index]
                if not(en_word == 'I' or en_word == 'O'):
                    plate_string += en_word
                    i += 1
        plate_string += '港' if type == PLATE_TYPE_HK else '澳'
    elif type == PLATE_TYPE_COACH:
        style_index = random.randint(0, len(plate_style_4) - 1)
        style = plate_style_4[style_index]
        area_index = random.randint(0, area_count - 1)
        area = zh_array[area_index]
        plate_string += area
        city_index = random.randint(0, city_count - 1)
        city = en_array[city_index]

        while city in area_black_list[area]:
            city_index = random.randint(0, city_count - 1)
            city = en_array[city_index]
        plate_string += city

        i = 0
        while i < len(style):
            if style[i] == '0':  # number
                number = random.randint(0, 9)
                plate_string += str(number)
                i += 1
            else:  # en
                item_index = random.randint(0, city_count - 1)
                en_word = en_array[item_index]
                if not (en_word == 'I' or en_word == 'O'):
                    plate_string += en_word
                    i += 1
        plate_string += '学'
    return plate_string


def get_word_with_color(word_img, color):

    size = word_img.size
    mask_bg = Image.new('RGB', size, color)

    word_img = np.array(word_img)
    mask_bg = np.array(mask_bg)

    word_img = cv2.bitwise_not(word_img)
    word_img = cv2.bitwise_and(word_img, mask_bg)
    return Image.fromarray(word_img)


def generate_plate_image(style, plate_string, size=(1300, 414)):

    width, _ = size
    scale = width / 440

    # white mask
    text = Image.new('RGB', size, (0, 0, 0))
    mask = Image.new('RGB', size, (255, 255, 255))

    if style == PLATE_STYLE_BLUE or style == PLATE_STYLE_YELLOW:
        if style == PLATE_STYLE_BLUE:
            bg_path = './backgrounds/14.bmp'
            text_color = (255, 255, 255)
        else:
            bg_path = './backgrounds/6.bmp'
            text_color = (0, 0, 0)
        bg_image = Image.open(bg_path).resize(size, Image.ANTIALIAS)

        zh_index = zh_array.index(plate_string[0])
        zh_word_path = './words/zhs/zh_' + str(zh_index) + '.jpg'
        zh_word = Image.open(zh_word_path)
        zh_word = zh_word.resize((int(45 * scale), int(90 * scale)), Image.ANTIALIAS)
        mask.paste(zh_word, (int(15.5 * scale), int(25 * scale)))
        zh_word = get_word_with_color(zh_word, text_color)
        text.paste(zh_word, (int(15.5 * scale), int(25 * scale)))

        en_index = en_array.index(plate_string[1])
        en_word_path = './words/ens/en_' + str(en_index) + '.jpg'
        en_word = Image.open(en_word_path)
        en_word = en_word.resize((int(45 * scale), int(90 * scale)), Image.ANTIALIAS)
        mask.paste(en_word, (int(72.5 * scale), int(25 * scale)))
        en_word = get_word_with_color(en_word, text_color)
        text.paste(en_word, (int(72.5 * scale), int(25 * scale)))

        for i in range(5):
            string = plate_string[i + 2]
            if string.isdigit():
                num_index = int(string)
                num_word_path = './words/numbers/numbers_' + str(num_index) + '.jpg'
                word = Image.open(num_word_path)
            else:
                en_index = en_array.index(string)
                en_word_path = './words/ens/en_' + str(en_index) + '.jpg'
                word = Image.open(en_word_path)
            word = word.resize((int(45 * scale), int(90 * scale)), Image.ANTIALIAS)
            mask.paste(word, (int((151.5 + 57 * i) * scale), int(25 * scale)))
            word = get_word_with_color(word, text_color)
            text.paste(word, (int((151.5 + 57 * i) * scale), int(25 * scale)))

    elif style == PLATE_STYLE_POLICE:

        bg_path = './backgrounds/8.bmp'
        bg_image = Image.open(bg_path).resize(size, Image.ANTIALIAS)
        first_color = (0, 0, 0)
        text_color = (0, 0, 0)
        last_color = (255, 0, 0)
        last_word_path = './words/zhs/zh_36.jpg'

        zh_index = zh_array.index(plate_string[0])
        zh_word_path = './words/zhs/zh_' + str(zh_index) + '.jpg'
        zh_word = Image.open(zh_word_path)
        zh_word = zh_word.resize((int(45 * scale), int(90 * scale)), Image.ANTIALIAS)
        mask.paste(zh_word, (int(15.5 * scale), int(25 * scale)))
        zh_word = get_word_with_color(zh_word, first_color)
        text.paste(zh_word, (int(15.5 * scale), int(25 * scale)))

        for i in range(5):
            string = plate_string[i + 1]
            if string.isdigit():
                num_index = int(string)
                num_word_path = './words/numbers/numbers_' + str(num_index) + '.jpg'
                word = Image.open(num_word_path)
            else:
                en_index = en_array.index(string)
                en_word_path = './words/ens/en_' + str(en_index) + '.jpg'
                word = Image.open(en_word_path)
            word = word.resize((int(45 * scale), int(90 * scale)), Image.ANTIALIAS)
            mask.paste(word, (int((94.5 + 57 * i) * scale), int(25 * scale)))
            word = get_word_with_color(word, text_color)
            text.paste(word, (int((94.5 + 57 * i) * scale), int(25 * scale)))

        lsat_word = Image.open(last_word_path)
        lsat_word = lsat_word.resize((int(45 * scale), int(90 * scale)))
        mask.paste(lsat_word, (int((94.5 + 57 * 5) * scale), int(25 * scale)))
        lsat_word = get_word_with_color(lsat_word, last_color)
        text.paste(lsat_word, (int((94.5 + 57 * 5) * scale), int(25 * scale)))

    elif style == PLATE_STYLE_EMBASSY:
        bg_path = './backgrounds/17.bmp'
        bg_image = Image.open(bg_path).resize(size)

        zh_word_path = './words/zhs/zh_33.jpg'
        zh_word = Image.open(zh_word_path)
        zh_word = zh_word.resize((int(45 * scale), int(90 * scale)))
        mask.paste(zh_word, (int(15.5 * scale), int(25 * scale)))
        zh_word = get_word_with_color(zh_word, (255, 0, 0))
        text.paste(zh_word, (int(15.5 * scale), int(25 * scale)))

        for i in range(3):
            string = plate_string[i + 1]
            if string.isdigit():
                num_index = int(string)
                num_word_path = './words/numbers/numbers_' + str(num_index) + '.jpg'
                word = Image.open(num_word_path)
            else:
                en_index = en_array.index(string)
                en_word_path = './words/ens/en_' + str(en_index) + '.jpg'
                word = Image.open(en_word_path)
            word = word.resize((int(45 * scale), int(90 * scale)))
            mask.paste(word, (int((72.5 + 57 * i) * scale), int(25 * scale)))
            word = get_word_with_color(word, (255, 255, 255))
            text.paste(word, (int((72.5 + 57 * i) * scale), int(25 * scale)))

        for i in range(3):
            string = plate_string[i + 4]
            if string.isdigit():
                num_index = int(string)
                num_word_path = './words/numbers/numbers_' + str(num_index) + '.jpg'
                word = Image.open(num_word_path)
            else:
                en_index = en_array.index(string)
                en_word_path = './words/ens/en_' + str(en_index) + '.jpg'
                word = Image.open(en_word_path)

            word = word.resize((int(45 * scale), int(90 * scale)))
            mask.paste(word, (int((265.5 + 57 * i) * scale), int(25 * scale)))
            word = get_word_with_color(word, (255, 255, 255))
            text.paste(word, (int((265.5 + 57 * i) * scale), int(25 * scale)))

    elif (style == PLATE_STYLE_HK or
          style == PLATE_STYLE_MC or
          style == PLATE_STYLE_COACH):

        if style == PLATE_STYLE_HK or style == PLATE_STYLE_MC:
            bg_path = './backgrounds/4.bmp'
            bg_image = Image.open(bg_path).resize(size, Image.ANTIALIAS)
            first_color = (255, 255, 255)
            text_color = (255, 255, 255)
            last_color = (255, 255, 255)
            last_word_path = ('./words/zhs/zh_31.jpg' if style == PLATE_STYLE_HK
                              else './words/zhs/zh_32.jpg')
        else:
            bg_path = './backgrounds/6.bmp'
            bg_image = Image.open(bg_path).resize(size, Image.ANTIALIAS)
            first_color = (0, 0, 0)
            text_color = (0, 0, 0)
            last_color = (0, 0, 0)
            last_word_path = './words/zhs/zh_35.jpg'

        zh_index = zh_array.index(plate_string[0])
        zh_word_path = './words/zhs/zh_' + str(zh_index) + '.jpg'
        zh_word = Image.open(zh_word_path)
        zh_word = zh_word.resize((int(45 * scale), int(90 * scale)), Image.ANTIALIAS)
        mask.paste(zh_word, (int(15.5 * scale), int(25 * scale)))
        zh_word = get_word_with_color(zh_word, first_color)
        text.paste(zh_word, (int(15.5 * scale), int(25 * scale)))

        en_index = en_array.index(plate_string[1])
        en_word_path = './words/ens/en_' + str(en_index) + '.jpg'
        en_word = Image.open(en_word_path)
        en_word = en_word.resize((int(45 * scale), int(90 * scale)), Image.ANTIALIAS)
        mask.paste(en_word, (int(72.5 * scale), int(25 * scale)))
        en_word = get_word_with_color(en_word, text_color)
        text.paste(en_word, (int(72.5 * scale), int(25 * scale)))

        for i in range(4):
            string = plate_string[i + 2]
            if string.isdigit():
                num_index = int(string)
                num_word_path = './words/numbers/numbers_' + str(num_index) + '.jpg'
                word = Image.open(num_word_path)
            else:
                en_index = en_array.index(string)
                en_word_path = './words/ens/en_' + str(en_index) + '.jpg'
                word = Image.open(en_word_path)
            word = word.resize((int(45 * scale), int(90 * scale)), Image.ANTIALIAS)
            mask.paste(word, (int((151.5 + 57 * i) * scale), int(25 * scale)))
            word = get_word_with_color(word, text_color)
            text.paste(word, (int((151.5 + 57 * i) * scale), int(25 * scale)))

        lsat_word = Image.open(last_word_path)
        lsat_word = lsat_word.resize((int(45 * scale), int(90 * scale)), Image.ANTIALIAS)
        mask.paste(lsat_word, (int((94.5 + 57 * 5) * scale), int(25 * scale)))
        lsat_word = get_word_with_color(lsat_word, last_color)
        text.paste(lsat_word, (int((94.5 + 57 * 5) * scale), int(25 * scale)))

    bg_image = np.array(bg_image)
    mask = np.array(mask)
    text = np.array(text)

    bg_image = cv2.bitwise_and(mask, bg_image)
    combine = cv2.bitwise_or(text, bg_image)  # pure text
    result = Image.fromarray(combine)
    return result


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Automatically generate images of Chinese license plates')

    parser.add_argument('output', type=str, help='Output directory')
    parser.add_argument('-T', '--text', type=str, help='Target plates number')
    parser.add_argument('-r', '--rand', action='store_true', help='Generate plates randomly')
    parser.add_argument('-t', '--type', type=str, help='Plates type: blue/yellow/white/coach/embassy/hk/mc', default='blue')
    args = parser.parse_args()
    output = args.output

    type_maps = {
        'blue': (PLATE_TYPE_NORMAL, PLATE_STYLE_BLUE, 'b_'),
        'yellow': (PLATE_TYPE_NORMAL, PLATE_STYLE_YELLOW, 'y_'),
        'white': (PLATE_TYPE_POLICE, PLATE_STYLE_POLICE, 'p_'),
        'coach': (PLATE_TYPE_COACH, PLATE_STYLE_COACH, 'c_'),
        'embassy': (PLATE_TYPE_EMBASSY, PLATE_STYLE_EMBASSY, 'e_'),
        'hk': (PLATE_TYPE_HK, PLATE_STYLE_HK, 'h_'),
        'mc': (PLATE_TYPE_MC, PLATE_STYLE_MC, 'm_')
    }

    size = (440, 140)

    if not os.path.exists(output):
        os.mkdir(output)

    if args.rand:
        _type = args.type
        file_name = ''
        plate_type, plate_style, file_name = type_maps[_type]
        plate_string = generate_random_plate_string(plate_type)

        result = generate_plate_image(plate_style, plate_string, size)
        file_name = file_name + plate_string + '.jpg'
        result.save(os.path.join(output, file_name))
    else:
        _type = args.type
        text = args.text
        file_name = ''
        if _type in type_maps:
            plate_type, plate_style, file_name = type_maps[_type]
            result = generate_plate_image(plate_style, text, size)
            file_name = file_name + text + '.jpg'
            result.save(os.path.join(output, file_name))
        else:
            print("--type option value error.")



    # turn = 0
    # cached_plate_strings = []

    # while turn < 1000:

    #     plate_string = generate_random_plate_string(plate_type)
    #     if plate_string not in cached_plate_strings:
    #         cached_plate_strings.append(plate_string)
    #         print('generate %d image' % (turn + 1))
    #         size = (440, 140)
    #         result = generate_plate_image(plate_style, plate_string, size)
    #         image_name = base_path + plate_string + '.jpg'
    #         result.save(image_name)
    #         turn += 1
    # print("complete!")
