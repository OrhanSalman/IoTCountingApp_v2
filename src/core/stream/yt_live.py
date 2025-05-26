from datetime import datetime
import re
import urllib
import yt_dlp

# https://github.com/MichaelMarav/RealTimeDetectionYoutube
# https://pypi.org/project/yt-dlp/

""" 
    Catcher for Youtube Live Streams. We can use it also as stream source for the inference.
    This is limited, because the token is only valid for some hours.
    Could use authentication with OAuth2, but this is not implemented yet.
"""

class StreamCatcher:
    def __init__(self):
        self.url = None
        self.ydl_opts = {
            'format': 'bestvideo[ext=mp4]',
        }
        self.video_url = None

        self.stream_resolution = None
        self.stream_fps = None
        self.expiration = None
        self.exp_timestamp = None

    def get_stream_values(self):
        return self.stream_resolution, self.stream_fps

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url
    
    def get_duration(self):
        return self.expiration
    
    def get_expiration(self):
        if self.expiration:
            return datetime.fromtimestamp(int(self.expiration))
        return None
    
    def get_video_url(self):
        if self.video_url and "expire" in self.video_url:
            parsed_url = urllib.parse.urlparse(self.video_url)
            match = re.search(r'/expire/(\d+)', parsed_url.path)
            expire = match.group(1) if match else None
            self.expiration = expire
            self.exp_timestamp = str(datetime.fromtimestamp(int(expire)))
            
        return self.video_url

    def get_formats(self):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
            formats = info['formats']

            video_formats = []
            for i, fmt in enumerate(formats):
                if 'acodec' not in fmt or fmt['acodec'] == 'none':
                    if 'height' in fmt:
                        if 'Premium' in fmt['format']:
                            continue
                        if '(storyboard)' in fmt['format']:
                            continue
                        video_formats.append(f"{i}: {fmt['format']} - Auflösung: {fmt['height']}p - FPS: {fmt['fps']}")
            
            return video_formats
    
    def set_quality(self, choice):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
            formats = info['formats']
    
            self.video_url = formats[choice]['url']
            self.video_url = f"{self.video_url}&low_latency=1&fast_start=1&buffer=0&latency=0&maxlatency=0"
    
            self.stream_resolution = f"{formats[choice]['height']}x{formats[choice]['width']}"
            self.stream_fps = formats[choice]['fps']
