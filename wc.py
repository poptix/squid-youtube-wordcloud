#! python3
import re
import subprocess
import sys
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import spacy
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# Configuration
LOG_FILE_PATH = '/home/poptix/git/wordcloud/access.log'  # Update to your Squid log path, if you're testing, use the *FULL PATH*
SUBTITLE_DIR = './subtitles'                 # Directory to save subtitles
WORDCLOUD_IMAGE = 'wordcloud.png'
YOUTUBE_URL_REGEX = re.compile(r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})')

# Initialize spaCy
nlp = spacy.load('en_core_web_sm')

# Ensure subtitle directory exists
os.makedirs(SUBTITLE_DIR, exist_ok=True)

# Track processed URLs
processed_urls = set()

class YouTubeLogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path != LOG_FILE_PATH:
            return
        with open(LOG_FILE_PATH, 'r') as log_file:
            for line in log_file:
                match = YOUTUBE_URL_REGEX.search(line)
                if match:
                    url = match.group(0)
                    if url not in processed_urls:
                        processed_urls.add(url)
                        download_subtitles(url)

def download_subtitles(url):
    args = [
        'yt-dlp',
        '--skip-download',
        '--write-auto-subs',
        '--write-subs',
        '--sub-lang', 'en',
        '--convert-subs', 'srt',
        '--sub-format', 'srt',
        '-o', os.path.join(SUBTITLE_DIR, '%(id)s.%(ext)s'),
        url
    ]
    try:
        subprocess.run(args, check=True)
        print(f"Downloaded subtitles for: {url}")
        generate_wordcloud()
    except subprocess.CalledProcessError as e:
        print(f"Failed to download subtitles for {url}: {e}")

def extract_text_from_srt(srt_path):
    text = []
    with open(srt_path, 'r', encoding='utf-8') as file:
        for line in file:
            if not line.strip().isdigit() and '-->' not in line:
                text.append(line.strip())
    return ' '.join(text)

def extract_nouns_verbs(text):
    doc = nlp(text)
    words = [token.lemma_.lower() for token in doc if token.pos_ in {'NOUN', 'VERB'} and not token.is_stop and token.is_alpha]
    return ' '.join(words)

def generate_wordcloud():
    all_words = ''
    for filename in os.listdir(SUBTITLE_DIR):
        if filename.endswith('.srt'):
            srt_path = os.path.join(SUBTITLE_DIR, filename)
            text = extract_text_from_srt(srt_path)
            words = extract_nouns_verbs(text)
            all_words += words + ' '
    if not all_words.strip():
        print("No words extracted for word cloud.")
        return
    stop_words = set(STOPWORDS)
    wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=stop_words).generate(all_words)
    plt.figure(figsize=(15, 7.5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(WORDCLOUD_IMAGE)
    plt.close()
    print(f"Word cloud generated and saved as {WORDCLOUD_IMAGE}")

def main():
    event_handler = YouTubeLogHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(LOG_FILE_PATH) or '.', recursive=False)
    observer.start()
    print(f"Watching {LOG_FILE_PATH} for YouTube URLs...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()

