import os
import yt_dlp

def download_videos_from_file(txt_file):
    # Create folder with same name as txt file (without extension)
    folder_name = os.path.splitext(txt_file)[0]
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Read URLs from txt file
    with open(txt_file, 'r') as f:
        urls = f.readlines()

    # Filter out [MISSING] entries and clean URLs
    urls = [url.strip() for url in urls if not url.startswith('[MISSING:')]

    # Create failed downloads log file
    failed_downloads_file = os.path.join(folder_name, 'failed_downloads.txt')

    # Configure yt-dlp options
    ydl_opts = {
        'outtmpl': os.path.join(folder_name, '%(autonumber)s. %(title)s [%(id)s].%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'format': 'bv*+ba/b',  # Best video + best audio
        'format_sort': ['res:1080', 'ext:mp4:m4a'],  # Prefer 1080p MP4 with M4A audio
        'merge_output_format': 'mp4',  # Merge into MP4 container
        'postprocessor_args': [
            'FFmpegMerger', '-c:v copy -c:a aac'  # Use ffmpeg with copy codecs
        ],
        'autonumber_start': 1
    }

    # Download each video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            try:
                print(f"Downloading: {url}")
                ydl.download([url])
            except Exception as e:
                print(f"Error downloading {url}: {str(e)}")
                # Log failed download
                with open(failed_downloads_file, 'a') as f:
                    f.write(f"{url} - Error: {str(e)}\n")

def main():
    # Get all txt files in current directory
    txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]
    
    for txt_file in txt_files:
        print(f"\nProcessing file: {txt_file}")
        download_videos_from_file(txt_file)

if __name__ == "__main__":
    main()
