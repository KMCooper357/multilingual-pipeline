# multilingual-pipeline

# multilingual-pipeline

##  Background

**Pixel Learning Co.** is a digital-first education startup committed to **accessibility** and **language inclusion**. Their team regularly uploads `.mp3` audio files with educational content and needs to:

- Transcribe speech
- Translate into multiple languages
- Regenerate speech in those languages

To make this efficient and repeatable, they want to automate the full process using **GitHub Actions** and **AWS AI services**.

---

##  Objective

This project builds a fully automated, serverless pipeline using **Amazon Transcribe**, **Translate**, **Polly**, **S3**, and **GitHub Actions**.

###  Goals:
- **Transcribe** `.mp3` files using Amazon Transcribe
- **Translate** transcripts into a target language (e.g., Spanish, French)
- **Regenerate** speech using Amazon Polly
- **Store** all outputs in a structured S3 bucket layout

---

##  Why These AWS Services?

| Service     | Purpose                                                             |
|-------------|---------------------------------------------------------------------|
| Transcribe  | Converts spoken English to text (speech-to-text)                   |
| Translate   | Translates transcripts to supported target languages               |
| Polly       | Converts translated text into natural-sounding speech (text-to-speech) |
| S3          | Centralized storage of input and output artifacts                  |

All services are fully managed, scalable, and require **no custom ML model training**.

---

##  Why GitHub Actions?

-  **CI/CD Automation**: Automatically triggers workflows on PRs and merges
-  **Environment Awareness**: Uses `beta/` or `prod/` S3 prefixes based on GitHub event type
-  **Secure Credential Handling**: All AWS credentials stored in **GitHub Secrets**

---

##  Folder Structure (S3)

```text
your-bucket/
├── beta/
│   ├── transcripts/
│   ├── translations/
├── prod/
│   ├── audio/
│   ├── audio_outputs/
 How It Works
Developer pushes an .mp3 file to audio_inputs/ in the GitHub repo

GitHub Actions runs either on_pull_request.yml or on_merge.yml:

Uploads the audio file to prod/audio/

Starts a Transcribe job

Saves transcript to beta/transcripts/

Translates the transcript (e.g., to Spanish)

Uploads translation to beta/translations/

Uses Polly to generate new multilingual .mp3

Uploads it to prod/audio_outputs/

 GitHub Secrets Required
Secret Name	Description
AWS_ACCESS_KEY_ID	Your IAM user access key
AWS_SECRET_ACCESS_KEY	Your IAM user secret key
AWS_REGION	AWS region (e.g., us-east-1)
S3_BUCKET_BETA	Name of your S3 bucket for beta outputs
S3_BUCKET_PROD	Name of your S3 bucket for prod outputs
FILENAME	Base name of the audio file (no extension)
SOURCE_LANG	Source language code (e.g., en-US)
TRANSLATE_LANG	Target language code (e.g., es)
POLLY_VOICE	Polly voice ID (e.g., Lupe for Spanish)

Local Testing Instructions
bash
Copy
Edit
python process_audio.py
Ensure your .env file includes the following:

env
Copy
Edit
AWS_ACCESS_KEY_ID=YOUR_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET
AWS_REGION=us-east-1
S3_BUCKET_BETA=your-bucket-name
S3_BUCKET_PROD=your-bucket-name
FILENAME=your-audio-filename
SOURCE_LANG=en-US
TRANSLATE_LANG=es
POLLY_VOICE=Lupe
Sample Workflow Trigger (on_pull_request.yml)
yaml
Copy
Edit
on:
  pull_request:
    branches:
      - main
jobs:
  audio_pipeline:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: pip install boto3 python-dotenv

      - name: Run audio processing
        run: python process_audio.py
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: ${{ secrets.AWS_REGION }}
          S3_BUCKET_BETA: ${{ secrets.S3_BUCKET_BETA }}
          S3_BUCKET_PROD: ${{ secrets.S3_BUCKET_PROD }}
          FILENAME: ${{ secrets.FILENAME }}
          SOURCE_LANG: ${{ secrets.SOURCE_LANG }}
          TRANSLATE_LANG: ${{ secrets.TRANSLATE_LANG }}
          POLLY_VOICE: ${{ secrets.POLLY_VOICE }}
 Verification
After your PR or merge, go to your S3 console and verify:

Transcript in beta/transcripts/

Translation in beta/translations/

Audio output in prod/audio_outputs/
