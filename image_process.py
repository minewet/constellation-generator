import cv2
import numpy as np

from sklearn.neighbors import NearestNeighbors
from scipy.sparse.csgraph import connected_components
import networkx as nx

class StarImage:
    def __init__(self, file_name):
        self.file_path = file_name

        self.image = cv2.imread("input/"+self.file_path, cv2.IMREAD_COLOR)
        self.binary = self.get_binary()
        self.size = self.binary.shape

        self.stars = self.detect_stars()
        save_image(self.binary, "input/binary_"+self.file_path)


    def get_binary(self, threshold_value=50, max_value=255): 
        grayscale_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, thresholded = cv2.threshold(grayscale_image, threshold_value, max_value, cv2.THRESH_BINARY)
        
        return thresholded

    def detect_stars(self, min_size=1):
        stars = [] 

        contours, _ = cv2.findContours(self.binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour) # 윤곽선을 둘러싸는 최소한의 원 (x,y, radius)
            if radius < min_size: 
                cv2.drawContours(self.binary, contour, -1, (120, 120, 120), thickness=cv2.FILLED)
                continue
            center = (round(y), round(x))
            stars.append(center)
        return stars



def connect_knn(image, stars, k=2):
    coords = np.array(stars)

    # K-Nearest Neighbors (K-NN) with k=2
    nbrs = NearestNeighbors(n_neighbors=k+1, algorithm='ball_tree').fit(coords)
    distances, indices = nbrs.kneighbors(coords)

    height, width = image.shape
    canvas = np.ones((height, width), np.uint8) * 255
    for i in range(len(stars)):
        for j in indices[i][1:]:  # Skip the first index because it's the point itself
            cv2.line(canvas, coords[i][::-1], coords[j][::-1], 0, thickness=2)

    num_labels, labels, _, _ = cv2.connectedComponentsWithStats(255-canvas, connectivity=8, ltype=cv2.CV_32S)

    extracted_images = []

    for label in range(1, num_labels):
        component = np.ones_like(canvas) * 255
        component[labels == label] = 0
        extracted_images.append(component)
        save_image(component, f"output/component_{label}.png")    
    return extracted_images


def overlay_image(image, line, opacity = 0.2):
    result = image.copy()
    line = ((255-line) * opacity).astype(np.uint8)
    result += cv2.cvtColor(line, cv2.COLOR_GRAY2BGR) 
    return result


def save_image(image, name):
    cv2.imwrite(name, image)        


def new_canvas(size):
    canvas = np.ones(size, np.uint8) * 255
    return canvas

def draw_line(canvas, p1, p2, thickness=2):
    cv2.line(canvas, p1,p2, 0, thickness=thickness)
    return canvas