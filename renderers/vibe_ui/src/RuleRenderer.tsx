import { useCurrentFrame } from "remotion";
import type { VisualPlan, VibePVProps } from "../../host/src/app/types";
import { componentRegistry } from "./registry";

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
      safeParams[key] = key in rule.params ? rule.params[key] : entry.meta.defaults[key];
    }
    const Component = entry.component;
    return <Component key={rule.effectId} {...commonProps} {...safeParams} effectId={rule.effectId} layer={rule.layer} />;
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
          <WrapperComponent {...safeParams}>{children}</WrapperComponent>
        </div>
      );
    }
  }

  return <div style={{ width: "100%", height: "100%", position: "relative" }}>{children}</div>;
};