import wave
import struct
import math

SAMPLE_RATE = 22050

def make_tone(filename, freq, duration_ms, volume=0.5):
    with wave.open(filename, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        
        num_samples = int(SAMPLE_RATE * (duration_ms / 1000.0))
        for i in range(num_samples):
            # ADSR envelope: quick attack, slow release
            envelope = 1.0
            if i < 0.1 * num_samples:
                envelope = i / (0.1 * num_samples)
            elif i > 0.5 * num_samples:
                envelope = 1.0 - (i - 0.5 * num_samples) / (0.5 * num_samples)
                
            sample = int(volume * envelope * 32767.0 * math.sin(2.0 * math.pi * freq * i / SAMPLE_RATE))
            wav.writeframes(struct.pack('<h', sample))

# awake beep: 800Hz, 150ms
make_tone('awake.wav', 800, 150, 0.5)
# done beep: 400Hz, 200ms
make_tone('done.wav', 400, 200, 0.5)
