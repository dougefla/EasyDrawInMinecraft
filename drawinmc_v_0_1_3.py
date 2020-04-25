'''
developing_version:Color support

'''
import sys
import argparse
import matplotlib.pyplot as graph
import numpy as np
from numpy import fft
import math
from cv2 import cv2 as cv2

class point_gray:
    x = 0
    z = 0
    color = 0
    new_color = -1
    has_group = 0
    def __init__(self, x, z, color, has_group, new_color = -1):
        self.x = x
        self.z = z
        self.color = color
        self.has_group = has_group
        self.new_color = new_color

class point_bgr:
    x = 0
    z = 0
    bgr = [0,0,0]
    new_bgr = [-1,-1,-1]
    has_group = 0
    def __init__(self, x, z, bgr, has_group, new_bgr = [-1,-1,-1]):
        self.x = x
        self.z = z
        self.bgr = bgr
        self.has_group = has_group
        self.new_bgr = new_bgr




def get_single_block(point_color):
    
    if point_color>150:
        block = "white_concrete"
    elif point_color>100:
        block = "light_gray_concrete"
    elif point_color>50:
        block = "gray_concrete"
    elif point_color<=50:
        block = "black_concrete"
    return block

def get_bit_color(point_color):
    
    if point_color>150:
        block = 250
    elif point_color>100:
        block = 150
    elif point_color>50:
        block = 50
    elif point_color<=50:
        block = 0
    return block


def get_single_command(x1, z1, x2, z2, block,dp,y=0):
    return "fill "+'~'+str(dp[0]+x1)+' '+'~'+str(dp[1]+y)+' '+'~'+str(dp[2]+z1)+' '+'~'+str(dp[0]+x2)+' '+'~'+str(dp[1]+y)+' '+'~'+str(dp[2]+z2)+' '+block+'\n'

def init_map(img,size):
    p_map = [[0 for i in range(size)] for i in range(size)]
    #将图片缩小便于显示观看
    img=cv2.resize(img,(size,size),interpolation=cv2.INTER_CUBIC)

    #将图片转为灰度图
    img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    #cv2.imwrite('gray.jpg', img_gray)


    for i in range(size):
        for j in range(size):
            #print(img_gray[j,i])
            p_map[i][j] = point_gray(i,j,img_gray[j,i],0)
            img_gray[j][i] = get_bit_color(img_gray[j][i])
    #cv2.imwrite('/var/www/flask-prod/bit.jpg', img_gray)
    return p_map


def draw(img_path, size, dp):
    img = cv2.imread(img_path)
    p_map = init_map(img, size)
    keypoint = []
    fd = open('result.mcfunction','w+')

    for i in range(size):
        for j in range(size):
            #print(p_map[i][j].color)
            #遍历所有像素
            exit_flag = 0
            if p_map[i][j].has_group == 0:

                #如果当前像素不属于任何一个组，以其为一个顶点画最大矩阵
                p_corner = point_gray(i,j,p_map[i][j].color,1)
                flag_2 =0
                for jj in range(j+1, size):#先向右找,用p_corner标记另一个顶点
                    if jj == size-1 and get_bit_color(p_map[i][jj].color) == get_bit_color(p_corner.color):
                        flag_2 = 1 # 如果是该行最后一个，而且也符合要求，那么就强制向下扩
                        p_map[i][jj].has_group = 1
                        break
                    if get_bit_color(p_map[i][jj].color) == get_bit_color(p_corner.color):#如果可以向右扩，就向右扩;                                                                                
                        p_map[i][jj].has_group = 1
                    else:#如果不能向右扩，就向下扩，注意当前点列坐标为jj-1
                        for ii in range(i+1,size):
                            #检验当前点作为顶点的话，与p_corner形成的矩形中是否无杂点
                            flag_1 = 1#校验是否无杂点
                            for jjj in range(p_corner.x, jj):#校验当前行即可
                                if not get_bit_color(p_map[ii][jjj].color) == get_bit_color(p_corner.color):
                                    flag_1 = 0
                                    break#只要有一个点不符合就跳出
                            if flag_1 == 1:#如果当前行无杂点，就把该行标记为已分组，继续向下直到达到size
                                for jjj in range(p_corner.x, jj):
                                    p_map[i][jjj].has_group = 1
                            else:#如果当前行有杂点，停止向下
                                keypoint.append([p_corner,p_map[ii-1][jj-1]])#返回点对
                                exit_flag = 1#直接退到最外层
                                break
                        if exit_flag ==1:
                            break
                        keypoint.append([p_corner,p_map[size-1][jj-1]])#向下扩到底，也返回点对
                        break
                        
                if flag_2==1:#是该行最后一个，而且也符合要求，那么就强制向下扩
                    for ii in range(i+1,size):
                        #检验当前点作为顶点的话，与p_corner形成的矩形中是否无杂点
                        flag_1 = 1#校验是否无杂点
                        for jjj in range(p_corner.x, jj):#校验当前行即可
                            if not get_bit_color(p_map[ii][jjj].color) == get_bit_color(p_corner.color):
                                flag_1 = 0
                                break#只要有一个点不符合就跳出
                        if flag_1 == 1:#如果当前行无杂点，就把该行标记为已分组，继续向下直到达到size
                            for jjj in range(p_corner.x, jj):
                                p_map[i][jjj].has_group = 1
                        else:#如果当前行有杂点，停止向下
                            keypoint.append([p_corner,p_map[ii-1][jj-1]])#返回点对
                            exit_flag = 1
                    if exit_flag ==1:
                        break
                    keypoint.append([p_corner,p_map[size-1][jj-1]])#向下扩到底，也返回点对
                    break
    for pp in keypoint:
        #print(pp[0].x)
        fd.write(get_single_command(pp[0].x,pp[0].z,pp[1].x,pp[1].z,get_single_block(pp[0].color),dp))
    fd.close()
    return


def get_rect_color(p_map, x0, z0, dsize):
    status = 0
    rect_color = []
    for i in range(x0, x0+dsize):
        for j in range(z0, z0+dsize):
            rect_color.append(p_map[i][j].color)
    #print(rect_color)
    new_color = max(rect_color, key=rect_color.count)
    if not new_color == p_map[x0][z0].new_color:
        status = 1
        for i in range(x0, x0+dsize):
            for j in range(z0, z0+dsize):
                p_map[i][j].new_color = new_color
        return [p_map,new_color,status]
    else:
        status = 0
        return [p_map,new_color,status]

def draw_new(img_path, size, dp):
    img = cv2.imread(img_path)
    p_map = init_map(img, size)
    fd = open('result_new.mcfunction','w+')
    dsize = 128
    while not dsize == 0:
        for i in range(0, size, dsize):
            for j in range(0, size, dsize):
                #print(i,j,dsize)
                [p_map,color, status] = get_rect_color(p_map, i, j, dsize)
                if status == 1:
                    result = get_single_command(i,j,i+dsize-1,j+dsize-1,get_single_block(color),dp)
                    fd.write(result)
                #print(result)
        dsize = int(dsize/2)

    fd.close()

'''
def main():
    parser = argparse.ArgumentParser(description='Easy Draw in Minecraft')
    parser.add_argument('--path', type=str, help='The path of source picture, like: ./sample.jpg')
    parser.add_argument('--size', type=int, default = 128, help='The expect size of the pic in MC, default 128', required = False)
    parser.add_argument('--pos', type=str, default = '[10,10,10]', help='The related position of the pic in MC, default [10,10,10]',required = False)

    args = parser.parse_args()
    position = eval(args.pos)
    draw(args.path,args.size, position)
'''

draw_new('eriri.jpg',128,[10,10,10])
#draw('eriri.jpg',128,[10,10,10])