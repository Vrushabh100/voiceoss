import pyaudio
p = pyaudio.PyAudio()

print("=== ALL INPUT DEVICES ===")
for i in range(p.get_device_count()):
    d = p.get_device_info_by_index(i)
    if d['maxInputChannels'] > 0:
        print(f"Index {i}: {d['name']}")
        print(f"         Channels: {d['maxInputChannels']}")
        print(f"         Default SR: {int(d['defaultSampleRate'])}")
        print()

print(f"System default input index: {p.get_default_input_device_info()['index']}")
print(f"System default input name:  {p.get_default_input_device_info()['name']}")
p.terminate()