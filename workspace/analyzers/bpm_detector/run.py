import sys
from processor import detect_bpm

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python src/audio/bpm_detector/run.py <音频路径> <输出JSON路径>")
        sys.exit(1)
    detect_bpm(sys.argv[1], sys.argv[2])