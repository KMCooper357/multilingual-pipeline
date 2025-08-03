import os
import boto3
import time
from pathlib import Path
import requests

# Load env variables
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')  
S3_BUCKET = os.environ.get('S3_BUCKET', 'pixellearning-beta')

TARGET_LANGUAGE = 'es'  # Spanish

# Initialize AWS clients
s3 = boto3.client('s3', region_name=AWS_REGION)
transcribe = boto3.client('transcribe', region_name=AWS_REGION)
translate = boto3.client('translate', region_name=AWS_REGION)
polly = boto3.client('polly', region_name=AWS_REGION)

# Determine if we're in beta or prod
def get_env_prefix():
    ref = os.getenv('GITHUB_REF', '')
    return 'prod' if ref == 'refs/heads/main' else 'beta'

# Upload a file to S3
def upload_to_s3(file_path, s3_key):
    s3.upload_file(file_path, S3_BUCKET, s3_key)
    print(f"Uploaded to s3://{S3_BUCKET}/{s3_key}")

# Start Transcribe job
def transcribe_audio(job_name, s3_uri):
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': s3_uri},
        MediaFormat='mp3',
        LanguageCode='en-US'
    )

    print("Waiting for transcription to complete...")
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        state = status['TranscriptionJob']['TranscriptionJobStatus']
        if state in ['COMPLETED', 'FAILED']:
            break
        time.sleep(5)

    if state == 'FAILED':
        raise Exception("Transcription failed.")

    transcript_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
    return transcript_url

# Download and extract text from transcript
def get_transcript_text(transcript_url):
    response = requests.get(transcript_url)
    return response.json()['results']['transcripts'][0]['transcript']

# Translate English to target language
def translate_text(text, target_language):
    result = translate.translate_text(Text=text, SourceLanguageCode='en', TargetLanguageCode=target_language)
    return result['TranslatedText']

# Synthesize translated speech with Polly
def synthesize_speech(text, lang_code, output_path):
    voice_id = 'Lucia' if lang_code == 'es' else 'Joanna'  # Adjust as needed
    response = polly.synthesize_speech(Text=text, OutputFormat='mp3', VoiceId=voice_id)
    with open(output_path, 'wb') as f:
        f.write(response['AudioStream'].read())

def main():
    prefix = get_env_prefix()
    audio_folder = Path("audio_inputs")
    for file in audio_folder.glob("*.mp3"):
        base_name = file.stem
        s3_input_key = f"{prefix}/audio_inputs/{file.name}"
        upload_to_s3(str(file), s3_input_key)

        s3_uri = f"s3://{S3_BUCKET}/{s3_input_key}"
        job_name = f"{prefix}-{base_name}-{int(time.time())}".replace('_', '-')
        transcript_url = transcribe_audio(job_name, s3_uri)
        transcript = get_transcript_text(transcript_url)

        

        # Upload transcript
        transcript_key = f"{prefix}/transcripts/{base_name}.txt"
        s3.put_object(Bucket=S3_BUCKET, Key=transcript_key, Body=transcript.encode('utf-8'))
        print(f"Uploaded transcript: {transcript_key}")

        # Translate
        translated_text = translate_text(transcript, TARGET_LANGUAGE)
        translation_key = f"{prefix}/translations/{base_name}_{TARGET_LANGUAGE}.txt"
        s3.put_object(Bucket=S3_BUCKET, Key=translation_key, Body=translated_text.encode('utf-8'))
        print(f"Uploaded translation: {translation_key}")

        # Synthesize and upload audio
        local_audio_file = f"{base_name}_{TARGET_LANGUAGE}.mp3"
        synthesize_speech(translated_text, TARGET_LANGUAGE, local_audio_file)
        audio_output_key = f"{prefix}/audio_outputs/{local_audio_file}"
        upload_to_s3(local_audio_file, audio_output_key)

if __name__ == "__main__":
    main()