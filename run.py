import concurrent.futures
import csv
import telnyx
import time
from rich.console import Console
from rich.progress import track
from rich.table import Table
import openai
import logging
from flask import Flask, request

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Set Telnyx and OpenAI API keys
telnyx.api_key = "xxxxxxxxxxxxxxx"
openai.api_key = "xxxxxxxxxxxxxxx"

# Global variables to keep track of active calls and their recordings
active_calls = {}

# Function to make a call and play a sound
def call_and_play_sound(number):
    logging.info(f"Calling {number}...")
    call = telnyx.Call.create(connection_id="xxxxxxxxxxxxxxx", to=number, from_="+xxxxxxxxxxxxxxxxx")
    active_calls[call.call_control_id] = call
    return call

# Function to transcribe the call and write the result to a TSV file.
def transcribe_call(call_control_id):
    call = active_calls[call_control_id]

    logging.info(f"Transcribing call {call.call_control_id}...")

    # Check if recording is available
    recording_url = None
    while recording_url is None:
        call = telnyx.Call.retrieve(call_control_id)
        try:
            recording_url = call.recording_url
        except telnyx.error.TelnyxError:
            time.sleep(5)

    # Download audio file
    audio_file = requests.get(recording_url, stream=True).raw

    # Transcribe audio file
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    # Write result to TSV file
    with open('results.tsv', 'a', newline='') as f_output:
        tsv_output = csv.writer(f_output, delimiter='\t')
        tsv_output.writerow([call.from_, call.to, transcript['text'], call.call_duration])

    del active_calls[call_control_id]

# Load list of numbers from a text file
def load_numbers(filename):
    with open(filename) as f:
        numbers = f.read().splitlines()
    return numbers

# Function to manage the calling process for a given number.
def process_number(number):
    call_and_play_sound(number)

# Function to manage the multi-threaded calling process.
def multi_threaded_call(numbers):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_number, numbers)

# Function to display the progress bar and table using Rich library.
def display_progress(numbers):
    console = Console()

    # Progress bar
    with console.status("[bold green]Making calls...") as status:
        for number in track(numbers, description="Calling..."):
            time.sleep(1)

    # Table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("From Number")
    table.add_column("To Number")
    table.add_column("Text")
    table.add_column("Total Call Duration")

    with open('results.tsv', 'r', newline='') as f_input:
        tsv_input = csv.reader(f_input, delimiter='\t')
        for row in tsv_input:
            table.add_row(*row)

    console.print(table)

@app.route("/webhook", methods=["POST"])
def webhook_received():
    data = request.json
    event_type = data.get('data').get('event_type')

    logging.info(f"Received {event_type} event")

    if event_type == "call.initiated":
        # Call has been initiated
        pass
    elif event_type == "call.answered":
        # Call has been answered
        call_control_id = data.get('data').get('payload').get('call_control_id')
        # Here, you can start the audio playback
        call = active_calls[call_control_id]
        call.playback_start(audio_url="https://dsc.cloud/xxxx/ritalin-xxx.mp3")
        # Start recording the call
        call.record_start(format="mp3", channels="single")
    elif event_type == "call.hangup":
        # Call has been hung up
        call_control_id = data.get('data').get('payload').get('call_control_id')
        # Here, you can transcribe the call
        if call_control_id in active_calls:
            transcribe_call(call_control_id)

    return '', 200


@app.route("/webhook/call-recording-saved", methods=["POST"])
def call_recording_saved():
    data = request.json
    call_control_id = data.get('data').get('payload').get('call_control_id')
    recording_url = data.get('data').get('payload').get('public_recording_urls').get('mp3')  # Use MP3 format

    # Check if the call exists in active_calls
    if call_control_id in active_calls:
        call = active_calls[call_control_id]

        logging.info(f"Transcribing call {call.call_control_id}...")

        # Download audio file
        audio_file = requests.get(recording_url, stream=True).raw

        # Transcribe audio file
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

        # Write result to TSV file
        with open('results.tsv', 'a', newline='') as f_output:
            tsv_output = csv.writer(f_output, delimiter='\t')
            tsv_output.writerow([call.from_, call.to, transcript['text'], call.call_duration])

        del active_calls[call_control_id]

    return '', 200

if __name__ == "__main__":
    numbers = load_numbers('/home/xxxxxxx/ritalin-worker/numbers.txt')  # Load numbers from text file
    multi_threaded_call(numbers)  # Make calls using multi-threading
    app.run(host='0.0.0.0', port=5000)
