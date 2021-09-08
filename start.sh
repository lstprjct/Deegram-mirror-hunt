pip3 -qq install --upgrade yt-dlp
gunicorn wserver:start_server --bind 0.0.0.0:$PORT --worker-class aiohttp.GunicornWebWorker & ./aria.sh; python3 -m bot 
