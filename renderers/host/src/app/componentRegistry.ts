import type { ComponentType } from "react";
import type { ComponentMeta } from "./types";

export type RegistryEntry = {
  component: ComponentType<any>;
  meta: ComponentMeta;
};

export const componentRegistry: Record<string, RegistryEntry> = {};

const context = require.context("../../../workspace/components", true, /Component\.tsx$/);

for (const key of context.keys()) {
  const mod = context(key);
  const folderName = key.split("/")[1];
  const component = mod[folderName];
  const metaName = folderName.charAt(0).toLowerCase() + folderName.slice(1) + "Meta";
  const meta = mod[metaName];
  if (component && meta) {
    componentRegistry[folderName] = { component, meta };
  }
}