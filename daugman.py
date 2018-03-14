from PIL import Image, ImageDraw
import math

def daugman_algorithm():
    image = gray_scale()
    rgb_image = image.convert('RGB')
    width, height = image.size
    print(width,height)
    pixels = image.load()
    max_diff = 0
    for y in range(60,height,3):
        for x in range(50,width,3):

            #middle point of circle
            list_of_intensiteis_for_given_radius = []

            for r in range(0,height/2):
                #get the intensity sum for given input x y and r
                intensity_sum_for_curr_radius = get_intensity_sum(x,y,r, pixels)
                list_of_intensiteis_for_given_radius[r] = intensity_sum_for_curr_radius

            check_maximal_difference(list_of_intensiteis_for_given_radius,max_diff)
            list_of_intensiteis_for_given_radius.index(max_diff)
    image.show()


def check_maximal_difference(intensity_sum_list, max_difference):
    for it in range(0,intensity_sum_list.__len__()-1):
        if intensity_sum_list[it+1]-intensity_sum_list[it] > max_difference:
            max_difference = intensity_sum_list[it+1]-intensity_sum_list[it]

def get_intensity_sum(x,y,radius, pixel_array):
    intensity_sum = 0
    for alfa in range(0, 360):
        curr_x = int(x + radius * math.cos(alfa))
        curr_y = int(y + radius * math.sin(alfa))
        #print(curr_x, curr_y)
        if curr_x > 0 and curr_y > 0:
            r,g,b = pixel_array[curr_x,curr_y]
            #print(r)
            intensity_sum += r
    return intensity_sum

def load_image(image_name):
    return Image.open(image_name)

def gray_scale():
    image = load_image('eye.jpg')
    rgb_image = image.convert('RGB')
    width, height = image.size
    pixel_table = image.load()
    for y in range(height):
        for x in range(width):
            r,g,b = rgb_image.getpixel((x,y))
            #pixel = pixel_table[x,y]
            value = 0.3*r + 0.6*g + 0.1*b
            pixel_table[x,y] = (int(value),int(value),int(value))
    return image

#daugman_algorithm()



image = gray_scale()
rgb_image = image.convert('RGB')
width, height = image.size
print(width,height)
pixels = image.load()
print(get_intensity_sum(0,0,10,pixels))


#for x in range(0,10,3):

#draw = ImageDraw.Draw(image)
#r = 20
#draw.point((180, 180), fill='red')
#draw.ellipse((180 - r, 180 - r, 180 + r, 180 + r), outline='blue')


#  TODO: Daugman algorithm
#  set the middle of the image, check for all values to the r, from small to big one. try to compute the sum of the value of the pixels on the boarder(sum of intensities)
#  if p is starting point sum we got the array p1,p2,p3,....px where x = height/2
#  after passing the border of the iris the value differ much and we can use it to extract iris
#  on  output array we are looking for the pair with biggest difference, and then this pk is the paramiter of our iris and k is length of our radius of our iris
#  if iris is not included we can skip an image
#  we can define some marginis to make complexity of our algorithm a bit better
#  increase x and y not by 1 you can do it by 3 or 4
#  TODO: daugman integral method + compute sum of pixels on the border compute it by using polar coordinates x = r * cos(alfa), y = rsin(alfa) where alfa[0;2pi] alfa(step) = pi / 1000;


