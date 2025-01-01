import cv2
from pyzbar.pyzbar import decode
import os
import numpy as np
import requests

def get_final_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        return response.url
    except:
        return url

def remove_duplicates_from_file(filename):
    # Read all lines and remove duplicates while preserving order
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
        unique_lines = list(dict.fromkeys(lines))
        with open(filename, 'w') as f:
            f.writelines(unique_lines)

def read_qr_codes(image_path, folder_name):
    # Read the image
    image = cv2.imread(image_path)
    
    extracted_links_file = f"extractedlinks_{folder_name}.txt"
    
    if image is None:
        print(f"Could not read image: {image_path}")
        # Add [MISSING] placeholder for unreadable images
        with open(extracted_links_file, "a") as f:
            f.write(f"[MISSING:{image_path}]\n")
        return False
    
    # Decode QR codes
    qr_codes = decode(image)
    
    # Check if no QR codes were found
    if not qr_codes:
        print(f"No QR codes found in: {image_path}")
        # Add [MISSING] placeholder when no QR codes found
        with open(extracted_links_file, "a") as f:
            f.write(f"[MISSING:{image_path}]\n")
        return False
        
    # Process each detected QR code
    for qr_code in qr_codes:
        # Extract the data
        data = qr_code.data.decode('utf-8')
        
        # Get QR code coordinates
        points = qr_code.polygon
        if len(points) > 4:
            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
            points = hull
        
        # Draw boundary
        n = len(points)
        for j in range(n):
            cv2.line(image, tuple(points[j]), tuple(points[(j+1) % n]), (255,0,0), 2)
            
        # Put text
        cv2.putText(image, data, (points[0][0], points[0][1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
        
        print(f"QR Code detected in {image_path}: {data}")
        
        # Append link to file
        with open(extracted_links_file, "a") as f:
            f.write(data + "\n")
        
        # Remove duplicates (but preserve [MISSING] entries)
        remove_duplicates_from_file(extracted_links_file)
    
    # Display the image
    cv2.imshow("QR Code Detection", image)
    cv2.waitKey(1)  # Show image briefly
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    # Get all subfolders in current directory
    subfolders = [f for f in os.listdir('.') if os.path.isdir(f)]
    
    for folder in subfolders:
        print(f"\nProcessing folder: {folder}")
        
        # Get all image files in current subfolder
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        image_files = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(image_extensions):
                    image_files.append(os.path.join(root, file))
        
        # Sort files lexicographically
        image_files.sort()
        
        # Process each image
        failed_images = []
        for image_path in image_files:
            success = read_qr_codes(image_path, folder)
            if success:
                os.remove(image_path)
                print(f"Deleted successfully processed image: {image_path}")
            else:
                failed_images.append(image_path)
        
        if failed_images:
            print(f"\nImages that failed QR code detection in {folder}:")
            for img in failed_images:
                print(img)
        
        # After processing all images in folder, get final URLs
        extracted_links_file = f"extractedlinks_{folder}.txt"
        final_links_file = f"finallinks_{folder}.txt"
        
        if os.path.exists(extracted_links_file):
            with open(extracted_links_file, "r") as f:
                links = f.readlines()
            
            # Get final URLs after redirects
            final_links = []
            for link in links:
                link = link.strip()
                if "[MISSING:" in link:
                    final_links.append(link + "\n")  # Preserve [MISSING:image] placeholder
                else:
                    final_url = get_final_url(link)
                    final_links.append(final_url + "\n")
                print(f"Original: {link}")
                print(f"Final: {final_url if '[MISSING:' not in link else link}")
            
            # Save final links
            with open(final_links_file, "w") as f:
                f.writelines(final_links)
            
            # Remove duplicates (but preserve [MISSING] entries)
            remove_duplicates_from_file(final_links_file)
