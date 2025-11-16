import argparse
from .commands import find_duplicates

def main():
    parser = argparse.ArgumentParser(
        description="Find duplicate images within a directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find all duplicates in photos/ folder
  python -m yourpackage.main --dir photos/
  
  # Use stricter matching (95% similarity required)
  python -m yourpackage.main --dir photos/ --threshold 95
  
  # More lenient pixel tolerance
  python -m yourpackage.main --dir photos/ --tolerance 20
        """
    )

    parser.add_argument(
        "--dir",
        required=True,
        help="Directory containing images to scan for duplicates"
    )

    parser.add_argument(
        "--threshold",
        type=int,
        default=95,
        help="Minimum similarity percentage to consider duplicates (0-100, default: 95)"
    )

    parser.add_argument(
        "--hash-distance",
        type=int,
        default=5,
        help="Maximum hash distance for initial filtering (default: 5, lower=stricter)"
    )

    parser.add_argument(
        "--size",
        type=int,
        default=64,
        help="Resize dimension for comparison (NxN, default: 64x64)"
    )

    parser.add_argument(
        "--tolerance",
        type=int,
        default=10,
        help="Pixel grayscale tolerance (0-255, default: 10, lower=stricter)"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed progress information"
    )

    args = parser.parse_args()

    # Validate inputs
    if args.threshold < 0 or args.threshold > 100:
        parser.error("Threshold must be between 0 and 100")
    
    if args.tolerance < 0 or args.tolerance > 255:
        parser.error("Tolerance must be between 0 and 255")
    
    if args.size < 8 or args.size > 512:
        parser.error("Size must be between 8 and 512")
    
    if args.hash_distance < 0 or args.hash_distance > 64:
        parser.error("Hash distance must be between 0 and 64")

    find_duplicates(
        directory=args.dir,
        threshold=args.threshold,
        hash_distance=args.hash_distance,
        size=args.size,
        tolerance=args.tolerance,
        verbose=args.verbose
    )

if __name__ == "__main__":
    main()
