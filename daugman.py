from PIL import Image, ImageDraw
import math
#TODO : naprawic import numpy
#hrbmUBIRIS haslo do database
#TODO : klasyfikacja z sieciami neuronowymi + cross-validation
#TODO : (Priorytet = high) tworzenie prostokata z danego okregu
#TODO : (Priorytet = high) procesing uzyskanego juz prostokata
#TODO : (Priorytet = mid) dowiedziec sie jak rozkodowac dany obrazek
#TODO : (Priorytet = high) przygotowac baze danych + os walkera
#TODO : (Priorytet = low) zaczac przygotowywac siec neuronowa



class EyePixel:
    def __init__(self,x_cord,y_cord,color_value):
        self.x = x_cord
        self.y = y_cord
        self.channel_value = color_value
    def print_pixel(self):
       res = 'X = {}, Y = {}, Channel value = {}\n'.format(self.x,self.y,self.channel_value)
       print(res)

class EyeImage:
    def __init__(self, name, id_of_image):
        self.image_name = name
        self.id = id_of_image
        self.image = Image.open(name)
        self.pixel_table = self.gray_scale()
        self.width,self.height = self.image.size

    def __set_image__(self, image_to_set):
        self.image = image_to_set

    def __get_image__(self):
        return self.image

    def __set_image_tuple__(self,_tuple):
        self.tuple = _tuple

    def __get_image_tuple__(self):
        return self.tuple

    def __get_pixel_table__(self):
        return self.pixel_table

    def open_image(self):
        return Image.open(self.image_name)

    def gray_scale(self):
        if self.__get_image__() is not None:
            _image = self.__get_image__()
            rgb_image = _image.convert('RGB')
            width, height = _image.size
            pixel_table = _image.load()
            channel_table = [[0] * height for i in range(width)]
            for y in range(height):
                for x in range(width):
                    r, g, b = rgb_image.getpixel((x, y))
                    value = r
                    pixel_table[x, y] = (int(value))
                    channel_table[x][y] = int(value)
        return channel_table

    def get_intensity_sum(self, x, y, radius, pixel_array, height, width):
        intensity_sum = 0
        for alfa in range(0, 360):
            curr_x = int(x + radius * math.cos(math.radians(alfa)))
            curr_y = int(y + radius * math.sin(math.radians(alfa)))
            if width > curr_x >= 0 and height > curr_y >= 0:
                r = pixel_array[curr_x][curr_y]
                intensity_sum += r
        return intensity_sum

    def radius_of_maximal_difference(self,intensity_sum_list, max_difference):
        it_to_return = 0
        for it in range(0, intensity_sum_list.__len__() - 1):
            temp_diff = intensity_sum_list[it + 1] - intensity_sum_list[it]
            if temp_diff > max_difference:
                max_difference = temp_diff
                it_to_return = it
        return it_to_return, max_difference

    def get_ellipse_tuple(self,array, width, height):
        _tuple = (0, 0, 0, 0)
        max_diff = 0
        for i in range(width):
            for j in range(height):
                if array[i][j] != 0:
                    curr_tuple = array[i][j]
                    curr_radius = curr_tuple[0]
                    curr_max_diff = curr_tuple[1]
                    if curr_max_diff > max_diff and curr_radius > 0:
                        max_diff = curr_max_diff
                        _tuple = (i, j, curr_radius, curr_max_diff)
        return _tuple
    def show_image(self):
        if self.image is not None:
            self.image.show()
        else:
            print("No image is loaded")



def daugman_algorithm(image_name):

    _image = EyeImage(image_name,1)
    width, height = _image.__get_image__().size

    print(width,height)

    pixels = _image.__get_pixel_table__()

    array_of_radius_for_cords = [[0]*height for i in range(width)]

    start_r = 15

    for y in range(int(height/4),height,2):

        for x in range(int(width/4),width,2):

            temp_list_of_intensity = []
            max_diff = 0

            for r in range(start_r,int(height/2)):

                # TODO (maybe) : zmienic fora zeby range bral step pi/1000 i funkcja ma brac 2pi a nie 360 + store max_diffa i na podstawie maxdiffa wybieramy najbardziej adekwatny promien

                #obliczam tutaj sume intesywnosci dla danego okregu o ustalonym r : (1,90)

                intensity_sum_for_curr_radius = _image.get_intensity_sum(x,y,r, pixels, _image.height, _image.width)

                #wkladam na liste dla danego x,y wartosc sumy intensywnosci w szufladce ktora odpowiada dlugosci promienia
                temp_list_of_intensity.append(intensity_sum_for_curr_radius)

            #w tym momencie otrzymuje radius dla danego x i y przy ktorym maksymalna roznica pomiedzy r+1 a r jest najwieksza
            radius_for_given_pixel, max_diff_for_given_coordinates = _image.radius_of_maximal_difference(temp_list_of_intensity,max_diff)


            radius_difference_touple = (radius_for_given_pixel+start_r, max_diff_for_given_coordinates)


            array_of_radius_for_cords[x][y] = radius_difference_touple



    #teraz z tablicy wyciagam wartosci x y r maxdiff i na podstawie maxdiff wyciagamy coordynaty naszego okregu

    _image.__set_image_tuple__(_image.get_ellipse_tuple(array_of_radius_for_cords,width,height))
    print(_image.__get_image_tuple__())

    draw = ImageDraw.Draw( _image.image )
    draw.point((_image.tuple[0],_image.tuple[1]), fill='red')
    draw.ellipse(
         (
             _image.tuple[0] - _image.tuple[2], _image.tuple[1] - _image.tuple[2],
             _image.tuple[0] + _image.tuple[2], _image.tuple[1] + _image.tuple[2]),
             outline= 'blue')

    _image.show_image()


def create_rectangle_from_obtained_iris_perimiter(center_of_circle_x, center_of_circle_y, radius_of_iris, list_of_pixels):

    length_of_rectangle = 2 * math.pi * radius_of_iris
    unwrapped_rectangle_image_of_the_radius = Image.new('RGB',(int(length_of_rectangle),radius_of_iris))
    list_of_pixels_of_iris = []
    list_of_float_pixels = []

    for alfa in range(0,360):
        for r in range(radius_of_iris):
            #TODO: for each r distinct a pixel and add it on the list in proper order starting from right edge to the end
            curr_pixel_x = center_of_circle_x + radius_of_iris * math.cos(math.radians(alfa))
            curr_pixel_y = center_of_circle_y + radius_of_iris * math.sin(math.radians(alfa))
            list_of_float_pixels.append((curr_pixel_x,curr_pixel_y))
            pixel = EyePixel(curr_pixel_x, curr_pixel_y, list_of_pixels[int(curr_pixel_x)][int(curr_pixel_y)])
            list_of_pixels_of_iris.append(pixel)

    for pixel in list_of_pixels_of_iris:
        pixel.print_pixel()

    return unwrapped_rectangle_image_of_the_radius




daugman_algorithm('eye3.jpg')
#create_rectangle_from_obtained_iris_perimiter(100,69,46,pixels)
