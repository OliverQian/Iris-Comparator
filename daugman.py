from PIL import Image, ImageDraw
import math

def daugman_algorithm():
    image = load_image('eye2.jpg')
    width, height = image.size
    print(width,height)
    pixels = gray_scale()
    array_of_radius_for_cords = [[0]*height for i in range(width)]
    for y in range(100,height-100,3):
        for x in range(100,width-100,3):

            #middle point of circle
            temp_list_of_intensity = []
            max_diff = 0
            for r in range(1,90):

                #get the intensity sum for given input x y and r

                intensity_sum_for_curr_radius = get_intensity_sum(x,y,r, pixels, height, width)

                temp_list_of_intensity.append(intensity_sum_for_curr_radius)

            radius_for_given_pixel = radius_of_maximal_difference(temp_list_of_intensity, max_diff)

            array_of_radius_for_cords[x][y] = radius_for_given_pixel


    #TODO: get maximum value from arra_of_radius_for cords value and draw image from  that


    ellipse_touple = get_elipse_touple(array_of_radius_for_cords, width, height)
    print(ellipse_touple)
    draw = ImageDraw.Draw(image)
    draw.point((ellipse_touple[0],ellipse_touple[1]),fill='red')
    draw.ellipse((ellipse_touple[0] - ellipse_touple[2], ellipse_touple[1] - ellipse_touple[2]
                  , ellipse_touple[0] + ellipse_touple[2], ellipse_touple[1] + ellipse_touple[2]), outline='blue')
    image.show()


def get_elipse_touple(array,width,height):
    touple = (0,0,0)
    max_diff = 0
    for i in range(width):
        for j in range(height):
            curr_val = array[i][j]
            if curr_val > max_diff:
                max_diff = curr_val
                touple = (i,j,curr_val)
    return touple


def radius_of_maximal_difference(intensity_sum_list, max_difference):
    it_to_return = 0
    for it in range(0,intensity_sum_list.__len__()-1):
        temp_diff = intensity_sum_list[it + 1] - intensity_sum_list[it]
        if  temp_diff > max_difference:
            max_difference = temp_diff
            it_to_return = it
    return it_to_return


def get_intensity_sum(x,y,radius, pixel_array,height, width):
    intensity_sum = 0
    for alfa in range(0, 360,10):
        curr_x = int(x + radius * math.cos(alfa))
        curr_y = int(y + radius * math.sin(alfa))

        if width > curr_x > 0 and height > curr_y > 0 :
            r = pixel_array[curr_x][curr_y]
            intensity_sum += r
    return intensity_sum

def load_image(image_name):
    return Image.open(image_name)

def gray_scale():
    image = load_image('eye2.jpg')
    rgb_image = image.convert('RGB')
    width, height = image.size
    pixel_table = image.load()
    channel_table = [[0]*height for i in range(width)]
    for y in range(height):
        for x in range(width):
            r,g,b = rgb_image.getpixel((x,y))
            #pixel = pixel_table[x,y]
            value = 0.3*r + 0.6*g + 0.1*b
            pixel_table[x,y] = (int(value),int(value),int(value))
            channel_table[x][y]=int(value)
    return channel_table

daugman_algorithm()

# image = gray_scale()
# rgb_image = image.convert('RGB')
# width, height = image.size
# print(width,height)
# pixels = image.load()
# print(get_intensity_sum(0,0,10,pixels))


#for x in range(0,10,3):

#draw = ImageDraw.Draw(image)
#r = 20
#draw.point((180, 180), fill='red')
#draw.ellipse((180 - r, 180 - r, 180 + r, 180 + r), outline='blue')


#  TODO: Daugman algorithm
#  set the middle of the image, check for all values to the r, from small to big one. try to compute the sum of the value of the pixels on the boarder(sum of intensities)
#  if p is starting point sum we got the array p1,p2,p3,....px where x = height/2
#  after passing the border of the iris the value differ much and we can use it to extract iris
#  on  output array we are looking for the pair with biggest difference, and then this pk is the parameter of our iris and k is length of our radius of our iris
#  if iris is not included we can skip an image
#  we can define some marginis to make complexity of our algorithm a bit better
#  increase x and y not by 1 you can do it by 3 or 4
#  TODO: daugman integral method + compute sum of pixels on the border compute it by using polar coordinates x = r * cos(alfa), y = rsin(alfa) where alfa[0;2pi] alfa(step) = pi / 1000;


