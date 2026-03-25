import os
import threading
from typing import Callable

# ============================================================
# MODE SWITCH — change this one line only
# 'text'  = VirtualBox mode (type commands in terminal)
# 'voice' = Real Windows mode (speak via microphone)
# ============================================================
MODE = 'text'

MIC_INDEX  = 1
WAKE_WORD  = 'hey voiceos'
MODEL_SIZE = 'small'
RATE       = 44100
CHUNK      = 4096
BOOST      = 40
SILENCE_THRESHOLD = 500


class TextPipeline:
    def __init__(self, wake_word=WAKE_WORD):
        self.wake_word = wake_word.lower()
        self.running   = False
        self.callback  = None

    def start(self, on_command: Callable):
        self.running  = True
        self.callback = on_command
        threading.Thread(target=self._loop, daemon=True).start()
        print('VoiceOS started in TEXT MODE.')
        print('Type your command and press Enter.')
        print('Type exit to stop.\n')

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            try:
                command = input('VoiceOS> ').strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not command:
                continue
            if command.lower() == 'exit':
                self.running = False
                break
            if command.lower().startswith(self.wake_word):
                command = command[len(self.wake_word):].strip()
            if command and self.callback:
                self.callback(command)


class VoicePipeline:
    def __init__(self, mic_index=MIC_INDEX, wake_word=WAKE_WORD,
                 model_size=MODEL_SIZE):
        import pyaudio, wave, whisper, tempfile
        import numpy as np
        import scipy.signal as sig
        import scipy.io.wavfile as wav_io

        self.pyaudio   = pyaudio
        self.wave      = wave
        self.tempfile  = tempfile
        self.np        = np
        self.sig       = sig
        self.wav_io    = wav_io
        self.mic_index = mic_index
        self.wake_word = wake_word.lower()
        self.running   = False
        self.callback  = None

        print('Loading Whisper model...')
        self.model = whisper.load_model(model_size)
        print('Whisper ready.')

    def record(self, seconds=4):
        p = self.pyaudio.PyAudio()
        stream = p.open(format=self.pyaudio.paInt16, channels=1,
                        rate=RATE, input=True,
                        input_device_index=self.mic_index,
                        frames_per_buffer=CHUNK)
        for _ in range(5):
            stream.read(CHUNK, exception_on_overflow=False)
        frames = []
        for _ in range(int(RATE / CHUNK * seconds)):
            frames.append(stream.read(CHUNK, exception_on_overflow=False))
        stream.stop_stream()
        stream.close()
        p.terminate()

        tmp = self.tempfile.mktemp(suffix='.wav')
        with self.wave.open(tmp, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        sample_rate, data = self.wav_io.read(tmp)
        amplitude = self.np.abs(data.astype(self.np.float32)).mean()
        if amplitude < SILENCE_THRESHOLD:
            os.remove(tmp)
            return None

        data = self.np.clip(data.astype(self.np.float32) * BOOST,
                            -32768, 32767).astype(self.np.int16)
        resampled = self.sig.resample(
            data, int(len(data) * 16000 / sample_rate)
        ).astype(self.np.int16)
        self.wav_io.write(tmp, 16000, resampled)
        return tmp

    def transcribe(self, audio_file):
        result = self.model.transcribe(audio_file, language='en', fp16=False)
        os.remove(audio_file)
        return result['text'].strip()

    def start(self, on_command: Callable):
        self.running  = True
        self.callback = on_command
        threading.Thread(target=self._loop, daemon=True).start()
        print(f'VOICE MODE. Say "{self.wake_word}" to activate.')

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            tmp = self.record(3)
            if tmp is None:
                continue
            text = self.transcribe(tmp).lower()
            if not text:
                continue
            print(f'Heard: {text}')
            if self.wake_word in text:
                print('Listening for command...')
                tmp2 = self.record(5)
                if tmp2 is None:
                    print('No command heard.')
                    continue
                command = self.transcribe(tmp2)
                if command and self.callback:
                    self.callback(command)


def get_pipeline():
    if MODE == 'voice':
        return VoicePipeline()
    else:
        return TextPipeline()


if __name__ == '__main__':
    import time
    pipeline = get_pipeline()
    pipeline.start(lambda cmd: print(f'COMMAND: {cmd}'))
    while pipeline.running:
        time.sleep(0.5)