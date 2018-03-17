from PIL import Image, ImageDraw
import math
#import numpy as np
#TODO: hrbmUBIRIS haslo do database

def daugman_algorithm():
    image = load_image('eye3.jpg')
    width, height = image.size
    print(width,height)
    pixels = gray_scale('eye3.jpg')

    array_of_radius_for_cords = [[0]*height for i in range(width)]

    start_r = 15

    for y in range(int(height/4),height,2):

        for x in range(int(width/4),width,2):

            temp_list_of_intensity = []
            max_diff = 0

            for r in range(start_r,int(height/2)):

                # TODO: zmienic fora zeby range bral step pi/1000 i funkcja ma brac 2pi a nie 360 + store max_diffa i na podstawie maxdiffa wybieramy najbardziej adekwatny promien

                #obliczam tutaj sume intesywnosci dla danego okregu o ustalonym r : (1,90)
                intensity_sum_for_curr_radius = get_intensity_sum(x,y,r, pixels, height, width)
                #wkladam na liste dla danego x,y wartosc sumy intensywnosci w szufladce ktora odpowiada dlugosci promienia
                temp_list_of_intensity.append(intensity_sum_for_curr_radius)

            #w tym momencie otrzymuje radius dla danego x i y przy ktorym maksymalna roznica pomiedzy r+1 a r jest najwieksza
            radius_for_given_pixel, max_diff_for_given_coordinates = radius_of_maximal_difference(temp_list_of_intensity,max_diff)


            radius_difference_touple = (radius_for_given_pixel+start_r, max_diff_for_given_coordinates)


            array_of_radius_for_cords[x][y] = radius_difference_touple



    #teraz z tablicy wyciagam wartosci x y r maxdiff i na podstawie maxdiff wyciagamy coordynaty naszego okregu

    ellipse_tuple = get_ellipse_tuple(array_of_radius_for_cords,width,height)
    print(ellipse_tuple)
    image.convert('RGB')
    draw = ImageDraw.Draw(image)
    draw.point((ellipse_tuple[0],ellipse_tuple[1]), fill='red')
    draw.ellipse(
         (
             ellipse_tuple[0] - ellipse_tuple[2], ellipse_tuple[1] - ellipse_tuple[2],
             ellipse_tuple[0] + ellipse_tuple[2], ellipse_tuple[1] + ellipse_tuple[2]),
             outline= 'blue')
    image.show()


def get_ellipse_tuple(array,width,height):
    tuple_ = (0,0,0,0)
    max_diff = 0
    for i in range(width):
        for j in range(height):
            if array[i][j] != 0 :
                curr_tuple = array[i][j]
                curr_radius = curr_tuple[0]
                curr_max_diff = curr_tuple[1]
                if (i == 340 or i == 341 or i == 342) and (j == 231 or j == 232 or j == 233):
                    print(i,j,curr_radius,curr_max_diff)
                if curr_max_diff > max_diff and curr_radius > 0:
                    max_diff = curr_max_diff
                    tuple_ = (i,j,curr_radius,curr_max_diff)
    return tuple_


def radius_of_maximal_difference(intensity_sum_list, max_difference):
    it_to_return = 0
    for it in range(0,intensity_sum_list.__len__()-1):
        temp_diff = intensity_sum_list[it + 1] - intensity_sum_list[it]
        if  temp_diff > max_difference:
            max_difference = temp_diff
            it_to_return = it
    return it_to_return,max_difference

def get_intensity_sum(x,y,radius, pixel_array,height, width):
    intensity_sum = 0
    for alfa in range(0, 360):
        curr_x = int(x + radius * math.cos(math.radians(alfa)))
        curr_y = int(y + radius * math.sin(math.radians(alfa)))
        if width > curr_x >= 0 and height > curr_y >= 0 :
            r = pixel_array[curr_x][curr_y]
            intensity_sum += r
    return intensity_sum

def load_image(image_name):
    return Image.open(image_name)

def gray_scale(image_name):
    image = load_image(image_name)
    rgb_image = image.convert('RGB')
    width, height = image.size
    pixel_table = image.load()
    channel_table = [[0]*height for i in range(width)]
    for y in range(height):
        for x in range(width):
            r,g,b = rgb_image.getpixel((x,y))
            #pixel = pixel_table[x,y]
            #value = 0.3*r + 0.6*g + 0.1*b
            value = r
            pixel_table[x,y] = (int(value))
            channel_table[x][y]=int(value)
    return channel_table

daugman_algorithm()


#  TODO: Daugman algorithm
#  set the middle of the image, check for all values to the r, from small to big one. try to compute the sum of the value of the pixels on the boarder(sum of intensities)
#  if p is starting point sum we got the array p1,p2,p3,....px where x = height/2
#  after passing the border of the iris the value differ much and we can use it to extract iris
#  on  output array we are looking for the pair with biggest difference, and then this pk is the parameter of our iris and k is length of our radius of our iris
#  if iris is not included we can skip an image
#  we can define some marginis to make complexity of our algorithm a bit better
#  increase x and y not by 1 you can do it by 3 or 4
#  TODO: daugman integral method + compute sum of pixels on the border compute it by using polar coordinates x = r * cos(alfa), y = rsin(alfa) where alfa[0;2pi] alfa(step) = pi / 1000;

#TODO: klasyfikacja z sieciami neuronowymi + cross-validation
