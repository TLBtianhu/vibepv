import type { ComponentType } from "react";

// 组件元数据类型 (保持不变)
export type ComponentMeta = {
  allowedParams: string[];
  defaults: Record<string, unknown>;
};

// 注册表条目类型 (保持不变)
export type RegistryEntry = {
  component: ComponentType<any>;
  meta: ComponentMeta;
};

// 自动化注册表构建
const registry: Record<string, RegistryEntry> = {};

// 使用 Webpack 的 require.context 来自动发现组件
const componentContext = require.context('./components', false, /\.tsx$/);

componentContext.keys().forEach((key: string) => {
  const module: any = componentContext(key);
  // 将文件名 (如 './GlitchText.tsx') 清理为组件名 (如 'GlitchText')
  const componentName = key.replace('./', '').replace('.tsx', '');

  const component = module[componentName];
  const meta = module[`${componentName}Meta`];

  // 如果文件符合约定（同时导出了组件和Meta），则自动注册
  if (component && meta) {
    // 在这里可以自定义组件在代理眼中的名字
    registry[componentName] = { component, meta };
  }
});

export const componentRegistry = registry;