import pandas as pd
import os
import shutil

dataset = pd.read_csv('legend.csv', usecols = ['image','emotion'])

img_emotions = {}

for index, row in dataset.iterrows():
    img_emotions[row['image']] = row['emotion']

directory = 'images'
sad_folder = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\sad\\'
happy_folder = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\happy\\'
neutral_folder = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\neutral\\'
angry_folder = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\angry\\'
disgust_folder = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\disgust\\'
fear_folder = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\fear\\'
surprise_folder = 'C:\\Users\\PC\\Desktop\\emotions-train-dataset\\surprise\\'

for filename in os.scandir(directory):

    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)

        # checking if it is a file
        if os.path.isfile(f):
            if img_emotions.keys().__contains__(filename):

                emotion = img_emotions[filename]
                if emotion == 'anger':
                    shutil.move(os.path.abspath(f), angry_folder + filename)
                elif emotion == 'surprise':
                    shutil.move(os.path.abspath(f), surprise_folder + filename)
                elif emotion == 'disgust':
                    shutil.move(os.path.abspath(f), disgust_folder + filename)
                elif emotion == 'fear':
                    shutil.move(os.path.abspath(f), fear_folder + filename)
                elif emotion == 'neutral':
                    shutil.move(os.path.abspath(f), neutral_folder + filename)
                elif emotion == 'happiness':
                    shutil.move(os.path.abspath(f), happy_folder + filename)
                elif emotion == 'sadness':
                    shutil.move(os.path.abspath(f), sad_folder + filename)


