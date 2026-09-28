import asyncio
import os
import random
import miniaudio
import numpy as np
import scipy.signal
from openwakeword.utils import AudioFeatures
import edge_tts

print("=== Entrenamiento Rápido y Optimizado: 'Hey Arquímedes' ===", flush=True)

# Extractor oficial OpenWakeWord
af = AudioFeatures(inference_framework='tflite')

VOICES = [
    "es-ES-AlvaroNeural",   # España Hombre
    "es-ES-ElviraNeural",   # España Mujer
    "es-ES-XimenaNeural",   # España Mujer 2
    "es-MX-JorgeNeural",    # México Hombre
    "es-MX-DaliaNeural",    # México Mujer
    "es-CO-GonzaloNeural",  # Colombia Hombre
    "es-AR-TomasNeural"     # Argentina Hombre
]

POSITIVE_PHRASES = [
    "Hey Arquímedes",
    "Hey Arquimedes",
    "Oye Arquímedes",
    "Arquímedes"
]

NEGATIVE_PHRASES = [
    # Confusores fonéticos cercanos
    "Aquí me ves", "Aquí me veis", "Arqueología", "Arquitectura", "Alquimista",
    "Arturo", "Arturito", "Alquimia", "Arco iris", "Anticitera", "Hey Athena",
    "Oye Athena", "Athena", "Ok Nabu", "Nabu", "Alexa", "Hey Jarvis", "Jarvis",
    # Comandos comunes de domótica y charla
    "enciende la luz", "apaga la luz", "que hora es", "que tiempo hace",
    "reproduce musica", "sube el volumen", "baja el volumen", "silencio",
    "buenas noches", "buenos dias", "cuentame un chiste", "pon un temporizador",
    "cancela la alarma", "abre la persiana", "hola a todos", "como estas"
]

TARGET_SR = 16000
TARGET_LEN = 32000 # 2.0 segundos

async def generate_tts(text, voice):
    try:
        comm = edge_tts.Communicate(text, voice)
        data = b""
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                data += chunk["data"]
        if not data:
            return None
        decoded = miniaudio.decode(data, nchannels=1, sample_rate=TARGET_SR)
        samples = np.array(decoded.samples, dtype=np.float32)
        return samples
    except Exception as e:
        print(f"Error generando TTS ({text} - {voice}): {e}", flush=True)
        return None

async def collect_base_audio():
    positives = []
    print(f"Sintetizando {len(POSITIVE_PHRASES)} frases positivas x {len(VOICES)} voces ({len(POSITIVE_PHRASES)*len(VOICES)} clips)...", flush=True)
    for phrase in POSITIVE_PHRASES:
        for voice in VOICES:
            s = await generate_tts(phrase, voice)
            if s is not None and len(s) > 4000:
                positives.append(s)
    print(f"-> Base positivas descargadas: {len(positives)}", flush=True)

    negatives = []
    print(f"Sintetizando {len(NEGATIVE_PHRASES)} frases negativas...", flush=True)
    for phrase in NEGATIVE_PHRASES:
        voice = random.choice(VOICES)
        s = await generate_tts(phrase, voice)
        if s is not None and len(s) > 4000:
            negatives.append(s)
    print(f"-> Base negativas descargadas: {len(negatives)}", flush=True)
    return positives, negatives

positives_raw, negatives_raw = asyncio.run(collect_base_audio())

print("Aumentando datos en memoria (velocidad, volumen, desfase temporal, ruido)...", flush=True)

augmented_positives = []
speeds = [0.88, 0.94, 1.0, 1.06, 1.12]
volumes = [0.6, 0.85, 1.0, 1.25]
shifts = [0.1, 0.35, 0.6, 0.85]

for raw in positives_raw:
    for spd in speeds:
        if spd != 1.0:
            n_samp = int(len(raw) / spd)
            stretched = scipy.signal.resample(raw, n_samp)
        else:
            stretched = raw.copy()
            
        for vol in volumes:
            scaled = stretched * vol
            if len(scaled) > TARGET_LEN:
                scaled = scaled[:TARGET_LEN]
            pad_total = TARGET_LEN - len(scaled)
            
            for sh in shifts:
                pad_l = int(pad_total * sh)
                pad_r = pad_total - pad_l
                padded = np.pad(scaled, (pad_l, pad_r), mode='constant')
                
                # Muestra limpia
                augmented_positives.append(padded.astype(np.int16))
                
                # Muestra con ruido gaussiano suave
                noise = np.random.randn(TARGET_LEN) * 250.0
                noisy = np.clip(padded + noise, -32768, 32767).astype(np.int16)
                augmented_positives.append(noisy)

print(f"Total muestras positivas generadas: {len(augmented_positives)}", flush=True)

augmented_negatives = []
for raw in negatives_raw:
    for spd in [0.92, 1.0, 1.08]:
        if spd != 1.0:
            n_samp = int(len(raw) / spd)
            stretched = scipy.signal.resample(raw, n_samp)
        else:
            stretched = raw.copy()
        for vol in [0.7, 1.0]:
            scaled = stretched * vol
            if len(scaled) > TARGET_LEN:
                scaled = scaled[:TARGET_LEN]
            pad_total = TARGET_LEN - len(scaled)
            for sh in [0.2, 0.7]:
                pad_l = int(pad_total * sh)
                pad_r = pad_total - pad_l
                padded = np.pad(scaled, (pad_l, pad_r), mode='constant')
                augmented_negatives.append(padded.astype(np.int16))
                noise = np.random.randn(TARGET_LEN) * 250.0
                augmented_negatives.append(np.clip(padded + noise, -32768, 32767).astype(np.int16))

# Negativos de ruido ambiental y silencio
for _ in range(250):
    noise = (np.random.randn(TARGET_LEN) * 500).astype(np.int16)
    augmented_negatives.append(noise)

for _ in range(50):
    silence = np.zeros(TARGET_LEN, dtype=np.int16)
    augmented_negatives.append(silence)

print(f"Total muestras negativas generadas: {len(augmented_negatives)}", flush=True)

# Submuestrear si es necesario para balancear (ej. ~1500 por clase)
if len(augmented_positives) > 2000:
    augmented_positives = random.sample(augmented_positives, 2000)
if len(augmented_negatives) > 2000:
    augmented_negatives = random.sample(augmented_negatives, 2000)

print(f"Muestras balanceadas -> Positivas: {len(augmented_positives)}, Negativas: {len(augmented_negatives)}", flush=True)

print("Extrayendo embeddings con OpenWakeWord AudioFeatures...", flush=True)
X = []
y = []

count = 0
for clip in augmented_positives:
    emb = af._get_embeddings(clip)
    if emb is not None and len(emb) >= 16:
        X.append(emb[-16:, :])
        y.append(1.0)
    count += 1
    if count % 500 == 0:
        print(f"Embeddings positivos procesados: {count}/{len(augmented_positives)}", flush=True)

count = 0
for clip in augmented_negatives:
    emb = af._get_embeddings(clip)
    if emb is not None and len(emb) >= 16:
        X.append(emb[-16:, :])
        y.append(0.0)
    count += 1
    if count % 500 == 0:
        print(f"Embeddings negativos procesados: {count}/{len(augmented_negatives)}", flush=True)

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.float32)

print(f"Dataset X shape: {X.shape}, y shape: {y.shape}", flush=True)

# Permutar aleatoriamente
indices = np.random.permutation(len(X))
X = X[indices]
y = y[indices]

# Liberar extractor TFLite y cargar TensorFlow para entrenamiento
del af
import tensorflow as tf

# Arquitectura FCN estándar OpenWakeWord
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(16, 96)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.LayerNormalization(),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.LayerNormalization(),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print("Iniciando entrenamiento del modelo...", flush=True)
model.fit(X, y, epochs=30, batch_size=32, validation_split=0.15, verbose=2)

loss, acc = model.evaluate(X, y, verbose=0)
print(f"Evaluación final -> Accuracy: {acc * 100:.2f}%, Loss: {loss:.4f}", flush=True)

# Convertir a TFLite
print("Convirtiendo a formato TensorFlow Lite...", flush=True)
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

output_path = "/tmp/hey_arquimedes.tflite"
with open(output_path, "wb") as f:
    f.write(tflite_model)

print(f"¡Modelo TFLite generado con éxito en {output_path} ({len(tflite_model)} bytes)!", flush=True)

# Verificación de inferencia
interp = tf.lite.Interpreter(model_path=output_path)
interp.allocate_tensors()
inp_idx = interp.get_input_details()[0]['index']
out_idx = interp.get_output_details()[0]['index']

pos_tests = X[y == 1][:5]
neg_tests = X[y == 0][:5]

print("\n--- Verificación de Inferencia TFLite ---", flush=True)
for i, sample in enumerate(pos_tests):
    interp.set_tensor(inp_idx, sample[np.newaxis, ...])
    interp.invoke()
    score = float(interp.get_tensor(out_idx)[0][0])
    print(f"Positivo #{i+1} Predicción: {score:.4f} (esperado ~1.0)", flush=True)

for i, sample in enumerate(neg_tests):
    interp.set_tensor(inp_idx, sample[np.newaxis, ...])
    interp.invoke()
    score = float(interp.get_tensor(out_idx)[0][0])
    print(f"Negativo #{i+1} Predicción: {score:.4f} (esperado ~0.0)", flush=True)

print("\n=== Proceso completado exitosamente ===", flush=True)
