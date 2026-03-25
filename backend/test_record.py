import pyaudio, wave, time

MIC_INDEX = 1
CHUNK = 4096        # bigger buffer = more stable
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, input_device_index=MIC_INDEX,
                frames_per_buffer=CHUNK)

# Warm up the stream — discard first 10 chunks
print('Warming up mic...')
for _ in range(10):
    stream.read(CHUNK, exception_on_overflow=False)

print('Recording for 5 seconds... speak now!')
frames = []
for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK, exception_on_overflow=False)
    frames.append(data)

stream.stop_stream()
stream.close()
p.terminate()

with wave.open('C:/VoiceOS/backend/test.wav', 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

print('Saved to C:/VoiceOS/backend/test.wav')