export interface WordTimestamp {
  text: string;
  start_ms: number;
  end_ms: number;
}

export interface SentenceTimestamp {
  text: string;
  start_ms: number;
  end_ms: number;
}

export interface BPMData {
  detected_bpm: number | null;
  model: string;
  manual_override: boolean;
  error?: string;
}

export interface VisualParams {
  particle_speed: number;
  color_scheme: string[];
  energy_sync: "low" | "medium" | "high";
  bpm_sync: "off" | "quarter_beat" | "half_beat" | "full_beat";
  canvas_effects: string[];
  beat_effect: string;
  subtitle_animation: string;
  reasoning?: string;
}

export type VibePVProps = {
  lyrics: {
    words: WordTimestamp[];
    sentences: SentenceTimestamp[];
  } | null;
  bpm: BPMData | null;
  merge_multiplier: number | null;
  audio_duration_ms: number;
  audio_file: string;
  visual_params: VisualParams;
};

export type EffectRule = {
  effectId: string;
  type: "component" | "custom";
  layer: number;
  component?: string;
  target?: "canvas";
  dataSource?: "audio:spectrum";
  params: Record<string, unknown>;
  animation?: {
    type: "spring";
    config: Record<string, number>;
  };
  renderLogic?: string;
  timeline: {
    start: number;
    end: number;
  };
};

export type VisualPlan = {
  metadata: {
    style: string;
    description: string;
  };
  rules: EffectRule[];
};

export type ComponentMeta = {
  allowedParams: string[];
  defaults: Record<string, unknown>;
  renderMode?: "overlay" | "wrapper";
  requiresData?: string[];
};