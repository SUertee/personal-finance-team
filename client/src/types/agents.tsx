import type { ReactNode } from "react";
import { Brain, Heart, Shield, TrendingUp } from "lucide-react";

export type AgentType = "cfo" | "quant" | "coach" | "auditor";

export type AgentMeta = {
  id: AgentType;
  label: string;
  summary: string;
  prompt: string;
  badgeClass: string;
  icon: ReactNode;
};

export const AGENTS: AgentMeta[] = [
  {
    id: "cfo",
    label: "Agent A: CFO",
    summary: "总决策：预算、限制、优先级组合",
    prompt:
      "你是 Agent A：CFO（总决策）。输入：指标 + 异常 + 目标 + 历史表现。输出：本月策略组合（预算、限制、优先级）。用清晰要点输出，聚焦执行性。",
    badgeClass: "bg-slate-900 text-white",
    icon: <Brain className="w-4 h-4 text-white" />,
  },
  {
    id: "quant",
    label: "Agent B: Quant",
    summary: "量化分析：趋势/波动/异常/预测",
    prompt:
      "你是 Agent B：Quant Analyst（量化分析师）。工具调用：趋势/波动、异常检测、类别贡献、现金流预测。输出：诊断结论（结构性 vs 偶发）并列出证据点。",
    badgeClass: "bg-blue-600 text-white",
    icon: <TrendingUp className="w-4 h-4 text-white" />,
  },
  {
    id: "coach",
    label: "Agent C: Coach",
    summary: "行为干预：提醒规则 + 低摩擦习惯",
    prompt:
      "你是 Agent C：Behavior Coach（行为教练）。输入：消费习惯画像（冲动、夜间消费、商户集中度）。输出：干预计划（提醒规则、替代方案、低摩擦习惯）。",
    badgeClass: "bg-purple-600 text-white",
    icon: <Heart className="w-4 h-4 text-white" />,
  },
  {
    id: "auditor",
    label: "Agent D: Auditor",
    summary: "审计：规则校验 + 风险标签",
    prompt:
      "你是 Agent D：Auditor（审计师）。检查输出是否符合规则、建议是否可执行、JSON Schema 是否完整。输出：风险标签 & 可信度。",
    badgeClass: "bg-emerald-600 text-white",
    icon: <Shield className="w-4 h-4 text-white" />,
  },
];
