import { create } from 'zustand';
import type { VisualPlan } from '../../src/renderer/src/app/types';

interface VibePVState {
  visualPlan: VisualPlan | null;
  setVisualPlan: (plan: VisualPlan) => void;
  updateParam: (effectId: string, key: string, value: any) => void;
}

export const useStore = create<VibePVState>((set) => ({
  visualPlan: null,

  setVisualPlan: (plan) => set({ visualPlan: plan }),

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