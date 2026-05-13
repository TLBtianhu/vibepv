import sys
from processor import provide

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python src/audio/audio_provider/run.py <音频路径>")
        sys.exit(1)
    provide(sys.argv[1])