# AI教案生成工作站 - 设计系统 Token

> 设计者：风堇
> 版本：1.0.0
> 更新日期：2026-04-30

---

## 一、颜色系统

### 1.1 主色（Primary）

用于主要按钮、链接、进度条、选中状态。

| Token 名称 | CSS 变量 | Tailwind 映射 | 值 | 用途 |
|------------|----------|---------------|-----|------|
| primary-50 | `--color-primary-50` | `primary-50` | #eff6ff | 浅色背景 |
| primary-100 | `--color-primary-100` | `primary-100` | #dbeafe | 按钮背景（次要） |
| primary-500 | `--color-primary-500` | `primary-500` | #3b82f6 | 进度条、链接 |
| primary-600 | `--color-primary-600` | `primary-600` | #2563eb | 主要按钮 |
| primary-700 | `--color-primary-700` | `primary-700` | #1d4ed8 | 按钮悬停 |

### 1.2 中性色（Neutral）

用于文字、边框、背景。

| Token 名称 | CSS 变量 | Tailwind 映射 | 值 | 用途 |
|------------|----------|---------------|-----|------|
| neutral-50 | `--color-neutral-50` | `neutral-50` | #f9fafb | 页面背景 |
| neutral-100 | `--color-neutral-100` | `neutral-100` | #f3f4f6 | 卡片背景、禁用按钮 |
| neutral-200 | `--color-neutral-200` | `neutral-200` | #e5e7eb | 边框、进度条背景 |
| neutral-300 | `--color-neutral-300` | `neutral-300` | #d1d5db | 边框 |
| neutral-500 | `--color-neutral-500` | `neutral-500` | #6b7280 | 辅助文字 |
| neutral-600 | `--color-neutral-600` | `neutral-600` | #4b5563 | 标签文字 |
| neutral-700 | `--color-neutral-700` | `neutral-700` | #374151 | 正文文字 |
| neutral-900 | `--color-neutral-900` | `neutral-900` | #111827 | 标题文字 |

### 1.3 语义色（Semantic）

用于状态指示。

| Token 名称 | CSS 变量 | Tailwind 映射 | 值 | 用途 |
|------------|----------|---------------|-----|------|
| success-50 | `--color-success-50` | `success-50` | #f0fdf4 | 成功背景 |
| success-500 | `--color-success-500` | `success-500` | #22c55e | 完成状态 |
| success-600 | `--color-success-600` | `success-600` | #16a34a | 成功文字 |
| error-50 | `--color-error-50` | `error-50` | #fef2f2 | 错误背景 |
| error-500 | `--color-error-500` | `error-500` | #ef4444 | 失败状态 |
| error-600 | `--color-error-600` | `error-600` | #dc2626 | 错误文字 |
| warning-50 | `--color-warning-50` | `warning-50` | #fefce8 | 修改提示背景 |
| warning-300 | `--color-warning-300` | `warning-300` | #fde047 | 修改提示边框 |
| warning-600 | `--color-warning-600` | `warning-600` | #ca8a04 | 修改提示文字 |

---

## 二、字体系统

### 2.1 字体家族

| Token 名称 | CSS 变量 | 值 | 用途 |
|------------|----------|-----|------|
| font-sans | `--font-sans` | Geist Sans, system-ui, sans-serif | 正文 |
| font-mono | `--font-mono` | Geist Mono, ui-monospace, monospace | 代码 |

### 2.2 字号

| Token 名称 | CSS 变量 | Tailwind 类 | 值 | 用途 |
|------------|----------|-------------|-----|------|
| text-xs | `--text-xs` | `text-xs` | 12px / 0.75rem | 辅助文字、标签 |
| text-sm | `--text-sm` | `text-sm` | 14px / 0.875rem | 正文、表单标签 |
| text-base | `--text-base` | `text-base` | 16px / 1rem | 正文（默认） |
| text-lg | `--text-lg` | `text-lg` | 18px / 1.125rem | 小标题 |
| text-xl | `--text-xl` | `text-xl` | 20px / 1.25rem | 卡片标题 |
| text-2xl | `--text-2xl` | `text-2xl` | 24px / 1.5rem | 页面标题 |

### 2.3 字重

| Token 名称 | CSS 变量 | Tailwind 类 | 值 | 用途 |
|------------|----------|-------------|-----|------|
| font-normal | `--font-normal` | `font-normal` | 400 | 正文 |
| font-medium | `--font-medium` | `font-medium` | 500 | 标签、按钮 |
| font-semibold | `--font-semibold` | `font-semibold` | 600 | 标题 |
| font-bold | `--font-bold` | `font-bold` | 700 | 大标题 |

---

## 三、间距系统

### 3.1 基础间距

基于 4px 基准单位。

| Token 名称 | 值 | Tailwind 类 | 用途 |
|------------|-----|-------------|------|
| spacing-1 | 4px | `p-1`, `m-1`, `gap-1` | 微小间距 |
| spacing-2 | 8px | `p-2`, `m-2`, `gap-2` | 小间距 |
| spacing-3 | 12px | `p-3`, `m-3`, `gap-3` | 表单内间距 |
| spacing-4 | 16px | `p-4`, `m-4`, `gap-4` | 卡片内间距 |
| spacing-6 | 24px | `p-6`, `m-6`, `gap-6` | 区块间距 |
| spacing-8 | 32px | `p-8`, `m-8`, `gap-8` | 大区块间距 |

### 3.2 布局宽度

| Token 名称 | 值 | Tailwind 类 | 用途 |
|------------|-----|-------------|------|
| container-sm | 640px | `max-w-sm` | 小容器 |
| container-2xl | 672px | `max-w-2xl` | 表单、卡片 |
| container-7xl | 1280px | `max-w-7xl` | 页面主容器 |

---

## 四、圆角系统

| Token 名称 | 值 | Tailwind 类 | 用途 |
|------------|-----|-------------|------|
| radius-sm | 4px | `rounded` | 小元素 |
| radius-md | 8px | `rounded-lg` | 按钮、输入框、卡片 |
| radius-lg | 12px | `rounded-xl` | 大卡片 |
| radius-full | 9999px | `rounded-full` | 状态指示器、头像 |

---

## 五、阴影系统

| Token 名称 | 值 | Tailwind 类 | 用途 |
|------------|-----|-------------|------|
| shadow-sm | 0 1px 2px rgba(0,0,0,0.05) | `shadow-sm` | 卡片 |
| shadow-md | 0 4px 6px rgba(0,0,0,0.1) | `shadow-md` | 弹窗 |
| shadow-lg | 0 10px 15px rgba(0,0,0,0.1) | `shadow-lg` | 模态框 |

---

## 六、组件规范

### 6.1 按钮

#### 主要按钮（Primary）

```css
.btn-primary {
  background: var(--color-primary-600);
  color: white;
  padding: 12px 16px; /* py-3 px-4 */
  border-radius: var(--radius-md);
  font-weight: 500;
  transition: background 150ms;
}
.btn-primary:hover {
  background: var(--color-primary-700);
}
.btn-primary:disabled {
  background: var(--color-neutral-100);
  color: var(--color-neutral-500);
  cursor: not-allowed;
}
```

#### 次要按钮（Secondary）

```css
.btn-secondary {
  background: var(--color-neutral-100);
  color: var(--color-neutral-700);
  padding: 8px 12px; /* py-2 px-3 */
  border-radius: var(--radius-md);
  font-weight: 500;
}
.btn-secondary:hover {
  background: var(--color-neutral-200);
}
```

### 6.2 输入框

```css
.input {
  border: 1px solid var(--color-neutral-300);
  border-radius: var(--radius-md);
  padding: 8px 12px; /* py-2 px-3 */
  font-size: var(--text-sm);
  color: var(--color-neutral-900);
  background: white;
}
.input:focus {
  border-color: var(--color-primary-500);
  outline: none;
  ring: 2px var(--color-primary-500);
}
.input:disabled {
  background: var(--color-neutral-100);
}
```

### 6.3 卡片

```css
.card {
  background: white;
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-md);
  padding: 24px; /* p-6 */
  box-shadow: var(--shadow-sm);
}
```

### 6.4 进度条

```css
.progress-track {
  height: 16px; /* h-4 */
  background: var(--color-neutral-200);
  border-radius: var(--radius-full);
}
.progress-bar {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 300ms;
}
/* 状态色 */
.progress-bar.in-progress { background: var(--color-primary-500); }
.progress-bar.completed { background: var(--color-success-500); }
.progress-bar.failed { background: var(--color-error-500); }
```

---

## 七、可访问性规范

### 7.1 焦点状态

所有可交互元素必须有可见的焦点指示：

```css
.focus-ring {
  outline: none;
  ring-width: 2px;
  ring-color: var(--color-primary-500);
  ring-offset: 2px;
}
```

### 7.2 aria 属性

| 元素 | 必需 aria 属性 |
|------|----------------|
| 图标按钮 | `aria-label` 描述按钮功能 |
| 错误提示 | `aria-live="polite"` 动态提示 |
| 进度条 | `aria-valuenow`, `aria-valuemin`, `aria-valuemax` |
| 表单错误 | `aria-describedby` 关联错误消息 |

---

## 八、打印优化

```css
@media print {
  /* 增大字号 */
  .print-text { font-size: 14pt; }
  .print-title { font-size: 18pt; }

  /* 隐藏交互元素 */
  button, .connection-status { display: none; }

  /* 增强进度条可见性 */
  .progress-track { height: 20px; }

  /* 使用黑白打印 */
  * { color: black !important; }
}
```

---

## 九、Tailwind 配置扩展

在 `tailwind.config.ts` 中扩展以下配置：

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        neutral: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          900: '#111827',
        },
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a',
        },
        error: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
        },
        warning: {
          50: '#fefce8',
          300: '#fde047',
          600: '#ca8a04',
        },
      },
    },
  },
};

export default config;
```

---

## 十、实施优先级

| 优先级 | 任务 | 影响 |
|--------|------|------|
| P0 | 创建 Tailwind 配置扩展 | 设计一致性 |
| P0 | 封装 Button 组件 | 组件复用 |
| P1 | 封装 Input/Select 组件 | 组件复用 |
| P1 | 增加 aria 属性 | 可访问性 |
| P1 | 调整进度条高度 | 投影可见性 |
| P2 | 添加打印样式 | 打印场景 |

---

设计者：风堇