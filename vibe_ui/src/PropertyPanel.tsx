import { useStore } from "./store";
import { componentRegistry } from "./registry";

type Props = {
  effectId: string;
};

export const PropertyPanel: React.FC<Props> = ({ effectId }) => {
  const visualPlan = useStore((s) => s.visualPlan);
  const updateParam = useStore((s) => s.updateParam);

  const rule = visualPlan?.rules.find((r) => r.effectId === effectId);
  if (!rule) return <p className="text-gray-500 text-sm">未选中任何零件</p>;

  const entry = componentRegistry[rule.component || ""];
  if (!entry) return <p className="text-gray-500 text-sm">零件未注册: {rule.component}</p>;

  const { meta } = entry;
  const params = rule.params || {};

  const renderControl = (key: string, defaultValue: unknown) => {
    const current = params[key] ?? defaultValue;

    if (typeof defaultValue === "number") {
      const num = current as number;
      const min = key === "opacity" || key === "intensity" ? 0 : 0;
      const max = key === "opacity" || key === "intensity" ? 1 : 200;
      const step = key === "opacity" || key === "intensity" ? 0.01 : 1;

      return (
        <div key={key} className="mb-4">
          <label className="text-gray-300 text-xs mb-1 block">
            {key} ({num.toFixed(2)})
          </label>
          <input
            type="range" min={min} max={max} step={step}
            value={num}
            onChange={(e) => updateParam(effectId, key, Number(e.target.value))}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-pink-500"
          />
        </div>
      );
    }

    if (typeof defaultValue === "string") {
      const str = current as string;
      const isColor = defaultValue.startsWith("#") || key.toLowerCase().includes("color");
      return (
        <div key={key} className="mb-4">
          <label className="text-gray-300 text-xs mb-1 block">{key}</label>
          <div className="flex gap-2">
            <input
              type={isColor ? "color" : "text"}
              value={str}
              onChange={(e) => updateParam(effectId, key, e.target.value)}
              className={
                isColor
                  ? "w-10 h-8 rounded cursor-pointer border border-gray-600 bg-gray-900"
                  : "flex-1 bg-gray-900 text-white text-xs px-2 py-1 rounded border border-gray-600"
              }
            />
            <span className="text-gray-400 text-xs self-center">{str}</span>
          </div>
        </div>
      );
    }

    if (Array.isArray(defaultValue)) {
      return (
        <div key={key} className="mb-4">
          <label className="text-gray-300 text-xs mb-1 block">{key}</label>
          <div className="bg-gray-900 text-gray-400 text-xs p-2 rounded border border-gray-700 font-mono">
            {JSON.stringify(current)}
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <div>
      <h3 className="text-white font-bold mb-4 text-sm">
        {rule.component || "未知零件"}
      </h3>
      <p className="text-gray-500 text-xs mb-4">
        {meta.allowedParams.length} 个可调参数
      </p>
      {meta.allowedParams.map((k: string) => renderControl(k, meta.defaults[k]))}
    </div>
  );
};