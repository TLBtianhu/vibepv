import React from "react";
import { ErrorBoundary } from "./ErrorBoundary";
import { RuleRenderer } from "./RuleRenderer";
import type { VisualPlan, VibePVProps } from "../../src/renderer/src/app/types";

type Props = {
  visual_plan?: VisualPlan;
} & Pick<VibePVProps, "lyrics" | "bpm" | "audio_file" | "audio_duration_ms" | "visual_params">;

export const SafeRuleRenderer: React.FC<Props> = (props) => {
  return (
    <ErrorBoundary>
      <RuleRenderer {...props} />
    </ErrorBoundary>
  );
};