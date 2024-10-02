Watches a file (generally a squid access.log) for youtube urls. Downloads subtitles (requires yt-dlp). Creates a running wordcloud of videos watched. 

![Example output](https://github.com/poptix/squid-youtube-wordcloud/blob/main/wordcloud.png?raw=true)

```
python3 -m venv wc
pip install -r requirements.txt
python3 -m spacy download en_core_web_sm
python3 wc.py
```
