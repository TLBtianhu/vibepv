import type { ComponentType } from "react";
import type { ComponentMeta } from "../../host/src/app/types";

export type RegistryEntry = {
  component: ComponentType<any>;
  meta: ComponentMeta;
};

export const componentRegistry: Record<string, RegistryEntry> = {};

const modules = import.meta.glob(
  "../../workspace/components/*/Component.tsx",
  { eager: true }
);

for (const [filePath, module] of Object.entries(modules)) {
  const mod = module as any;
  const folderName = filePath.split("/").slice(-2)[0];
  const component = mod[folderName];
  const metaName = folderName.charAt(0).toLowerCase() + folderName.slice(1) + "Meta";
  const meta = mod[metaName];
  if (component && meta) {
    componentRegistry[folderName] = { component, meta };
  }
}