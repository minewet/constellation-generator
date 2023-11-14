from image_process import StarImage, connect_knn, get_overlay_image, save_image

file = "sky.jpg"

starImg = StarImage(file)
print(starImg.stars)

knn = connect_knn(starImg.binary, starImg.stars)

for i, classs in enumerate(knn):
    save_image(get_overlay_image(starImg.image, classs), f"output/overlay_{i+1}.png")
