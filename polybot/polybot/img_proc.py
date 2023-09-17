from pathlib import Path
from matplotlib.image import imread, imsave
import random


def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


class Img:

    def __init__(self, path):
        """
        Do not change the constructor implementation
        """
        self.path = Path(path)
        self.data = rgb2gray(imread(path)).tolist()

    def save_img(self):
        """
        Do not change the below implementation
        """
        new_path = self.path.with_name(self.path.stem + '_filtered' + self.path.suffix)
        imsave(new_path, self.data, cmap='gray')
        return new_path

    def blur(self, blur_level=16):

        height = len(self.data)
        width = len(self.data[0])
        filter_sum = blur_level ** 2

        result = []
        for i in range(height - blur_level + 1):
            row_result = []
            for j in range(width - blur_level + 1):
                sub_matrix = [row[j:j + blur_level] for row in self.data[i:i + blur_level]]
                average = sum(sum(sub_row) for sub_row in sub_matrix) // filter_sum
                row_result.append(average)
            result.append(row_result)

        self.data = result

    def contour(self):
        for i, row in enumerate(self.data):
            res = []
            for j in range(1, len(row)):
                res.append(abs(row[j-1] - row[j]))

            self.data[i] = res

    def rotate(self):
        # TODO remove the `raise` below, and write your implementation
        raise NotImplementedError()

    def salt_n_pepper(self):
        for row_num, row_data in enumerate(self.data):
            res = []
            for i in range(0, len(row_data)):
                pixel = row_data[i]
                rand = random.random()
                if rand < 0.2:
                    pixel = 255
                if rand > 0.8:
                    pixel = 0
                res.append(pixel)
            self.data[row_num] = res

    def concat(self, other_img, direction='horizontal'):
        # TODO remove the `raise` below, and write your implementation
        raise NotImplementedError()

    def segment(self):
        for row_num, row_data in enumerate(self.data):
            res = []
            for i in range(0, len(row_data)):
                pixel = row_data[i]
                if pixel > 100:
                    pixel = 255
                else:
                    pixel = 0
                res.append(pixel)
            self.data[row_num] = res


if __name__ == "__main__":
    my_img = Img('/home/setatm/GitExc/ImageProcessingService/polybot/test/beatles.jpeg')
    # my_img.salt_n_pepper()
    my_img.segment()
    my_img.save_img()
