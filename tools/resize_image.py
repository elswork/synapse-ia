from PIL import Image
import os

img_path = "/home/pirate/docker/anticitera.deft.work/public/img/soberania_digital_comite.png"

if os.path.exists(img_path):
    img = Image.open(img_path)
    print(f"Original size: {img.size}")
    
    # "75% más pequeña" implies reducing area by 75%, leaving 25%.
    # This corresponds to scaling dimensions by 0.5 (0.5 * 0.5 = 0.25)
    
    new_size = (int(img.size[0] * 0.5), int(img.size[1] * 0.5))
    resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    resized_img.save(img_path)
    print(f"Resized to: {new_size}")
else:
    print("Image not found")
