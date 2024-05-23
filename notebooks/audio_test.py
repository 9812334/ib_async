import pyaudio
import numpy as np

def play_chime(frequency, duration, volume):
    # Set the sample rate
    sample_rate = 44100

    # Generate the audio data
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    note = np.sin(frequency * np.pi * t)

    # Scale the audio data
    audio = volume * (note * 32767).astype(np.int16)

    # Open the audio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, output=True)

    # Write the audio data to the stream
    stream.write(audio.tobytes())

    # Close the audio stream
    stream.stop_stream()
    stream.close()
    p.terminate()

# Example usage:
play_chime(1440, 0.01, 0.05)  # Play a 440 Hz note for 1 second at 50% volume