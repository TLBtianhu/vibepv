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

  const wrapperRules = activeRules.filter(
    (r) => (componentRegistry[r.component || ""]?.meta?.renderMode ?? "overlay") === "wrapper"
  );
  const overlayRules = activeRules.filter(
    (r) => (componentRegistry[r.component || ""]?.meta?.renderMode ?? "overlay") !== "wrapper"
  );

  const renderRule = (rule: typeof activeRules[0]) => {
    const entry = componentRegistry[rule.component || ""];
    if (!entry) return null;

    const safeParams: Record<string, unknown> = {};
    for (const key of entry.meta.allowedParams) {
      if (key in rule.params) {
        safeParams[key] = rule.params[key];
      } else {
        console.warn(
          `[RuleRenderer] 组件 "${rule.component}" 缺少参数 "${key}"，已使用默认值`
        );
        safeParams[key] = entry.meta.defaults[key];
      }
    }

    for (const key of Object.keys(rule.params)) {
      if (!entry.meta.allowedParams.includes(key)) {
        console.warn(
          `[RuleRenderer] 组件 "${rule.component}" 收到了未知参数 "${key}"，已忽略`
        );
      }
    }

    const Component = entry.component;
    return (
      <Component
        key={rule.effectId}
        {...commonProps}
        {...safeParams}
        words={commonProps.lyrics?.words ?? []}
        effectId={rule.effectId}
        layer={rule.layer}
      />
    );
  };

  const overlayElements = overlayRules.map(renderRule).filter(Boolean);
  const children = <>{overlayElements}</>;

  if (wrapperRules.length > 0) {
    const wrapperRule = wrapperRules[0];
    const entry = componentRegistry[wrapperRule.component || ""];
    if (entry) {
      const safeParams: Record<string, unknown> = {};
      for (const key of entry.meta.allowedParams) {
        safeParams[key] = key in wrapperRule.params ? wrapperRule.params[key] : entry.meta.defaults[key];
      }
      const WrapperComponent = entry.component;
      return (
        <div style={{ width: "100%", height: "100%", position: "relative" }}>
          <WrapperComponent {...safeParams} layer={wrapperRule.layer}>
            {children}
          </WrapperComponent>
        </div>
      );
    }
  }

  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      {children}
    </div>
  );
};