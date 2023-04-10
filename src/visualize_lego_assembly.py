import cv2
import numpy as np
import yaml

board_size = [20, 20]

with open('example_list.yaml', 'r') as file:
    assembly_list = yaml.safe_load(file)
file.close()

with open('standard_lego_library.yaml', 'r') as file:
    lego_lib = yaml.safe_load(file)
file.close()

scale = 40
board_img = np.ones((board_size[0] * scale, board_size[1] * scale, 3), dtype=np.uint8) * 255

for p in assembly_list:
    piece = assembly_list[p]
    piece_id = piece['id']
    x = piece['x']
    y = piece['y']
    height = lego_lib[piece_id]['height']
    width = lego_lib[piece_id]['width']
    color = lego_lib[piece_id]['color']
    if (color == 'black'):
        c = [0, 0, 0]
    elif (color == 'orange'):
        c = [0, 150, 255]
    ori = piece['ori']
    if (ori == 0):
        board_img[y * scale: (y + height) * scale, x * scale: (x + width) * scale, :] = c
    else:
        board_img[y * scale: (y + width) * scale, x * scale: (x + height) * scale, :] = c

cv2.imshow('f', board_img)
cv2.waitKey(0)
