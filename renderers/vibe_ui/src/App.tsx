import { useEffect, useState, useCallback } from "react";
import { Player } from "@remotion/player";
import { SafeRuleRenderer } from "./SafeRuleRenderer";
import { useStore } from "./store";
import { PropertyPanel } from "./PropertyPanel";

export default function App() {
  const visualPlan = useStore((s) => s.visualPlan);
  const dataSources = useStore((s) => s.dataSources);
  const setProjectBundle = useStore((s) => s.setProjectBundle);
  const [selectedEffectId, setSelectedEffectId] = useState("");
  const [loading, setLoading] = useState(true);

  const loadProjectBundle = useCallback(() => {
    fetch("/project_bundle.json")
      .then((res) => {
        if (!res.ok) throw new Error("文件不存在");
        return res.json();
      })
      .then((data) => {
        const plan = data.visual_plan;
        const ds = data.data_sources || {};
        setProjectBundle(plan, ds);
        if (plan.rules?.length > 0) setSelectedEffectId(plan.rules[0].effectId);
        setLoading(false);
      })
      .catch((err) => {
        console.error("[App] 加载 project_bundle.json 失败:", err);
        setLoading(false);
      });
  }, [setProjectBundle]);

  useEffect(() => { loadProjectBundle(); }, [loadProjectBundle]);

  // WebSocket 监听
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimer: number | null = null;
    const connect = () => {
      ws = new WebSocket("ws://localhost:54322");
      ws.onopen = () => console.log("[App] WebSocket 已连接");
      ws.onmessage = (event) => {
        if (event.data === "refresh") {
          console.log("[App] 收到 refresh，重新加载数据...");
          loadProjectBundle();
        }
      };
      ws.onclose = () => {
        console.log("[App] WebSocket 已断开，3秒后重连...");
        reconnectTimer = window.setTimeout(connect, 3000);
      };
      ws.onerror = () => ws?.close();
    };
    connect();
    return () => { ws?.close(); if (reconnectTimer) clearTimeout(reconnectTimer); };
  }, [loadProjectBundle]);

  if (loading) return <div className="h-screen w-screen bg-gray-900 flex items-center justify-center text-white">加载中...</div>;
  if (!visualPlan?.rules?.length) return <div className="h-screen w-screen bg-gray-900 flex items-center justify-center text-white">暂无数据</div>;

  return (
    <div className="h-screen w-screen bg-gray-900 flex flex-col">
      <div className="h-12 bg-gray-800 flex items-center justify-between px-4 text-white text-sm border-b border-gray-700">
        VibePV Studio
        <button onClick={handleSave} className="bg-pink-600 hover:bg-pink-500 text-xs px-3 py-1 rounded">保存工程</button>
      </div>
      <div className="flex-1 flex">
        <div className="flex-1 flex items-center justify-center bg-gray-950">
          <Player
            component={SafeRuleRenderer}
            inputProps={{
              visual_plan: visualPlan,
              lyrics: dataSources?.["lyrics.words"] ? { words: dataSources["lyrics.words"], sentences: [] } : null,
              bpm: dataSources?.["bpm"] ?? null,
              audio_file: dataSources?.["audio_file"] ?? "",
              audio_duration_ms: dataSources?.["audio_duration_ms"] ?? 10000,
              visual_params: {} as any,
            }}
            durationInFrames={dataSources?.["audio_duration_ms"] ? Math.ceil(dataSources["audio_duration_ms"] / 1000 * 30) : 300}
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
            <select value={selectedEffectId} onChange={(e) => setSelectedEffectId(e.target.value)}
              className="w-full bg-gray-900 text-white text-sm px-2 py-1 rounded border border-gray-600">
              {visualPlan.rules.map((rule: any) => (
                <option key={rule.effectId} value={rule.effectId}>{rule.component} ({rule.effectId})</option>
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

const handleSave = async () => {
  const { useStore } = await import("./store");
  const state = useStore.getState();
  const bundle = {
    visual_plan: state.visualPlan,
    data_sources: state.dataSources || {},
    available_fields: state.dataSources ? Object.keys(state.dataSources) : [],
  };
  fetch("/save", { method: "POST", body: JSON.stringify(bundle), headers: { "Content-Type": "application/json" } });
};