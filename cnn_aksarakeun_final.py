# -*- coding: utf-8 -*-
"""CNN_AKSARAKEUN_FINAL.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZQzGfgwcQD3hR3XHODgcpjsiKTwn5ebM
"""

import zipfile
import pandas as pd
import numpy as np
import os

# Membaca file zip
zip_file_path = "imageset.zip"
folder_path = "imageset"
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(folder_path)

folder_path = "imageset"
# Menginisialisasi list kosong untuk menyimpan data gambar dan label
image_data = []
label_data = []


# Melakukan iterasi pada setiap folder di dalam folder_path
for folder_name in ['a', 'ae', 'ba', 'ca', 'da', 'e', 'eu', 'fa', 'ga',
                     'ha', 'i', 'ja', 'ka', 'ma', 'na', 'nga', 'nya', 'o',
                     'pa', 'qa', 'ra', 'sa', 'ta', 'u', 'va', 'wa', 'xa', 'ya', 'za']:
    folder_dir = os.path.join(folder_path, folder_name)
    if os.path.isdir(folder_dir):
        # Melakukan iterasi pada setiap file di dalam folder
        for filename in os.listdir(folder_dir):
            file_path = os.path.join(folder_dir, filename)
            if os.path.isfile(file_path):
                # Menambahkan path file (gambar) ke dalam list image_data
                image_data.append(file_path)
                # Menambahkan label folder ke dalam list label_data
                label_data.append(folder_name)

# Membuat DataFrame dari list image_data dan label_data
df = pd.DataFrame({'images': image_data, 'label': label_data})

# Menampilkan DataFrame
df

import matplotlib.pyplot as plt
import cv2

# Menampilkan 5 contoh gambar dari setiap label
for label in df['label'].unique():
    label_images = df[df['label'] == label]['images'].sample(5)  # Mengambil 5 gambar acak dari setiap label
    plt.figure(figsize=(10, 4))
    for i, img_path in enumerate(label_images):
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.subplot(1, 5, i+1)
        plt.imshow(img)
        plt.axis('off')
        plt.title(label)
    plt.show()

from tensorflow.keras.preprocessing.image import img_to_array, load_img
from sklearn.preprocessing import LabelEncoder

# Inisialisasi array untuk menyimpan gambar dan label
images = []
labels = []

# Mengubah gambar menjadi format yang sesuai

for index, row in df.iterrows():
    img_path = row['images']
    label = row['label']
    img = load_img(img_path, target_size=(224, 224))  # Mengubah ukuran gambar menjadi 224x224 pixels
    img = img_to_array(img) / 255.0  # Normalisasi piksel menjadi nilai antara 0 dan 1
    images.append(img)
    labels.append(label)

images = np.array(images)

# Mengubah label menjadi nilai numerik menggunakan LabelEncoder
label_encoder = LabelEncoder()
labels = label_encoder.fit_transform(labels)

#train test split
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=0)

print("Jumlah data pada set pelatihan:")
print("X_train:", len(X_train))
print("y_train:", len(y_train))
print("\nJumlah data pada set pengujian:")
print("X_test:", len(X_test))
print("y_test:", len(y_test))

from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
'''
# Membangun model CNN
model = Sequential()
model.add(Conv2D(16, (3, 3), activation='relu', input_shape=(224, 224, 3)))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(32, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(32, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Flatten())
model.add(Dense(10, activation='relu'))
model.add(Dense(len(label_encoder.classes_), activation='softmax'))
model.summary()
'''

# Model Development
import keras
from keras.models import Sequential
from keras.layers import Dense, Conv2D, MaxPool2D , Flatten, Dropout, LeakyReLU, GlobalMaxPooling2D, Activation
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.optimizers import Adam

model=Sequential()

model.add(Conv2D(32,(5,5),padding='same',input_shape=(224,224, 3)))
model.add(LeakyReLU(alpha=.02))
model.add(MaxPool2D(pool_size=(2,2)))
# model.add(Dropout(.2))

model.add(Conv2D(196,(5,5)))
model.add(LeakyReLU(alpha=.02))
model.add(MaxPool2D(pool_size=(2,2)))
model.add(Dropout(.3))

model.add(GlobalMaxPooling2D())
model.add(Dense(1024))
model.add(LeakyReLU(alpha=.02))
model.add(Dropout(.3))   #asalnya 2

model.add(Dense(29))
model.add(Activation('softmax'))
model.summary()

import datetime

# Mulai menghitung waktu eksekusi
start_time = datetime.datetime.now()
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

#check point
#checkpoint = ModelCheckpoint("my_model.h5", monitor='val_accuracy', verbose=1, save_weights_only=False, mode='auto', period=1)
# Old code with 'period' argument
checkpoint_callback = ModelCheckpoint(filepath='my_model.h5', monitor='val_loss', save_weights_only=True, period=5)

# Updated code with 'save_freq' argument
checkpoint_callback = ModelCheckpoint(filepath='my_model.h5', monitor='val_loss', save_weights_only=True, save_freq='epoch')


# Early Stopping
early_stopping = EarlyStopping(monitor='val_loss', min_delta=0, patience=20, verbose=1, mode='auto')#restore_best_weights=True


# Melatih model dengan seluruh data
history = model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test, y_test), callbacks=[early_stopping])

# Selesai eksekusi, hitung waktu total
end_time = datetime.datetime.now()

# Hitung selisih waktu
execution_time = end_time - start_time
print("Waktu eksekusi: ", execution_time)
hours, remainder = divmod(execution_time.seconds, 3600)
minutes, seconds = divmod(remainder, 60)
print("Waktu eksekusi: {} jam, {} menit, {} detik".format(hours, minutes, seconds))

import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt

# Prediksi menggunakan model
y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred_classes)
print("Confusion Matrix:")
print(cm)

# Classification Report
target_names = label_encoder.classes_
print("\nClassification Report:")
print(classification_report(y_test, y_pred_classes, target_names=target_names))

import seaborn as sns
# Visualisasi Confusion Matrix
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.show()

# Training dan Validation Accuracy
plt.figure(figsize=(10, 6))
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

# Training dan Validation Loss
plt.figure(figsize=(10, 6))
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()



saved_model_path = "mymodel.h5"

# YOUR CODE HERE
model.save(saved_model_path)

#!pip install tensorflowjs

import tensorflow as tf
#import tensorflowjs as tfjs

# Specify the path to your saved Keras model
saved_model_path = "mymodel.h5"

# Load the saved Keras model
model = tf.keras.models.load_model(saved_model_path)

# Specify the output directory where the converted files will be saved
output_dir = "output_directory"

# Convert the Keras model to TensorFlow.js format
#tfjs.converters.save_keras_model(model, output_dir)

import keras.utils as image

img = image.load_img("testing.png", target_size=(224, 224), color_mode='grayscale')
img = np.asarray(img)
img_rgb = np.repeat(img[..., np.newaxis], 3, axis=-1)  # Mengulang saluran warna
plt.imshow(img_rgb)
img_rgb = np.expand_dims(img_rgb, axis=0)

from keras.models import load_model
saved_model = load_model("mymodel.h5")
output = saved_model.predict(img_rgb)

max = output[0][0]
pos = 0
for i in range(1, 29):
    if output[0][i] > max:
        max = output[0][i]
        pos = i

print(output)
print(max)

if (pos == 0) :
    print('a')
elif (pos == 1) :
    print('ae')
elif (pos == 2) :
    print('ba')
elif (pos == 3) :
    print('ca')
elif (pos == 4) :
    print('da')
elif (pos == 5) :
    print('e')
elif (pos == 6) :
    print('eu')
elif (pos == 7) :
    print('fa')
elif (pos == 8) :
    print('ga')
elif (pos == 9) :
    print('ha')
elif (pos == 10) :
    print('i')
elif (pos == 11) :
    print('ja')
elif (pos == 12) :
    print('ka')
elif (pos == 13) :
    print('ma')
elif (pos == 14) :
    print('na')
elif (pos == 15) :
    print('nga')
elif (pos == 16) :
    print('nya')
elif (pos == 17) :
    print('o')
elif (pos == 18) :
    print('pa')
elif (pos == 19) :
    print('qa')
elif (pos == 20) :
    print('ra')
elif (pos == 21) :
    print('sa')
elif (pos == 22) :
    print('ta')
elif (pos == 23) :
    print('u')
elif (pos == 24) :
    print('va')
elif (pos == 25) :
    print('wa')
elif (pos == 26) :
    print('xa')
elif (pos == 27) :
    print('ya')
elif (pos == 28) :
    print('za')

