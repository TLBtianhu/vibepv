import sys
from processor import align

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python src/audio/lyrics_aligner/run.py <音频路径> <输出JSON路径>")
        sys.exit(1)
    align(sys.argv[1], sys.argv[2])