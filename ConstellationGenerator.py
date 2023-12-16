import tkinter as tk
from PIL import Image, ImageTk
from image_process import *

import cv2
import numpy as np


class App:
    def __init__(self, droot):
        self.root = root
        self.root.title("Constellation Creator")

        self.filename = "sky.png" # 이미지 경로 지정
        self.starImg = StarImage(self.filename)
        self.size = self.starImg.size[::-1]
        self.stars = [(b, a) for a, b in self.starImg.stars]

        self.canvas = tk.Canvas(root, width=self.size[0], height=self.size[1], bg="black")
        self.canvas.pack()

        self.load_background_image("input/binary_"+self.filename)  
        self.drawn_image = new_canvas(self.starImg.size)

        self.output_line = None
        self.output_overlay = None

        # 클릭 이벤트 연결
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # 연결된 별들의 리스트
        self.activated_star = None

        reset_button = tk.Button(root, text="Reset", command=self.reset_canvas)
        reset_button.pack(side=tk.LEFT, padx=10, pady=10)

        fix_button = tk.Button(root, text="Fix", command=self.fix_canvas)
        fix_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        submit_button = tk.Button(root, text="Submit", command=self.submit_canvas)
        submit_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.knn_lines = []
        self.knn_index = 0
        knn_button = tk.Button(root, text="K-NN", command=self.knn)
        knn_button.pack(side=tk.LEFT, padx=10, pady=10)


    def load_background_image(self, image_path):
        # 이미지 로드 및 적절한 크기 조절
        self.image = Image.open(image_path)
        self.image = self.image.resize(self.size, Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(self.image)
        
        # 캔버스에 이미지 배치
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_image)

    def on_canvas_click(self, event):
        """ 캔버스 클릭 시 이벤트 처리 """
        clicked_star = self.find_closest_star(event.x, event.y)
        if clicked_star:
            if self.activated_star:
                self.canvas.create_line(self.activated_star[0], self.activated_star[1], clicked_star[0], clicked_star[1], fill="#aaaaaa", width=3)
                self.drawn_image = draw_line(self.drawn_image, self.activated_star, clicked_star)
            self.activated_star = clicked_star
        else:
            self.activated_star = None

    def find_closest_star(self, x, y):
        """ 클릭된 위치와 가장 가까운 별을 찾습니다. """
        closest_star = None
        min_dist = 20
        for star in self.stars:
            dist = ((star[0] - x) ** 2 + (star[1] - y) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest_star = star
        return closest_star if min_dist < 15 else None
    
    def reset_canvas(self):
        self.canvas.delete("all")
        self.load_background_image("input/binary_"+self.filename)  
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_image)
        self.drawn_image = new_canvas(self.starImg.size)
        self.activated_star = None
        self.knn_index = 0

    def fix_canvas(self):
        save_image(self.drawn_image, "processed/drawing.png")
        save_image(overlay_image(self.starImg.image, self.drawn_image), "processed/overlay_drawing.png")

        self.canvas.delete("all")
        self.load_background_image("processed/overlay_drawing.png")  
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_image)
        self.drawn_image = new_canvas(self.starImg.size)

    def submit_canvas(self):
        if self.knn_index:
            self.output_line = f"processed/line_{self.knn_index}.png"
            self.output_overlay = f"processed/overlay_{self.knn_index}.png"
        else: 
            self.fix_canvas()
            self.output_line = "processed/drawing.png"
            self.output_overlay = "processed/overlay_drawing.png"
        root.destroy()


    def knn(self):
        knn_lines = connect_knn(self.starImg.binary, self.starImg.stars)
        for i, classs in enumerate(knn_lines):
            save_image(overlay_image(self.starImg.image, classs), f"processed/overlay_{i+1}.png")
            
        if self.knn_index >= len(knn_lines): self.knn_index = 1
        else: self.knn_index +=1

        self.canvas.delete("all")
        self.load_background_image(f"processed/overlay_{self.knn_index}.png")  
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_image)
        self.drawn_image = new_canvas(self.starImg.size)




import sys
print("\n*･--- 𝐂𝐨𝐧𝐬𝐭𝐞𝐥𝐥𝐚𝐭𝐢𝐨𝐧 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐨𝐫 --·*");

webcam = cv2.VideoCapture(0)

if not webcam.isOpened():
    print("Could not find camera.")
    exit()

while webcam.isOpened():
    status, frame = webcam.read()

    if status:
        cv2.imshow("test", frame)

    if cv2.waitKey(1) & 0xFF == ord(' '):
        cv2.imwrite("./input/sky.png", frame)
        break
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

webcam.release()
cv2.destroyAllWindows()
print("* Sky Captured.")

# 애플리케이션 실행
root = tk.Tk()
app = App(root)
root.mainloop()

print("* Star Connected.")



sys.argv = ["", app.output_line, app.output_overlay, app.size]
exec(open("chatGPT_API.py").read())