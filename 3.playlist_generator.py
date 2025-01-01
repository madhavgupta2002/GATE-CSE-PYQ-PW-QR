import os
import re

def extract_video_id(url):
    # Extract video ID from YouTube URL
    pattern = r'(?:v=|/)([0-9A-Za-z_-]{11})(?:[&?]|$)'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def create_playlist_url(video_ids):
    # Create a YouTube playlist URL from video IDs
    return f"https://www.youtube.com/watch_videos?video_ids={','.join(video_ids)}"

def process_txt_file(file_path):
    video_ids = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    video_id = extract_video_id(line)
                    if video_id:
                        video_ids.append(video_id)
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
    return video_ids

def main():
    # Create markdown file
    with open('playlists.md', 'w', encoding='utf-8') as md_file:
        md_file.write("# Course Playlists\n\n")
        
        # Get all directories starting with numbers
        base_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and (d.startswith('1.') or d.startswith('2.'))]
        base_dirs.sort()
        
        # Process each main directory
        for base_dir in base_dirs:
            # Write chapter heading
            chapter_name = base_dir.split('. ', 1)[1] if '. ' in base_dir else base_dir
            md_file.write(f"## {chapter_name}\n\n")
            
            # Get all txt files in the directory
            txt_files = [f for f in os.listdir(base_dir) if f.endswith('.txt')]
            txt_files.sort()
            
            # Process each txt file
            for txt_file in txt_files:
                file_path = os.path.join(base_dir, txt_file)
                topic_name = os.path.splitext(txt_file)[0]
                
                # Get video IDs and create playlist
                video_ids = process_txt_file(file_path)
                if video_ids:
                    playlist_url = create_playlist_url(video_ids)
                    md_file.write(f"### {topic_name}\n")
                    md_file.write(f"[Watch Playlist]({playlist_url})\n\n")

if __name__ == "__main__":
    main() 