// src/renderer/src/RuleRenderer.tsx
import { useCurrentFrame } from "remotion";
import type { VisualPlan, VibePVProps } from "./types";
import { componentRegistry } from "./componentRegistry";

type Props = {
  visual_plan?: VisualPlan;
} & Pick<VibePVProps, "lyrics" | "bpm" | "audio_file" | "audio_duration_ms" | "visual_params">;

export const RuleRenderer: React.FC<Props> = ({ visual_plan, ...commonProps }) => {
  const frame = useCurrentFrame();

  const rules = visual_plan?.rules ?? [];
  const activeRules = rules
    .filter((rule) => frame >= rule.timeline.start && frame <= rule.timeline.end)
    .sort((a, b) => a.layer - b.layer);

  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      {activeRules.map((rule) => {
        const entry = componentRegistry[rule.component || ""];
        if (!entry) return null;

        // 白名单过滤：只保留组件允许的参数，缺失的用默认值补上
        const safeParams: Record<string, unknown> = {};
        for (const key of entry.meta.allowedParams) {
          if (key in rule.params) {
            safeParams[key] = rule.params[key];
          } else {
            // eslint-disable-next-line no-console
            console.warn(
              `[RuleRenderer] 组件 "${rule.component}" 缺少参数 "${key}"，已使用默认值`
            );
            safeParams[key] = entry.meta.defaults[key];
          }
        }

        // 检查 Agent 是否传了不在白名单里的未知参数
        for (const key of Object.keys(rule.params)) {
          if (!entry.meta.allowedParams.includes(key)) {
            // eslint-disable-next-line no-console
            console.warn(
              `[RuleRenderer] 组件 "${rule.component}" 收到了未知参数 "${key}"，已忽略`
            );
          }
        }

        const Component = entry.component;
        const extendedProps = {
          ...commonProps,
          ...safeParams,
          words: commonProps.lyrics?.words ?? [],
          effectId: rule.effectId,
          layer: rule.layer,
        };
        return (
          <Component key={rule.effectId} {...extendedProps} />
        );
      })}
    </div>
  );
};