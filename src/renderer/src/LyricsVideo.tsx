import { useCurrentFrame, useVideoConfig, Audio, staticFile } from "remotion";
import { useAudioData, visualizeAudio } from "@remotion/media-utils";
import type { VibePVProps } from "./types";

export const LyricsVideo: React.FC<VibePVProps> = ({
  lyrics,
  bpm,
  audio_file,
  visual_params,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTimeMs = (frame / fps) * 1000;

  const audioData = useAudioData(staticFile(audio_file));
  const spectrum = audioData
    ? visualizeAudio({ fps, frame, audioData, numberOfSamples: 32 })
    : null;

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
        position: "absolute",
        inset: 0,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "PingFang SC, Microsoft YaHei, sans-serif",
        color: "white",
        padding: "80px",
        zIndex: 1,
      }}
    >
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

      {spectrum && (
        <div
          style={{
            position: "absolute",
            bottom: "120px",
            left: 0,
            right: 0,
            display: "flex",
            justifyContent: "center",
            alignItems: "flex-end",
            gap: "4px",
            height: "80px",
          }}
        >
          {spectrum.map((value, index) => {
            const barColor = visual_params.color_scheme?.[1] || "#ff00ff";
            const height = Math.max(2, value * 80);
            return (
              <div
                key={index}
                style={{
                  width: "8px",
                  height: `${height}px`,
                  backgroundColor: barColor,
                  borderRadius: "4px",
                  transition: "height 0.1s ease",
                }}
              />
            );
          })}
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
        BPM {bpm.detected_bpm} | {visual_params.particle_speed}
      </div>
    </div>
  );
};