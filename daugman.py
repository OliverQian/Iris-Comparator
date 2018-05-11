import operator
from PIL import Image, ImageDraw
import math
import cv2
import numpy as np
import os
from sqlite3 import dbapi2 as sqlite


TABLE_NAME = 'PROCESSED_IRIS_TABLE'


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

    def _set_image(self, image_to_set):
        self.image = image_to_set

    def get_image(self):
        return self.image

    def set_image_tuple(self, _tuple):
        self.tuple = _tuple

    def get_image_tuple(self):
        return self.tuple

    def get_pixel_table(self):
        return self.pixel_table

    def set_center_of_iris_x(self, x):
        self.center_of_iris_x = x

    def set_center_of_iris_y(self, y):
        self.center_of_iris_y = y

    def set_radius_of_iris(self, radius):
        self.radius = radius

    def open_image(self):
        return Image.open(self.image_name)

    def gray_scale(self):
        _image = self.get_image()
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

    def gaussian_filter(self, coeff):
        processed_image = np.array(self.image)
        processed_image = cv2.GaussianBlur(processed_image, (5, 5), coeff)
        self.image = Image.fromarray(processed_image)


def daugman_algorithm(image_name, gaus_coeff, id):
    _image = EyeImage(image_name, id)
    _image.gaussian_filter(gaus_coeff)
    width, height = _image.get_image().size
    pixels = _image.get_pixel_table()
    array_of_radius_for_cords = [[0]*height for i in range(width)]
    start_r = 45
    for y in range(int(height/4), height, 3):
        for x in range(int(width/4), width, 3):
            temp_list_of_intensity = []
            max_diff = 0
            for r in range(start_r,int(height/2)):
                intensity_sum_for_curr_radius = _image.get_intensity_sum(x,y,r, pixels, _image.height, _image.width)
                temp_list_of_intensity.append(intensity_sum_for_curr_radius)
            radius_for_given_pixel, max_diff_for_given_coordinates = _image.radius_of_maximal_difference(temp_list_of_intensity, max_diff)
            radius_difference_touple = (radius_for_given_pixel+start_r, max_diff_for_given_coordinates)
            array_of_radius_for_cords[x][y] = radius_difference_touple
    _image.set_image_tuple(_image.get_ellipse_tuple(array_of_radius_for_cords, width, height))
    draw = ImageDraw.Draw(_image.image)
    _image.set_center_of_iris_x(_image.tuple[0])
    _image.set_center_of_iris_y(_image.tuple[1])
    _image.set_radius_of_iris(_image.tuple[2])
    draw.point((_image.center_of_iris_x, _image.center_of_iris_y), fill='red')
    draw.ellipse(
         (
             _image.center_of_iris_x - _image.radius, _image.center_of_iris_y - _image.radius,
             _image.center_of_iris_x + _image.radius, _image.center_of_iris_y + _image.radius),
             outline = 'blue')
    rectangle_with_iris = create_rectangle_from_obtained_iris_perimiter(_image.center_of_iris_x, _image.center_of_iris_y, _image.radius, _image.pixel_table, _image.get_image())
    cropped_iris_rectangle = crop_obtained_unwrapped_rectangle_of_iris(rectangle_with_iris)
    normalized = histogram_normalization(cropped_iris_rectangle)
    median_fiter_img = median_filter(normalized)
    lbp_img = local_binary_pattern(median_fiter_img)
    byte_code = chunk_encoding(lbp_img)
    return byte_code


def create_rectangle_from_obtained_iris_perimiter(center_of_circle_x, center_of_circle_y, radius_of_iris, list_of_pixels, image):
    unwrapped_rectangle_image_of_the_radius = Image.new('L', (360, radius_of_iris))
    pixel_table_of_rectangle = unwrapped_rectangle_image_of_the_radius.load()
    width, height = image.size
    for alfa in range(0, 360):
        for r in range(0, radius_of_iris):
            curr_pixel_x = center_of_circle_x + r * math.cos(math.radians(alfa))
            curr_pixel_y = center_of_circle_y + r * math.sin(math.radians(alfa))
            if curr_pixel_x < width and curr_pixel_y < height:
                intensity = list_of_pixels[int(curr_pixel_x)][int(curr_pixel_y)]
                pixel = EyePixel(curr_pixel_x, curr_pixel_y, intensity)
                pixel_table_of_rectangle[alfa, r] = pixel.channel_value
    return unwrapped_rectangle_image_of_the_radius


def crop_obtained_unwrapped_rectangle_of_iris(rectangle):

    rec_width, rec_height = rectangle.size
    processed_rectangle = rectangle.crop((0, rec_height/3, rec_width, rec_height/3 + 16))
    return processed_rectangle


def median_filter(image_array):
    median = cv2.medianBlur(image_array, 5)
    processed_image = Image.fromarray(median)
    return processed_image


def histogram_normalization(image):
    image_array = np.array(image)
    normalized_image_array = cv2.normalize(image_array, image_array, 0, 255, cv2.NORM_MINMAX)
    return normalized_image_array


def create_code_from_binary_array(arr):
    pixel_code = ''
    pixel_code += str(arr[0][0])
    pixel_code += str(arr[0][1])
    pixel_code += str(arr[0][2])
    pixel_code += str(arr[1][2])
    pixel_code += str(arr[2][2])
    pixel_code += str(arr[2][1])
    pixel_code += str(arr[2][0])
    pixel_code += str(arr[1][0])
    if pixel_code == '11111111':
        pixel_code = '11111110'
    return pixel_code


def local_binary_pattern(image):
    width, height = image.size
    pixel_array = image.load()
    arr = np.zeros([height, width])
    code_for_image = ''
    for y in range(0,height):
        for x in range(0, width):
            binary_arr = np.zeros([3,3], dtype=int)
            center_pixel = pixel_array[x, y]
            for i in range(0, 3):
                for j in range(0, 3):
                    if x-1+i < 0 or y-1+j<0 or x-1+i >= width or y-1+j >= height:
                        binary_arr[i][j] = 0
                    else:
                        curr_pixel = pixel_array[x+i-1, y+j-1]
                        if center_pixel <= curr_pixel:
                            binary_arr[i][j] = 0
                        else:
                            binary_arr[i][j] = 1
            code_for_pixel = create_code_from_binary_array(binary_arr)
            code_for_image += code_for_pixel
            arr[y][x] = int(code_for_pixel, 2)
    im2 = Image.fromarray(arr)
    return im2


def calculate_mean(start_x, start_y, width, height, image):
    pixel_table = np.array(image)
    sum_of_intensities = 0
    for x in range(start_x, width + start_x):
        for y in range(start_y, height + start_y):
            sum_of_intensities += pixel_table[y][x]
    deviation = sum_of_intensities/(width*height)
    return deviation


def calculate_variance(start_x, start_y, width, height, image, mean):
    pixel_table = np.array(image)
    sum_of_intensities = 0
    for x in range(start_x, width + start_x):
        for y in range(start_y, height + start_y):
            intensity = pixel_table[y][x]
            sum_of_intensities += math.pow(intensity, 2)
    variance = math.sqrt((sum_of_intensities/(width*height)) - math.pow(mean,2))
    return variance


def chunk_encoding(image):
    width, height = image.size
    global_deviation = calculate_mean(0, 0, width, height, image)
    global_variance = calculate_variance(0, 0, width, height, image, global_deviation)
    list_of_deviance_variance_tuples = []
    y_step = 4
    x_step = 36
    for y in range(0, height - y_step + 1, y_step):
        for x in range(0, width - x_step + 1, x_step):
            mean = calculate_mean(x, y, x_step, y_step, image)
            variance = calculate_variance(x, y, x_step, y_step, image, mean)
            deviance_variance_tuple = (mean, variance)
            list_of_deviance_variance_tuples.append(deviance_variance_tuple)
    byte_code = ''
    for i in range(list_of_deviance_variance_tuples.__len__()):
        _tuple = list_of_deviance_variance_tuples[i]
        if _tuple[0] <= global_deviation:
            byte_code += str('0')
        else:
            byte_code += str('1')
        if _tuple[1] <= global_variance:
            byte_code += str('0')
        else:
            byte_code += str('1')
        if i + 1 < list_of_deviance_variance_tuples.__len__():
            next_tuple = list_of_deviance_variance_tuples[i+1]
            if _tuple[0] <= next_tuple[0]:
                byte_code += str('0')
            else:
                byte_code += str('1')
            if _tuple[1] <= next_tuple[1]:
                byte_code += str('0')
            else:
                byte_code += str('1')
        else:
            byte_code += str('00')

    return byte_code


def connect_to_database(name_of_database):
    connection = sqlite.connect(name_of_database)
    return connection


def get_db_cursor(connection):
    cursor = connection.cursor()
    return cursor


def fill_database(name_of_db,root_path):
    connection = connect_to_database(name_of_db)
    cursor = get_db_cursor(connection)
    count = 0
    create_table_sql = """ CREATE TABLE IF NOT EXISTS """ + TABLE_NAME + """ (
                                        id integer PRIMARY KEY,
                                        person_id integer,
                                        name text NOT NULL,
                                        path_to_img text NOT NULL,
                                        byte_code text NOT NULL);
                                        """
    cursor.execute(create_table_sql)
    for root, dirs, files in os.walk(root_path, topdown=True):
        for name in files:
            if not name.startswith('.') and not name.__eq__('Thumbs.db'):
                img_path = os.path.join(root, name)
                id = root.split("/")
                print('Processing img number %d' % count)
                byte_code = daugman_algorithm(img_path, count)
                cursor.execute("insert into " + TABLE_NAME + " values (?,?,?,?,?)",
                               [count, int(id[5]), name, img_path, byte_code])
                out = "For personId= " + id[5] + name + ' byte code  = {}'.format(byte_code)
                print(out)
                count += 1
    connection.commit()
    connection.close()
    print('Filling db ended, connection closed, changes commited')


def calculate_hamming_distance(code1, code2):
    sum = 0
    for i in range(len(code1)):
        sum += int(code1[i],2) ^ int(code2[i],2)
    return sum/len(code1)


def prepare_dataset(name_of_db, training_set = []):
    connection = connect_to_database(name_of_db)
    cursor = get_db_cursor(connection)
    data = [[0]*2 for i in range(1214)]
    row_c = 0
    rows = cursor.execute("SELECT person_id, byte_code FROM " + TABLE_NAME)
    for row in rows:
        string_code = str(row[1])
        data[row_c][1] = string_code
        data[row_c][0] = row[0]
        row_c += 1
    for x in range(len(data)-1):
        training_set.append(data[x])


def getNeighbours(training_set, test_instance, k):
    distances = []
    for x in range(len(training_set)):
        dist = calculate_hamming_distance(test_instance, training_set[x][1])
        distances.append((training_set[x], dist))
    distances.sort(key=operator.itemgetter(1))
    neighbors = []
    for x in range(k):
        neighbors.append(distances[x][0])
    return neighbors


def getResponse(neigbours):
    class_votes = {}
    for x in range(len(neigbours)):
        response = neigbours[x][0]
        if response in class_votes:
            class_votes[response] += 1
        else:
            class_votes[response] = 1
    return max(class_votes.items(), key=operator.itemgetter(1))[0]

#fill_database("/Users/Tomek/Desktop/iris.db", "/Users/Tomek/Desktop/Sessao_1")


def KNN(byte_code, k):
    training = []
    prepare_dataset("/Users/Tomek/Desktop/iris.db", training)
    neighbours = getNeighbours(training, byte_code, k)
    print(neighbours)
    response = getResponse(neighbours)
    print(response)


for i in range(1, 6):
    byte_code = daugman_algorithm('/Users/Tomek/Desktop/UBIRIS_200_150_R/Sessao_2/56/Img_56_2_'+str(i)+'.jpg', 1, 1)
    KNN(byte_code, 5)