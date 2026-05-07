import type { ComponentType } from "react";
import { AnimatedGradient } from "./components/AnimatedGradient";
import { CanvasParticleField } from "./components/CanvasParticleField";
import { LyricsVideo } from "./LyricsVideo";

export const componentRegistry: Record<string, ComponentType<any>> = {
  AnimatedGradient,
  LyricsDisplay: LyricsVideo,
  ParticleField: CanvasParticleField,  // ← Canvas 版本
};