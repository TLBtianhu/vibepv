import { useCurrentFrame } from "remotion";
import type { ComponentMeta } from "../../src/app/types";

type Props = {
  particleCount?: number;
  color?: string;
  colorSecondary?: string;
  sizeRange?: [number, number];
  speedRange?: [number, number];
  opacity?: number;
  layer?: number;
};

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  color: string;
}

export const CanvasParticleField: React.FC<Props> = ({
  particleCount = 60,
  color = "#ff00ff",
  colorSecondary,
  sizeRange = [1, 6],
  speedRange = [0.3, 1.5],
  opacity = 0.6,
  layer = 0,
}) => {
  const frame = useCurrentFrame();
  const safeCount = Math.min(particleCount, 120);

    const pseudoRandom = (seed: number) => (min: number, max: number) =>
    min + ((seed * 2654435761) % 1000) / 1000 * (max - min);

  const particles: Particle[] = Array.from({ length: safeCount }, (_, idx) => {
    const seed = idx * 137.5 + 1;
    const rand = pseudoRandom(seed);

    return {
      x: rand(0, 1920),
      y: rand(0, 1080),
      vx: rand(-1, 1) * speedRange[1],
      vy: -rand(speedRange[0], speedRange[1]),
      size: rand(sizeRange[0], sizeRange[1]),
      color: colorSecondary
        ? (Math.random() > 0.5 ? color : colorSecondary)
        : color,
    };
  });

  const draw = (ctx: CanvasRenderingContext2D) => {
    ctx.clearRect(0, 0, 1920, 1080);
    ctx.globalAlpha = opacity;

    particles.forEach((p) => {
      const y = (p.y + p.vy * frame) % 1080;
      const x = (p.x + p.vx * frame + 1920) % 1920;

      ctx.beginPath();
      ctx.arc(x, y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.fill();
    });
  };

  return (
    <canvas
      ref={(el) => {
        if (!el) return;
        const ctx = el.getContext("2d");
        if (ctx) draw(ctx);
      }}
      width={1920}
      height={1080}
      style={{
        position: "absolute",
        inset: 0,
        zIndex: layer,
        pointerEvents: "none",
      }}
    />
  );
};

export const canvasParticleFieldMeta: ComponentMeta = {
  allowedParams: ["particleCount", "color", "colorSecondary", "sizeRange", "speedRange", "opacity"],
  defaults: {
    particleCount: 60,
    color: "#ff00ff",
    sizeRange: [1, 6],
    speedRange: [0.3, 1.5],
    opacity: 0.6,
  },
};