import type { ComponentType } from "react";
import type { ComponentMeta } from "../../src/renderer/src/app/types";

export type RegistryEntry = {
  component: ComponentType<any>;
  meta: ComponentMeta;
};

export const componentRegistry: Record<string, RegistryEntry> = {};

// Vite 方式的批量导入
const modules = import.meta.glob(
  "../../src/renderer/components/*/Component.tsx",
  { eager: true }
);

for (const [filePath, module] of Object.entries(modules)) {
  const mod = module as any;
  // 从路径中提取文件夹名，例: '../../src/renderer/components/AnimatedGradient/Component.tsx' -> 'AnimatedGradient'
  const folderName = filePath.split("/").slice(-2)[0];

  const component = mod[folderName];
  const metaName = folderName.charAt(0).toLowerCase() + folderName.slice(1) + "Meta";
  const meta = mod[metaName];

  if (component && meta) {
    componentRegistry[folderName] = { component, meta };
  }
}

// 别名
componentRegistry["ParticleField"] = componentRegistry["CanvasParticleField"];