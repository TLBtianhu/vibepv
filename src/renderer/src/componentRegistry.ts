import type { ComponentType } from "react";
import type { ComponentMeta } from "./types";

export type RegistryEntry = {
  component: ComponentType<any>;
  meta: ComponentMeta;
};

// 扫描所有 index.ts 桶文件
const context = require.context("./components", true, /index\.ts$/);
const registry: Record<string, RegistryEntry> = {};

context.keys().forEach((key: string) => {
  const module = context(key);
  // 使用固定导出名获取组件和元数据
  const Component = module.Component;
  const Meta = module.Meta;
  if (Component && Meta) {
    // 从 index 文件的原始命名导出中获取组件名（用于注册表 key）
    // 这里可以直接从文件夹路径提取组件名
    const folderName = key.split("/")[1]; // "./AnimatedGradient/index.ts" -> "AnimatedGradient"
    registry[folderName] = { component: Component, meta: Meta };
  }
});

// 别名
registry["ParticleField"] = registry["CanvasParticleField"];

export const componentRegistry = registry;