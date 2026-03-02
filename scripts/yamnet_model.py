import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import os
import librosa

CONFIG = {
    "CLASS_NUMBER": 7,
    "SAMPLE_RATE": 16000,
    "BATCH_SIZE": 32,
    "DATASET_PATH": "2_processed_audio",
    "EPOCHS": 20
}

def load_wav(file_path):
    audio, sr = librosa.load(file_path, sr=CONFIG["SAMPLE_RATE"], mono=True)
    return audio.astype(np.float32)

def extract_embeddings(waveform):
    score, embeddings, spectrogram = yamnet(waveform)
    embedding = tf.reduce_mean(embeddings, axis=0)
    return embedding

yamnet = hub.load("https://tfhub.dev/google/yamnet/1")

# Tworzenie datasetu
X = []
y = []

base_dir = os.path.dirname(os.path.abspath(__file__))  # katalog, w którym jest skrypt
dataset_path = os.path.join(base_dir, "..", CONFIG["DATASET_PATH"])
dataset_path = os.path.abspath(dataset_path)

class_names = sorted(os.listdir(dataset_path))

for label, class_name in enumerate(class_names):
    class_directory = os.path.join(CONFIG["DATASET_PATH"], class_name)
    for file in os.listdir(class_directory):
        if file.endswith(".wav"):
            path = os.path.join(class_directory, file)
            waveform = load_wav(path)
            embedding = extract_embeddings(waveform)
            X.append(embedding.numpy())
            y.append(label)

X = np.array(X)
y = np.array(y)

inputs = tf.keras.Input(shape=(1024,))
x = tf.keras.layers.Dense(256, activation="relu")(inputs)
x = tf.keras.layers.Dropout(0.3)(x)
outputs = tf.keras.layers.Dense(CONFIG["CLASS_NUMBER"], activation="softmax")(x)

model = tf.keras.Model(inputs, outputs)

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-3),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.fit(
    X, y,
    batch_size=CONFIG["BATCH_SIZE"],
    epochs=CONFIG["EPOCHS"],
    validation_split=0.2
)

model.save("yamnet_sound_classifier.keras")