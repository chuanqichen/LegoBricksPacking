import cv2
import numpy as np
import yaml

board_size = [20, 20]

with open('example_list.yaml', 'r') as file:
    assembly_list = yaml.safe_load(file)
file.close()

with open('standard_lego_library.yaml', 'r') as file:  # Type of Brick
    lego_lib = yaml.safe_load(file)
file.close()

scale = 40
board_img = np.ones((board_size[0] * scale, board_size[1] * scale, 3), dtype=np.uint8) * 255

for p in assembly_list:
    print(p)

graph = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: [], 13: []}
for p in assembly_list:
    piece = assembly_list[p]
    piece_id = piece['id']
    x = piece['x']
    y = piece['y']
    height = lego_lib[piece_id]['height']
    width = lego_lib[piece_id]['width']
    color = lego_lib[piece_id]['color']
    if color == 'black':
        c = [0, 0, 0]
    elif color == 'orange':
        c = [0, 150, 255]
    ori_one = piece['ori']
    if ori_one == 0:
        board_img[y * scale: (y + height) * scale, x * scale: (x + width) * scale, :] = c
    else:
        board_img[y * scale: (y + width) * scale, x * scale: (x + height) * scale, :] = c
    cv2.imshow('f', board_img)
    cv2.waitKey(0)

    print(str(p) + " " + str(piece))
    for p2 in assembly_list:
        if p is p2: continue
        piece2 = assembly_list[p2]
        piece_id2 = piece2['id']
        x2 = piece2['x']
        y2 = piece2['y']
        height2 = lego_lib[piece_id]['height']
        width2 = lego_lib[piece_id]['width']
        color2 = lego_lib[piece_id]['color']
        ori_two = piece2['ori']

        if ori_one:



    graph[p].append(p2)

        # FIGURE OUT HOW TO CORRECT ORIENTATION
        # dimension = []


        # if x > x2 and y < y2:
        #     if ori_two == 0:
        #         dimension.append(width2)
        #     if ori_two == 1:
        #         dimension.append(height2)
        #     if ori_one == 0:
        #         dimension.append(height)
        #     if ori_one == 1:
        #         dimension.append(width)
        #
        #     if x2 + dimension[0] + 1 >= x and y + dimension[1] + 1 >= y2:  # Width 2 and height 1
        #         graph[p].append(p2)
        # elif x < x2 and y < y2:
        #     if ori_one == 0:
        #         dimension.append(width)
        #         dimension.append(height)
        #     if ori_one == 1:
        #         dimension.append(height)
        #         dimension.append(width)
        #
        #     if x + dimension[0] + 1 >= x2 and y + dimension[1] + 1 >= y2:  # width 1 and height 1
        #         graph[p].append(p2)
        # elif x < x2 and y > y2: # Might be wrong
        #     if ori_two == 0:
        #         dimension.append(height2)
        #     if ori_two == 1:
        #         dimension.append(width2)
        #     if ori_one == 0:
        #         dimension.append(width)
        #     if ori_one == 1:
        #         dimension.append(height)
        #
        #     if x + dimension[0] + 1 >= x2 and dimension[1] + 1 >= y:  # width 1 and height 2
        #         graph[p].append(p2)
        # elif x > x2 and y > y2:
        #     if ori_two == 0:
        #         dimension.append(width2)
        #         dimension.append(height2)
        #     if ori_two == 1:
        #         dimension.append(height2)
        #         dimension.append(width2)
        #
        #     if x2 + dimension[0] + 1 >= x and y2 + dimension[1] + 1 >= y:  # width 2 and height 2
        #         graph[p].append(p2)

print(graph)

cv2.imshow('f', board_img)
cv2.waitKey(0)
