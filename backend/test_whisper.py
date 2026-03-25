import whisper
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal

# Load and boost the audio
sample_rate, data = wav.read('C:/VoiceOS/backend/test.wav')

# Convert stereo to mono if needed
if len(data.shape) == 2:
    data = data.mean(axis=1).astype(np.int16)

# Boost volume by 10x
data = np.clip(data.astype(np.float32) * 10, -32768, 32767).astype(np.int16)

# Resample to 16000Hz (Whisper requirement)
if sample_rate != 16000:
    samples = int(len(data) * 16000 / sample_rate)
    data = signal.resample(data, samples).astype(np.int16)

# Save boosted audio
wav.write('C:/VoiceOS/backend/test_boosted.wav', 16000, data)

# Transcribe boosted file
model = whisper.load_model('small')
result = model.transcribe('C:/VoiceOS/backend/test_boosted.wav', language='en', fp16=False)
print('Transcription:', result['text'])
