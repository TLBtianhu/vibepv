import { useCurrentFrame } from "remotion";
import type { ComponentMeta } from "../../types";

type Props = {
  words?: { text: string; start_ms: number; end_ms: number }[];
  highlightColor?: string;
  glowColor?: string;
  layer?: number;
};

export const KaraokeHighlight: React.FC<Props> = ({
  words = [],
  highlightColor = "#ffff00",
  glowColor,
  layer = 10,
}) => {
  const frame = useCurrentFrame();
  const currentTimeMs = (frame / 30) * 1000;

  // 找到当前正在唱的字
  const currentWords = words.filter(
    (w) => currentTimeMs >= w.start_ms && currentTimeMs <= w.end_ms
  );

  if (currentWords.length === 0) return null;

  const currentWord = currentWords[0];

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        pointerEvents: "none",
        zIndex: layer,
      }}
    >
      <span
        style={{
          fontSize: "64px",
          fontWeight: "bold",
          color: highlightColor,
          textShadow: glowColor
            ? `0 0 20px ${glowColor}, 0 0 40px ${glowColor}`
            : "0 0 20px rgba(255, 255, 0, 0.8)",
          textAlign: "center",
          lineHeight: 1.4,
          padding: "80px",
        }}
      >
        {currentWord.text}
      </span>
    </div>
  );
};

export const karaokeHighlightMeta: ComponentMeta = {
  allowedParams: ["highlightColor", "glowColor"],
  defaults: {
    highlightColor: "#ffff00",
  },
};