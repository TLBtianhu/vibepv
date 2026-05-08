import { useCurrentFrame } from "remotion";
import { useAudioData, visualizeAudio } from "@remotion/media-utils";
import { staticFile } from "remotion";
import type { ComponentMeta } from "../../types";

type Props = {
  audioFile: string;           // 音频文件名，如 "gouqiqishi.wav"
  radius?: number;             // 频谱圆环半径，默认 300
  barCount?: number;           // 频谱条数（2的幂），默认 64
  maxHeight?: number;          // 最大弧段高度，默认 80
  color?: string;              // 频谱颜色，默认霓虹青
  opacity?: number;            // 整体透明度，默认 0.8
  layer?: number;
};

export const CircularSpectrum: React.FC<Props> = ({
  audioFile,
  radius = 300,
  barCount = 64,
  maxHeight = 80,
  color = "#00ffff",
  opacity = 0.8,
  layer = 0,
}) => {
  const frame = useCurrentFrame();

  const audioData = useAudioData(staticFile(audioFile));
  if (!audioData) return null;

  const spectrum = visualizeAudio({
    fps: 30,
    frame,
    audioData,
    numberOfSamples: barCount,
  });

  const centerX = 1920 / 2;
  const centerY = 1080 / 2;

  // 生成弧段路径
  const bars = spectrum.map((value, index) => {
    const angle = (index / barCount) * Math.PI * 2 - Math.PI / 2; // 从12点钟方向开始
    const innerR = radius;
    const outerR = radius + Math.max(2, value * maxHeight);

    const x1 = centerX + innerR * Math.cos(angle);
    const y1 = centerY + innerR * Math.sin(angle);
    const x2 = centerX + outerR * Math.cos(angle);
    const y2 = centerY + outerR * Math.sin(angle);

    return { x1, y1, x2, y2, value };
  });

  // 生成 SVG path：用相邻弧段连接成连续路径
  const pathData = bars
    .map((bar, i) => {
      const nextBar = bars[(i + 1) % bars.length];
      // 当前弧段：内圆到外圆
      const d = [
        `M ${bar.x1} ${bar.y1}`,
        `L ${bar.x2} ${bar.y2}`,
        `L ${nextBar.x2} ${nextBar.y2}`,
        `L ${nextBar.x1} ${nextBar.y1}`,
        "Z",
      ].join(" ");
      return d;
    })
    .join(" ");

  return (
    <svg
      width="1920"
      height="1080"
      viewBox="0 0 1920 1080"
      style={{
        position: "absolute",
        inset: 0,
        zIndex: layer,
        pointerEvents: "none",
      }}
    >
      <g opacity={opacity}>
        {bars.map((bar, i) => {
          const angle = (i / barCount) * Math.PI * 2 - Math.PI / 2;
          const x1 = centerX + radius * Math.cos(angle);
          const y1 = centerY + radius * Math.sin(angle);
          const x2 = centerX + (radius + Math.max(2, bar.value * maxHeight)) * Math.cos(angle);
          const y2 = centerY + (radius + Math.max(2, bar.value * maxHeight)) * Math.sin(angle);

          return (
            <line
              key={i}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke={color}
              strokeWidth={2}
              strokeLinecap="round"
              opacity={0.5 + bar.value * 0.5}
            />
          );
        })}
      </g>
    </svg>
  );
};

export const circularSpectrumMeta: ComponentMeta = {
  allowedParams: ["audioFile", "radius", "barCount", "maxHeight", "color", "opacity"],
  defaults: {
    radius: 300,
    barCount: 64,
    maxHeight: 80,
    color: "#00ffff",
    opacity: 0.8,
  },
};