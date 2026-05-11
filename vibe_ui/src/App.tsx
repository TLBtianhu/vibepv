import { useEffect, useState } from "react";
import { Player } from "@remotion/player";
import { SafeRuleRenderer } from "./SafeRuleRenderer";
import { useStore } from "./store";
import { PropertyPanel } from "./PropertyPanel";

export default function App() {
  const visualPlan = useStore((s) => s.visualPlan);
  const setVisualPlan = useStore((s) => s.setVisualPlan);
  const [selectedEffectId, setSelectedEffectId] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log("[App] 开始请求 /visual_params.json");
    fetch("/visual_params.json")
      .then((res) => {
        console.log("[App] fetch 响应状态:", res.status);
        if (!res.ok) throw new Error("文件不存在");
        return res.json();
      })
      .then((data) => {
        console.log("[App] 原始 JSON 数据:", data);
        const plan = data.visual_plan || data;
        console.log("[App] 提取后的 visualPlan:", plan);
        setVisualPlan(plan);
        if (plan.rules && plan.rules.length > 0) {
          setSelectedEffectId(plan.rules[0].effectId);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("[App] 加载或解析失败:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="h-screen w-screen bg-gray-900 flex items-center justify-center text-white">
        正在加载视觉计划...
      </div>
    );
  }

  if (!visualPlan?.rules?.length) {
    return (
      <div className="h-screen w-screen bg-gray-900 flex items-center justify-center text-white">
        暂无数据，请先运行 Agent 生成 visual_params.json
      </div>
    );
  }

  return (
    <div className="h-screen w-screen bg-gray-900 flex flex-col">
      <div className="h-12 bg-gray-800 flex items-center px-4 text-white text-sm border-b border-gray-700">
        VibePV Studio
      </div>
      <div className="flex-1 flex">
        <div className="flex-1 flex items-center justify-center bg-gray-950">
          <Player
            component={SafeRuleRenderer}
            inputProps={{
              visual_plan: visualPlan,
              lyrics: null,
              bpm: null,
              audio_file: "",
              audio_duration_ms: 10000,
              visual_params: {} as any,
            }}
            durationInFrames={300}
            fps={30}
            compositionWidth={1920}
            compositionHeight={1080}
            acknowledgeRemotionLicense="VibePV-Dev-2026"
            style={{ width: "100%", maxWidth: 800, aspectRatio: "16/9" }}
            controls
          />
        </div>
        <div className="w-72 bg-gray-800 p-4 border-l border-gray-700 overflow-y-auto">
          <div className="mb-4">
            <label className="text-gray-300 text-xs mb-1 block">当前编辑</label>
            <select
              value={selectedEffectId}
              onChange={(e) => setSelectedEffectId(e.target.value)}
              className="w-full bg-gray-900 text-white text-sm px-2 py-1 rounded border border-gray-600"
            >
              {visualPlan.rules.map((rule) => (
                <option key={rule.effectId} value={rule.effectId}>
                  {rule.component} ({rule.effectId})
                </option>
              ))}
            </select>
          </div>
          <PropertyPanel effectId={selectedEffectId} />
        </div>
      </div>
      <div className="h-8 bg-gray-800 flex items-center px-4 text-gray-400 text-xs border-t border-gray-700">
        从下拉菜单切换零件 | 拖动滑块实时调参
      </div>
    </div>
  );
}