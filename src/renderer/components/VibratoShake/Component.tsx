import { useCurrentFrame } from "remotion";
import type { ComponentMeta } from "../../src/app/types";

type Props = {
  intensity?: number;
  frequency?: number;
  direction?: "both" | "horizontal" | "vertical";
  layer?: number;
  children?: React.ReactNode;
};

export const VibratoShake: React.FC<Props> = ({
  intensity = 10,
  frequency = 8,
  direction = "both",
  layer = 10,
  children,
}) => {
  const frame = useCurrentFrame();
  const t = frame / 30;

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
        zIndex: layer,
      }}
    >
      {children}
    </div>
  );
};

export const vibratoShakeMeta: ComponentMeta = {
  allowedParams: ["intensity", "frequency", "direction"],
  defaults: {
    intensity: 10,
    frequency: 8,
    direction: "both",
  },
  renderMode: "wrapper",  // 关键：声明为包裹模式
};