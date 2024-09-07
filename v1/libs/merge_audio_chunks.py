import wave
import base64
import io
import struct
import numpy as np

def merge_audio_buffers(audio_buffers):
    # Convert base64 strings to wave objects
    wave_files = []
    for base64_audio in audio_buffers:
        buffer = base64.b64decode(base64_audio)
        wave_file = wave.open(io.BytesIO(buffer), 'rb')
        wave_files.append(wave_file)

    # Ensure all audio files have the same format
    first_wave = wave_files[0]
    format_params = first_wave.getparams()
    if not all(wav.getparams() == format_params for wav in wave_files):
        raise ValueError("All audio chunks must have the same format")

    # Calculate total number of frames
    total_frames = sum(wav.getnframes() for wav in wave_files)

    # Create a new wave file with the merged frames
    merged_wave = wave.open(io.BytesIO(), 'wb')
    merged_wave.setparams(format_params)

    # Copy frames from each wave file into the merged file
    for wav in wave_files:
        merged_wave.writeframes(wav.readframes(wav.getnframes()))
        wav.close()

    # Get the merged audio data as bytes
    merged_wave.seek(0)
    merged_audio_bytes = merged_wave.readframes(total_frames)
    merged_wave.close()

    # Convert merged audio to base64
    merged_base64 = base64.b64encode(merged_audio_bytes).decode('utf-8')

    return merged_base64