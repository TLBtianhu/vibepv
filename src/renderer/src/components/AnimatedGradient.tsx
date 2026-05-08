import React from "react";
import type { ComponentMeta } from "../componentRegistry";

type Props = {
  colors?: string[];
  layer?: number;
};

export const AnimatedGradient: React.FC<Props> = ({
  colors = ["#000", "#fff"],
  layer = 0,
}) => {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: `linear-gradient(135deg, ${colors.join(", ")})`,
        zIndex: layer,
      }}
    />
  );
};

export const animatedGradientMeta: ComponentMeta = {
  allowedParams: ["colors"],
  defaults: { colors: ["#000", "#fff"] },
};