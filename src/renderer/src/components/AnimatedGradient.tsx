import React from "react";

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