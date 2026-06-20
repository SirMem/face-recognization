# VisionAttend — 决策 ADR

## ADR-001: 导航方案使用 qfluentwidgets NavigationInterface

- **状态**: 已采纳
- **日期**: 2026-06-17
- **驱动因素**: 避免手写 SideNav，复用成熟组件的展开/收起/高亮/底部卡片功能
- **权衡**: 牺牲对 Figma 侧栏样式的精确还原，通过 QSS 覆盖弥补
- **替代方案**: 手写 SideNav Widget（完全还原 Figma，但开发维护成本高）

