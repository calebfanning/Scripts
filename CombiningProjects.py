import os
import json
import shutil
import glob
#Make sure to change the directory
MASTER_DIR = r"C:\Users\"
PARENT_DIR = r"C:\Users\"

def get_image_mapping(qpproj_path):
    """Reads a project file to match Image Names with their random Data Folder IDs."""
    with open(qpproj_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    mapping = {}
    for entry in data.get('images', []):
        # Find the image name
        image_name = entry.get('imageName')
        if not image_name:
            image_name = entry.get('serverBuilder', {}).get('builder', {}).get('name')
            
        # Find the folder ID
        entry_id = entry.get('entryID')
        # Use 'is None' just in case QuPath ever assigns a folder the ID of 0
        if entry_id is None:
            entry_id = entry.get('id')
            
        # If both exist, link them together AND force the ID to be a string!
        if image_name and entry_id is not None:
            mapping[image_name] = str(entry_id)
            
    return mapping

def get_data_folder(project_path):
    """Checks for both uppercase 'Data' and lowercase 'data' folders."""
    if os.path.exists(os.path.join(project_path, 'Data')):
        return os.path.join(project_path, 'Data')
    return os.path.join(project_path, 'data')

def main():
    print("Starting automated file transfer...")
    master_qpproj = os.path.join(MASTER_DIR, 'project.qpproj')
    
    if not os.path.exists(master_qpproj):
        print(f"ERROR: Could not find the Master Project file at {master_qpproj}")
        return

    # Read Master Project
    master_mapping = get_image_mapping(master_qpproj)
    print(f"SUCCESS: Found {len(master_mapping)} images in the Master Project.")
    
    files_copied_count = 0
    ontology_copied = False

    # Loop through all folders inside the Individual Projects directory
    for project_folder in os.listdir(PARENT_DIR):
        proj_path = os.path.join(PARENT_DIR, project_folder)
        qpproj_file = os.path.join(proj_path, 'project.qpproj')
        
        # Skip if it's not actually a QuPath project folder
        if not os.path.exists(qpproj_file):
            continue
            
        # AUTOMATICALLY COPY THE ONTOLOGY FILE
        if not ontology_copied:
            ontology_files = glob.glob(os.path.join(proj_path, '*Ontology.json'))
            if ontology_files:
                onto_source = ontology_files[0] # Grab the first one found
                onto_dest = os.path.join(MASTER_DIR, os.path.basename(onto_source))
                shutil.copy2(onto_source, onto_dest)
                print(f"\nSUCCESS: Copied Ontology file -> {os.path.basename(onto_source)}\n")
                ontology_copied = True

        indiv_mapping = get_image_mapping(qpproj_file)
        
        # Match images and copy the ABBA files
        for img_name, indiv_id in indiv_mapping.items():
            if img_name in master_mapping:
                master_id = master_mapping[img_name]
                
                source_data_dir = os.path.join(get_data_folder(proj_path), indiv_id)
                target_data_dir = os.path.join(get_data_folder(MASTER_DIR), master_id)
                
                if os.path.exists(source_data_dir):
                    # Ensure the target folder exists
                    os.makedirs(target_data_dir, exist_ok=True)
                    
                    # Find and copy ONLY the ABBA json and zip files
                    abba_files = glob.glob(os.path.join(source_data_dir, 'ABBA*'))
                    
                    for file_path in abba_files:
                        filename = os.path.basename(file_path)
                        shutil.copy2(file_path, os.path.join(target_data_dir, filename))
                        files_copied_count += 1
                        
                    if abba_files:
                        print(f"Copied ABBA files for image: {img_name}")

    print("\n--- SCRIPT COMPLETE ---")
    print(f"Total ABBA files copied: {files_copied_count}")

if __name__ == "__main__":
    main()