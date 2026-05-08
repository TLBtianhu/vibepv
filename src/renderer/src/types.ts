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
  detected_bpm: number;
  model: string;
  manual_override: boolean;
}

// ====== 新增：AI 生成的视觉参数格式 ======
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

// ====== 最终传入组件的完整 Props ======
export type VibePVProps = {
  lyrics: {
    words: WordTimestamp[];
    sentences: SentenceTimestamp[];
  };
  bpm: BPMData;
  merge_multiplier: number;
  audio_duration_ms: number;
  audio_file: string;
  visual_params: VisualParams;
};

// ====== VisualPlan 类型定义 ======

// 效果规则：一条规则描述一个视觉元素
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

// 视觉计划：Agent 输出的顶层结构
export type VisualPlan = {
  metadata: {
    style: string;
    description: string;
  };
  rules: EffectRule[];
};

// ====== 组件元数据类型 ======
export type ComponentMeta = {
  allowedParams: string[];
  defaults: Record<string, unknown>;
};