// src/renderer/src/RuleRenderer.tsx
import { useCurrentFrame } from "remotion";
import type { VisualPlan, VibePVProps } from "./types";
import { componentRegistry } from "./componentRegistry";

type Props = {
  visual_plan?: VisualPlan;   // 字段名改为 visual_plan，设为可选以防御缺失
} & Pick<VibePVProps, "lyrics" | "bpm" | "audio_file" | "audio_duration_ms" | "visual_params">;

export const RuleRenderer: React.FC<Props> = ({ visual_plan, ...commonProps }) => {
  const frame = useCurrentFrame();

  // 防御：万一 visual_plan 或 rules 缺失，使用空数组
  const rules = visual_plan?.rules ?? [];
  const activeRules = rules
    .filter((rule) => frame >= rule.timeline.start && frame <= rule.timeline.end)
    .sort((a, b) => a.layer - b.layer);

  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      {activeRules.map((rule) => {
        const Component = componentRegistry[rule.component || ""];
        if (!Component) return null;

        return (
          <Component
            key={rule.effectId}
            {...commonProps}
            {...rule.params}
            effectId={rule.effectId}
            layer={rule.layer}
          />
        );
      })}
    </div>
  );
};