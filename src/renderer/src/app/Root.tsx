// @ts-nocheck
import { Composition } from "remotion";
import { RuleRenderer } from "./RuleRenderer";
import type { VibePVProps, VisualPlan } from "./types";

type ExtendedProps = VibePVProps & { visual_plan: VisualPlan };

export const RemotionRoot: React.FC = () => {
  return (
    <Composition<ExtendedProps>
      id="SongLyrics"
      component={RuleRenderer}
      durationInFrames={1}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        lyrics: null,
        bpm: null,
        merge_multiplier: null,
        audio_duration_ms: 0,
        audio_file: "",
        visual_params: {
          particle_speed: 1.0,
          color_scheme: ["#0a0a2a", "#ff00ff", "#00ffff"],
          energy_sync: "medium",
          bpm_sync: "quarter_beat",
          canvas_effects: ["spectrum"],
          beat_effect: "none",
          subtitle_animation: "fade_in",
        },
        visual_plan: {
          metadata: { style: "default", description: "默认视觉计划" },
          rules: [],
        },
      }}
      calculateMetadata={({ props }) => {
        const totalFrames = Math.ceil((props.audio_duration_ms / 1000) * 30);
        return {
          durationInFrames: totalFrames > 0 ? totalFrames : 1,
          props,
        };
      }}
    />
  );
};