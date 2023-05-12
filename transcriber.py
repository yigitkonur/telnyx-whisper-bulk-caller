import os
import openai
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress

# Ensure to set OPENAI_API_KEY environment variable as per OpenAI Python client setup
openai.api_key = 'sk-xxxxxxxxxx'

# Specify the directory
directory = 'xxxxxxxxxxxxxx'

# Define the function to transcribe audio with exponential backoff
def transcribe_audio(filename):
    if filename.endswith('.mp3') or filename.endswith('.mp4') or filename.endswith('.mpeg') or filename.endswith('.mpga') or filename.endswith('.m4a') or filename.endswith('.wav') or filename.endswith('.webm'):
        file_path = os.path.join(directory, filename)
        retries = 0
        while retries < 10:
            try:
                # Transcribe audio
                with open(file_path, 'rb') as audio_file:
                    transcript = openai.Audio.transcribe("whisper-1", audio_file)
                    return (filename, transcript["text"])
            except Exception as e:
                print(f"An error occurred while processing file {filename}: {str(e)}")
                retries += 1
                time.sleep(10 * 2 ** retries)
        return None

# Prepare list of audio files
audio_files = [f for f in os.listdir(directory) if f.endswith(('.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'))]

# Create TSV file
with open('transcriptions.tsv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(["filename", "transcription_of_text"])

    # Create a progress bar
    progress = Progress("[progress.description]{task.description}", "[progress.percentage]{task.percentage:>3.0f}%")

    # Add a task to track progress
    task = progress.add_task("[cyan]Transcribing...", total=len(audio_files))

    # Use ThreadPoolExecutor to transcribe audio files concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(transcribe_audio, f): f for f in audio_files}

        with progress:
            for future in as_completed(futures):
                res = future.result()
                if res is not None:
                    writer.writerow(res)
                    progress.update(task, advance=1)
