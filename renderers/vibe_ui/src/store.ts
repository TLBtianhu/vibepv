import { create } from 'zustand';
import type { VisualPlan } from '../../host/src/app/types';

interface VibePVState {
  visualPlan: VisualPlan | null;
  dataSources: Record<string, any> | null;
  setProjectBundle: (plan: VisualPlan, data: Record<string, any>) => void;
  updateParam: (effectId: string, key: string, value: any) => void;
}

export const useStore = create<VibePVState>((set) => ({
  visualPlan: null,
  dataSources: null,
  setProjectBundle: (plan, data) => set({ visualPlan: plan, dataSources: data }),
  updateParam: (effectId, key, value) =>
    set((state) => {
      if (!state.visualPlan) return state;
      return {
        visualPlan: {
          ...state.visualPlan,
          rules: state.visualPlan.rules.map((rule) =>
            rule.effectId === effectId
              ? { ...rule, params: { ...rule.params, [key]: value } }
              : rule
          ),
        },
      };
    }),
}));