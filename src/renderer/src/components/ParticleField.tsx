import { useEffect, useState } from "react";
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import type { Container } from "@tsparticles/engine";

type Props = {
  particleCount?: number;
  color?: string;
  colorSecondary?: string;
  sizeRange?: [number, number];
  speedRange?: [number, number];
  opacity?: number;
  layer?: number;
};

export const ParticleField: React.FC<Props> = ({
  particleCount = 50,
  color = "#ffffff",
  colorSecondary,
  sizeRange = [2, 6],
  speedRange = [0.5, 2.0],
  opacity = 0.5,
  layer = 0,
}) => {
  // 硬限制：单层粒子不超过 100，防止渲染超时
  const safeCount = Math.min(particleCount, 100);

  const [ready, setReady] = useState(false);

  useEffect(() => {
    initParticlesEngine(async (engine) => {
      await loadSlim(engine);
    }).then(() => setReady(true));
  }, []);

  const particlesLoaded = async (_container?: Container): Promise<void> => {
    // 粒子加载完成，可用于高级控制
  };

  if (!ready) return null;

  return (
    <Particles
      id="vibepv-particles"
      particlesLoaded={particlesLoaded}
      options={{
        particles: {
          number: { value: safeCount },
          color: {
            value: color,
            ...(colorSecondary ? { animation: { enable: true, speed: 4, sync: false, color: [color, colorSecondary] } } : {}),
          },
          size: {
            value: { min: sizeRange[0], max: sizeRange[1] },
          },
          move: {
            enable: true,
            speed: { min: speedRange[0], max: speedRange[1] },
            direction: "bottom",
            straight: false,
          },
          opacity: { value: opacity },
          shape: { type: "circle" },
        },
        detectRetina: true,
      }}
      style={{
        position: "absolute",
        inset: 0,
        zIndex: layer,
        pointerEvents: "none",
      }}
    />
  );
};