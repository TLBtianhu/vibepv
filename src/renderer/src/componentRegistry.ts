// src/renderer/src/componentRegistry.ts
import type { ComponentType } from "react";
import { AnimatedGradient } from "./components/AnimatedGradient";
import { LyricsVideo } from "./LyricsVideo";

// 所有可被 Agent 调度的组件都在这注册
export const componentRegistry: Record<string, ComponentType<any>> = {
  AnimatedGradient,
  LyricsDisplay: LyricsVideo,
  // 后续新组件在这里追加
  // ParticleField: ParticleField,
  // SpectrumVisualizer: SpectrumVisualizer,
};