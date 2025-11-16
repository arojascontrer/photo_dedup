from pathlib import Path
from PIL import Image
from dedupe.indexer import build_index, load_image
from dedupe.comparer import deep_similarity

def find_duplicates(directory, threshold=95, hash_distance=5, size=64, tolerance=10, verbose=False):
    """
    Find all duplicate images within a directory.
    
    Args:
        directory: Path to folder containing images to search
        threshold: Similarity percentage threshold (0-100)
        hash_distance: Maximum hamming distance for hash-based filtering
        size: Size to resize images for comparison (NxN)
        tolerance: Grayscale pixel tolerance (0-255)
        verbose: Show detailed progress
    """
    if verbose:
        print(f"Scanning directory: {directory}")
    
    index, tree, records = build_index(directory, verbose=verbose)
    
    if len(records) == 0:
        print("No images found in directory.")
        return
    
    if verbose:
        print(f"\nSearching for duplicates (threshold: {threshold}%, tolerance: {tolerance})...")
    
    duplicate_groups = []
    processed = set()
    comparison_size = (size, size)
    
    for i, record in enumerate(records):
        if record.path in processed:
            continue
        
        if verbose and (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(records)} images...")
        
        candidates = tree.search(record.hash, threshold=hash_distance)
        
        img1 = load_image(record.path)
        if img1 is None:
            continue
        
        group = []
        
        for candidate in candidates:
            if candidate.path == record.path or candidate.path in processed:
                continue
            
            img2 = load_image(candidate.path)
            if img2 is None:
                continue
            
            similarity = deep_similarity(
                img1, 
                img2, 
                size=comparison_size, 
                tolerance=tolerance
            )
            
            img2.close()
            
            if similarity >= threshold:
                if not group:
                    group.append((record.path, 100.0))
                group.append((candidate.path, similarity))
                processed.add(candidate.path)
        
        img1.close()
        
        if group:
            processed.add(record.path)
            duplicate_groups.append(group)
    
    print("\n" + "="*70)
    if duplicate_groups:
        print(f"Found {len(duplicate_groups)} duplicate group(s):\n")
        
        for idx, group in enumerate(duplicate_groups, 1):
            print(f"Group {idx} ({len(group)} images):")
            for path, similarity in group:
                print(f"  [{similarity:5.2f}%] {path}")
            print()
    else:
        print("No duplicates found.")
    print("="*70)
