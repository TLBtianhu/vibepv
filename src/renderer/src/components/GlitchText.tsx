import { useCurrentFrame, interpolate } from "remotion";
import type { ComponentMeta } from "../componentRegistry";

type Props = {
  intensity?: number;    // 故障强度 0~1，默认 0.5
  color?: string;        // 故障色条颜色，默认霓虹粉
  layer?: number;
};

export const GlitchText: React.FC<Props> = ({
  intensity = 0.5,
  color = "#ff00ff",
  layer = 1,
}) => {
  const frame = useCurrentFrame();

  // 故障撕裂：clip-path 在垂直方向随机偏移
  const clipOffset1 = interpolate(
    Math.sin(frame * 0.3) * intensity,
    [-1, 1],
    [-8, 8]
  );
  const clipOffset2 = interpolate(
    Math.cos(frame * 0.37) * intensity,
    [-1, 1],
    [-6, 6]
  );

  // RGB 通道分离偏移
  const rgbShift = interpolate(
    Math.sin(frame * 0.25) * intensity,
    [-1, 1],
    [-3, 3]
  );

  // 随机闪烁：故障色块随机出现
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
      {/* 红色通道偏移 */}
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

      {/* 蓝色通道偏移 */}
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

      {/* 故障色块 */}
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
};