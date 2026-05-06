import { useCurrentFrame, useVideoConfig, Audio, staticFile } from "remotion";
import type { AnalysisData } from "./types";

export const LyricsVideo: React.FC<AnalysisData> = ({
  lyrics,
  bpm,
  audio_file,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTimeMs = (frame / fps) * 1000;

  const currentSentence = lyrics.sentences.find(
    (s) => currentTimeMs >= s.start_ms && currentTimeMs <= s.end_ms
  );

  const nextSentenceIndex = lyrics.sentences.findIndex(
    (s) => currentTimeMs < s.start_ms
  );
  const nextSentence =
    nextSentenceIndex !== -1 ? lyrics.sentences[nextSentenceIndex] : null;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: "linear-gradient(135deg, #0a0a2a, #1a1a4a)",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "PingFang SC, Microsoft YaHei, sans-serif",
        color: "white",
        padding: "80px",
      }}
    >
      {/* 从 public 目录加载音频文件 */}
      {audio_file ? <Audio src={staticFile(audio_file)} /> : null}

      <div
        style={{
          fontSize: "64px",
          fontWeight: "bold",
          textShadow: "0 0 20px rgba(255, 255, 255, 0.5)",
          textAlign: "center",
          lineHeight: 1.4,
          transition: "opacity 0.3s",
        }}
      >
        {currentSentence?.text ?? "♬"}
      </div>
      {nextSentence && (
        <div
          style={{
            marginTop: "40px",
            fontSize: "32px",
            opacity: 0.4,
          }}
        >
          {nextSentence.text}
        </div>
      )}
      <div
        style={{
          position: "absolute",
          bottom: "40px",
          right: "40px",
          fontSize: "24px",
          opacity: 0.3,
        }}
      >
        BPM {bpm.detected_bpm}
      </div>
    </div>
  );
};