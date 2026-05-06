import { Composition } from "remotion";
import { LyricsVideo } from "./LyricsVideo";
import type { AnalysisData } from "./types";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="SongLyrics"
      component={LyricsVideo}
      durationInFrames={1}
      fps={30}
      width={1920}
      height={1080}
      // 1. 将完整的默认 Props 内联在此，确保类型严格匹配
      defaultProps={{
        lyrics: { words: [], sentences: [] },
        bpm: { detected_bpm: 120, model: "", manual_override: false },
        merge_multiplier: 0.672,
        audio_duration_ms: 0,
      }}
      // 2. 根据音频时长精确计算总帧数
      calculateMetadata={({ props }) => {
        const totalFrames = Math.ceil(
          ((props as AnalysisData).audio_duration_ms / 1000) * 30
        );
        return {
          durationInFrames: totalFrames > 0 ? totalFrames : 1,
          props,
        };
      }}
    />
  );
};