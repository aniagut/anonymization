import os
from PIL import Image, UnidentifiedImageError

sad_folder = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\train_images\\sad\\'
happy_folder = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\train_images\\happy\\'
neutral_folder = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\train_images\\neutral\\'
angry_folder = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\train_images\\angry\\'
disgust_folder = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\train_images\\disgust\\'
fear_folder = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\train_images\\fear\\'
surprise_folder = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\train_images\\surprise\\'

sad_folder_new = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\train_images_new\\sad\\'
happy_folder_new = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\train_images_new\\happy\\'
neutral_folder_new = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\train_images_new\\neutral\\'
angry_folder_new = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\train_images_new\\angry\\'
disgust_folder_new = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\train_images_new\\disgust\\'
fear_folder_new = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\train_images_new\\fear\\'
surprise_folder_new = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\train_images_new\\surprise\\'

folders = [sad_folder, happy_folder, neutral_folder, angry_folder, disgust_folder, fear_folder, surprise_folder]
new_folders = [sad_folder_new, happy_folder_new, neutral_folder_new, angry_folder_new, disgust_folder_new, fear_folder_new, surprise_folder_new]

for folder, new_folder in zip(folders, new_folders):
    for filename in os.listdir(folder):

        f = os.path.join(folder, filename)
        name, extension = os.path.splitext(filename)
        new_f = os.path.join(new_folder, f"{name}.jpg")
        # checking if it is a file
        if os.path.isfile(f):
            try:
                image = Image.open(f)
                new_image = image.resize((48, 48))
                image_gray = new_image.convert('L')
                image_gray.save(new_f)
            except UnidentifiedImageError:
                pass