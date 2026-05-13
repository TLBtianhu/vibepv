import { useCurrentFrame } from "remotion";
import { useAudioData, visualizeAudio } from "@remotion/media-utils";
import { staticFile } from "remotion";
import type { ComponentMeta } from "../../../renderers/host/src/app/types";;

type Props = {
  audioFile: string;
  radius?: number;
  barCount?: number;
  maxHeight?: number;
  color?: string;
  opacity?: number;
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
        {spectrum.map((value, i) => {
          const angle = (i / barCount) * Math.PI * 2 - Math.PI / 2;
          const x1 = centerX + radius * Math.cos(angle);
          const y1 = centerY + radius * Math.sin(angle);
          const height = Math.max(2, value * maxHeight);
          const x2 = centerX + (radius + height) * Math.cos(angle);
          const y2 = centerY + (radius + height) * Math.sin(angle);

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
              opacity={0.5 + value * 0.5}
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
  renderMode: "overlay",
  requiresData: ["audio_file"],
};