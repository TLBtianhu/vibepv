import type { ComponentType } from "react";
import type { ComponentMeta } from "./types";

export type RegistryEntry = {
  component: ComponentType<any>;
  meta: ComponentMeta;
};

// 自动扫描 src/renderer/components/ 下子目录中的 index.ts 桶文件
const context = require.context("../../components", true, /index\.ts$/);
const registry: Record<string, RegistryEntry> = {};

context.keys().forEach((key: string) => {
  const module = context(key);
  const Component = module.Component;
  const Meta = module.Meta;
  if (Component && Meta) {
    const folderName = key.split("/")[1];
    registry[folderName] = { component: Component, meta: Meta };
  }
});

// 别名映射
registry["ParticleField"] = registry["CanvasParticleField"];

export const componentRegistry = registry;