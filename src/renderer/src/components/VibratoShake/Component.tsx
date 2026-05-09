import { useCurrentFrame } from "remotion";
import type { ComponentMeta } from "../../types";

type Props = {
  intensity?: number;    // 震动强度（像素），默认 10
  frequency?: number;    // 震动频率（Hz），默认 8
  direction?: "both" | "horizontal" | "vertical";  // 震动方向，默认 both
  layer?: number;
};

export const VibratoShake: React.FC<Props> = ({
  intensity = 10,
  frequency = 8,
  direction = "both",
  layer = 10,
}) => {
  const frame = useCurrentFrame();
  const t = frame / 30; // 秒

  const offsetX =
    direction === "vertical" ? 0 : Math.sin(t * frequency * Math.PI * 2) * intensity;
  const offsetY =
    direction === "horizontal" ? 0 : Math.cos(t * frequency * Math.PI * 2 + 0.5) * intensity * 0.7;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        transform: `translate(${offsetX}px, ${offsetY}px)`,
        pointerEvents: "none",
        zIndex: layer,
      }}
    />
  );
};

export const vibratoShakeMeta: ComponentMeta = {
  allowedParams: ["intensity", "frequency", "direction"],
  defaults: {
    intensity: 10,
    frequency: 8,
    direction: "both",
  },
};