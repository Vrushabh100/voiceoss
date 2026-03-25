import pyaudio, wave, whisper, tempfile, os
import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wav_io

MIC_INDEX = 1
CHUNK = 4096
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

WAKE_WORD = 'siri'

print("Loading Whisper model...")
model = whisper.load_model('small')
print("Model loaded.")

def record_chunk(seconds=4):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, input_device_index=MIC_INDEX,
                    frames_per_buffer=CHUNK)

    # Warm up mic
    for _ in range(5):
        stream.read(CHUNK, exception_on_overflow=False)

    frames = []
    for _ in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    fd, path = tempfile.mkstemp(suffix='.wav')
    with os.fdopen(fd, 'wb') as f:
        with wave.open(f, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

    # Boost and resample for Whisper
    sample_rate, data = wav_io.read(path)
    data = np.clip(data.astype(np.float32) * 40, -32768, 32767).astype(np.int16)
    resampled = signal.resample(data, int(len(data) * 16000 / sample_rate)).astype(np.int16)
    wav_io.write(path, 16000, resampled)

    return path

def transcribe(path):
    result = model.transcribe(path, language='en', fp16=False)
    os.remove(path)
    return result['text'].strip().lower()

print(f'Say "{WAKE_WORD}" to activate...')

try:
    while True:
        # Step 1 — listen for wake word
        tmp = record_chunk(3)
        text = transcribe(tmp)

        if not text:
            continue

        print(f'Heard: {text}')

        # Step 2 — check for wake word
        if WAKE_WORD in text:
            print('Wake word detected! Listening for command...')

            # Step 3 — record the actual command
            tmp2 = record_chunk(5)
            command = transcribe(tmp2)

            if command:
                print(f'Command received: {command}')
            else:
                print('No command heard, try again.')

except KeyboardInterrupt:
    print("\nStopping VoiceOS...")