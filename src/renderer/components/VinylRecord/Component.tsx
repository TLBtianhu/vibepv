import { useCurrentFrame } from "remotion";
import type { ComponentMeta } from "../../src/app/types";

type Props = {
  rpm?: number;           // 转速（圈/分钟），默认 33.3
  vinylColor?: string;    // 唱片底色，默认深黑
  grooveColor?: string;   // 沟槽颜色，默认浅灰
  labelColor?: string;    // 中心标签颜色，默认暖黄
  size?: number;          // 唱片直径（像素），默认 600
  layer?: number;
};

export const VinylRecord: React.FC<Props> = ({
  rpm = 33.3,
  vinylColor = "#1a1a1a",
  grooveColor = "#2a2a2a",
  labelColor = "#f5e6c8",
  size = 600,
  layer = 0,
}) => {
  const frame = useCurrentFrame();
  const radius = size / 2;
  const centerX = 1920 / 2;
  const centerY = 1080 / 2;

  // 旋转角度：每帧旋转 (rpm / 60) * 360 / 30 度
  const rotation = (frame * rpm * 360) / (60 * 30);

  const draw = (ctx: CanvasRenderingContext2D) => {
    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.rotate((rotation * Math.PI) / 180);

    // 唱片盘面
    ctx.beginPath();
    ctx.arc(0, 0, radius, 0, Math.PI * 2);
    ctx.fillStyle = vinylColor;
    ctx.fill();

    // 沟槽圆弧（多圈同心圆）
    for (let r = radius - 10; r > radius * 0.25; r -= 8) {
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.strokeStyle = grooveColor;
      ctx.lineWidth = 0.5;
      ctx.stroke();
    }

    // 高光反射（径向渐变模拟光源）
    const gradient = ctx.createLinearGradient(-radius, -radius, radius, radius);
    gradient.addColorStop(0, "rgba(255, 255, 255, 0.08)");
    gradient.addColorStop(0.3, "rgba(255, 255, 255, 0.02)");
    gradient.addColorStop(0.5, "rgba(255, 255, 255, 0)");
    gradient.addColorStop(0.7, "rgba(255, 255, 255, 0.01)");
    gradient.addColorStop(1, "rgba(255, 255, 255, 0.06)");
    ctx.beginPath();
    ctx.arc(0, 0, radius, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.fill();

    // 两道弧形反光条（模拟窗户/灯光反射）
    ctx.save();
    ctx.rotate(Math.PI * 0.15); // 稍微偏移角度，让反光条不在正上方
    for (let i = 0; i < 2; i++) {
      const angle = i * Math.PI; // 两道反光条相对
      ctx.save();
      ctx.rotate(angle);
      ctx.beginPath();
      ctx.ellipse(radius * 0.35, 0, radius * 0.15, radius * 0.6, 0, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(255, 255, 255, 0.03)";
      ctx.fill();
      ctx.restore();
    }
    ctx.restore();

    // 中心标签
    const labelR = radius * 0.22;
    ctx.beginPath();
    ctx.arc(0, 0, labelR, 0, Math.PI * 2);
    ctx.fillStyle = labelColor;
    ctx.fill();

    // 标签内圈装饰
    ctx.beginPath();
    ctx.arc(0, 0, labelR * 0.7, 0, Math.PI * 2);
    ctx.fillStyle = "#e8d5a3";
    ctx.fill();

    // 中心孔
    ctx.beginPath();
    ctx.arc(0, 0, 4, 0, Math.PI * 2);
    ctx.fillStyle = "#000";
    ctx.fill();

    ctx.restore();
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

export const vinylRecordMeta: ComponentMeta = {
  allowedParams: ["rpm", "vinylColor", "grooveColor", "labelColor", "size"],
  defaults: {
    rpm: 33.3,
    vinylColor: "#1a1a1a",
    grooveColor: "#2a2a2a",
    labelColor: "#f5e6c8",
    size: 600,
  },
};