import React from "react";
import type { ComponentMeta } from "../../src/app/types";

type Props = {
  glowColor?: string;      // 发光颜色，默认霓虹粉
  glowIntensity?: number;  // 发光强度 0~1，默认 0.8
  glowRadius?: number;     // 发光半径（像素），默认 40
  pulseSpeed?: number;     // 脉冲速度 0~2，0 为不脉冲，默认 0
  layer?: number;
};

export const NeonGlow: React.FC<Props> = ({
  glowColor = "#ff00ff",
  glowIntensity = 0.8,
  glowRadius = 40,
  pulseSpeed = 0,
  layer = 10,
}) => {
  // 脉冲逻辑：用 CSS 变量控制发光强度随时间变化
  const pulseStyle =
    pulseSpeed > 0
      ? {
          animation: `neon-pulse ${2 / pulseSpeed}s ease-in-out infinite alternate`,
        }
      : {};

  // 构建多层 text-shadow 模拟霓虹发光
  const alpha = glowIntensity;
  const shadowLayers = [
    `0 0 ${glowRadius * 0.25}px ${glowColor}`,
    `0 0 ${glowRadius * 0.5}px ${glowColor}`,
    `0 0 ${glowRadius}px ${glowColor}`,
    `0 0 ${glowRadius * 2}px ${glowColor}`,
  ].join(", ");

  return (
    <>
      <style>
        {`
          @keyframes neon-pulse {
            from { opacity: ${Math.max(0.3, alpha - 0.3)}; }
            to { opacity: ${alpha}; }
          }
        `}
      </style>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          pointerEvents: "none",
          zIndex: layer,
          textShadow: shadowLayers,
          color: glowColor,
          opacity: alpha,
          ...pulseStyle,
        }}
      />
    </>
  );
};

export const neonGlowMeta: ComponentMeta = {
  allowedParams: ["glowColor", "glowIntensity", "glowRadius", "pulseSpeed"],
  defaults: {
    glowColor: "#ff00ff",
    glowIntensity: 0.8,
    glowRadius: 40,
    pulseSpeed: 0,
  },
};