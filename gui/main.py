from pathlib import Path
from PIL import Image
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from dedupe.indexer import build_index, load_image
from dedupe.comparer import deep_similarity

def find_duplicates_for_gui(
    directory,
    threshold=95,
    hash_distance=5,
    size=64,
    tolerance=10,
    verbose=False,
    progress_callback=None,
    use_deep_comparison=True
):

    try:
        index, tree, records = build_index(directory, verbose=verbose)
    except Exception as e:
        
        if verbose:
            print(f"Error building index: {e}")
        return []
    
    if len(records) == 0:
        return []

    duplicate_groups = []
    processed = set()
    comparison_size = (size, size)
    
    for i, record in enumerate(records):
        if record.path in processed:
            continue
        
        try:
            candidates = tree.search(record.hash, threshold=hash_distance)
        except Exception as e:
            if verbose:
                print(f"Error searching candidates for {record.path}: {e}")
            continue
        
        if use_deep_comparison:
            img1 = load_image(record.path)
            if img1 is None:
                continue
            
            try:
                group = []
            
                for candidate in candidates:
                    if candidate.path == record.path or candidate.path in processed:
                        continue
                
                    try:
                        img2 = load_image(candidate.path)
                        if img2 is None:
                            continue
                    
                        try:
                            similarity = deep_similarity(
                                img1,
                                img2,
                                size=comparison_size,
                                tolerance=tolerance
                            )
                    
                            if similarity >= threshold:
                                if not group:
                                    group.append((record.path, 100.0))
                                group.append((candidate.path, similarity))
                                processed.add(candidate.path)

                        finally:
                            img2.close()
                
                    except Exception as e:
                        if verbose:
                            print(f"Error comparing {candidate.path}: {e}")
                        continue
            
                if group:
                    processed.add(record.path)
                    duplicate_groups.append(group)

            finally:
                img1.close()
        
        else:
            group = []
            
            for candidate in candidates:
                if candidate.path == record.path or candidate.path in processed:
                    continue
                
                if not group:
                    group.append((record.path, 100.0))
                group.append((candidate.path, 95.0))
                processed.add(candidate.path)
            
            if group:
                processed.add(record.path)
                duplicate_groups.append(group)

    return duplicate_groups
