from yt_dlp.postprocessor.common import PostProcessor
from dotenv import load_dotenv
import yt_dlp, os, re, json, urllib.request, sys, time, zipfile

load_dotenv()

songs = []

PATH = os.getenv('DOWNLOAD_PATH')
ORIGINAL_PATH = os.getcwd()

FIRST = 'https://www.youtube.com/results?search_query='
SECOND = 'https://www.youtube.com/watch?v='

def search(key):
    key = key.replace(' ', '+')
    
    print(f'[i] Searching for: "{key}"...')

    count = 0
    top = []
    url = FIRST + key
    html = urllib.request.urlopen(url)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    
    return SECOND + video_ids[0]

class MyCustomPP(PostProcessor):
        def run(self, info):
            self.to_screen('Doing stuff')
            return [], info

def download(link):
    
    os.chdir(PATH)

    def my_hook(d):
        if d['status'] == 'finished':
            print('Done downloading, now converting ...')

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'progress_hooks': [my_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.add_post_processor(MyCustomPP())
        info = ydl.extract_info(link)

    os.chdir(ORIGINAL_PATH)

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))

with open('songs.txt', 'r') as f:
    for i in f.readlines():
        if i.strip() in songs:
            pass
        else:
            songs.append(i.strip())

for title in songs:
    link = search(title)
    print(f'[i] Downloading "{link}"...')
    download(link)
      
print('Zipping songs and saving to: "{os.getcwd()}/{songs.zip}"')

zipf = zipfile.ZipFile('songs.zip', 'w', zipfile.ZIP_DEFLATED)
zipdir(PATH, zipf)
zipf.close()