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
    missing_videos = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('[MISSING:'):
                    missing_videos.append(line)
                elif line:
                    if line.startswith('https://www.youtube.com'):
                        video_id = extract_video_id(line)
                        if video_id:
                            video_ids.append(video_id)
                    else:
                        missing_videos.append(f"[MISSING: Non-Redireting URL - {line}]")
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
    return video_ids, missing_videos

def main():
    # Create markdown file
    with open('README.md', 'w', encoding='utf-8') as md_file:
        md_file.write("# Course Playlists\n\n")
        
        # Get all directories starting with numbers
        base_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and any(d.startswith(f'{i:02d}.') for i in range(1, 11))]
        base_dirs.sort()
        
        all_missing_videos = []  # Store all missing videos
        
        # Process each main directory
        for base_dir in base_dirs:
            # Extract chapter number and name
            chapter_num = base_dir.split('.')[0]
            chapter_name = base_dir.split('. ', 1)[1] if '. ' in base_dir else base_dir
            md_file.write(f"## {chapter_num}. {chapter_name}\n\n")
            
            # Get all txt files in the directory
            txt_files = [f for f in os.listdir(base_dir) if f.endswith('.txt')]
            txt_files.sort()
            
            # Process each txt file
            for txt_file in txt_files:
                file_path = os.path.join(base_dir, txt_file)
                topic_name = os.path.splitext(txt_file)[0]
                
                # Get video IDs and create playlist
                video_ids, missing_videos = process_txt_file(file_path)
                if video_ids:
                    playlist_url = create_playlist_url(video_ids)
                    md_file.write(f"### [{topic_name}]({playlist_url})\n\n")
                    if missing_videos:
                        # Store missing videos with topic info
                        all_missing_videos.append((topic_name, missing_videos))

        # Write all missing videos at the end
        for topic_name, missing_videos in all_missing_videos:
            md_file.write(f"Missing videos for {topic_name}:\n")
            for missing in missing_videos:
                md_file.write(f"- {missing}\n")
            md_file.write("\n")

if __name__ == "__main__":
    main()