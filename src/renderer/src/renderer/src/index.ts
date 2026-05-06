import { Composition } from "remotion";
import { LyricsVideo } from "./LyricsVideo";
import type { AnalysisData } from "./types";

export const Root: React.FC = () => {
  return (
    <Composition
      id="SongLyrics"
      component={LyricsVideo}
      durationInFrames={30 * 180}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        lyrics: { words: [], sentences: [] },
        bpm: { detected_bpm: 120, model: "", manual_override: false },
        merge_multiplier: 0.672,
      }}
    />
  );
};
