import React from "react";
import type { ComponentMeta } from "../componentRegistry";

type Props = {
  opacity?: number;   // 扫描线透明度，0~1，默认 0.08
  color?: string;     // 扫描线颜色，默认黑色
  layer?: number;
};

export const ScanLines: React.FC<Props> = ({
  opacity = 0.08,
  color = "#000",
  layer = 1,
}) => {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        pointerEvents: "none",
        zIndex: layer,
        background: `repeating-linear-gradient(
          0deg,
          transparent,
          transparent 2px,
          ${color} 2px,
          ${color} 4px
        )`,
        opacity,
      }}
    />
  );
};

export const scanLinesMeta: ComponentMeta = {
  allowedParams: ["opacity", "color"],
  defaults: { opacity: 0.08, color: "#000" },
};