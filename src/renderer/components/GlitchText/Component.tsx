import { useCurrentFrame } from "remotion";
import { useMemo } from "react";
import type { ComponentMeta, BPMData, WordTimestamp } from "../../src/app/types";
import { mergeWordsToSentences } from "../../core/mergeSentences";

type Props = {
  intensity?: number;
  color?: string;
  layer?: number;
  lyrics?: { words: WordTimestamp[] } | null;
  bpm?: BPMData | null;
};

export const GlitchText: React.FC<Props> = ({
  intensity = 0.5,
  color = "#ff00ff",
  layer = 1,
  lyrics,
  bpm,
}) => {
  const frame = useCurrentFrame();
  const currentTimeMs = (frame / 30) * 1000;

  const sentences = useMemo(() => {
    const words = lyrics?.words ?? [];
    const bpmValue = bpm?.detected_bpm;
    if (!bpmValue || words.length === 0) return [];
    return mergeWordsToSentences(words, bpmValue);
  }, [lyrics, bpm]);

  const isInLyrics = sentences.some(
    (s) => currentTimeMs >= s.start_ms && currentTimeMs <= s.end_ms
  );

  if (!isInLyrics) return null;

  const clipOffset1 = (Math.sin(frame * 0.3) * intensity) * 8;
  const clipOffset2 = (Math.cos(frame * 0.37) * intensity) * 6;
  const rgbShift = (Math.sin(frame * 0.25) * intensity) * 3;

  const glitchBlockOpacity =
    Math.sin(frame * 0.7) > 0.85 && Math.random() > 0.3 ? 0.3 : 0;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        pointerEvents: "none",
        zIndex: layer,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          color: "#ff0000",
          opacity: intensity * 0.4,
          transform: `translateX(${rgbShift}px)`,
          mixBlendMode: "screen",
          clipPath: `inset(${40 + clipOffset1}% 0 ${40 - clipOffset1}% 0)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          color: "#0000ff",
          opacity: intensity * 0.4,
          transform: `translateX(${-rgbShift}px)`,
          mixBlendMode: "screen",
          clipPath: `inset(${45 + clipOffset2}% 0 ${35 - clipOffset2}% 0)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: `${30 + clipOffset1 * 2}%`,
          left: `${10 + rgbShift * 3}%`,
          width: `${60 + Math.random() * 20}%`,
          height: "4px",
          backgroundColor: color,
          opacity: glitchBlockOpacity,
          transition: "opacity 0.05s",
        }}
      />
    </div>
  );
};

export const glitchTextMeta: ComponentMeta = {
  allowedParams: ["intensity", "color"],
  defaults: { intensity: 0.5, color: "#ff00ff" },
  renderMode: "overlay",
  requiresData: ["lyrics.words", "bpm"],
};