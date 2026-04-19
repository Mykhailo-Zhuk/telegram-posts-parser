import { type FC } from "react";
import { type PillProps } from "../types";

export const Pill: FC<PillProps> = ({ active, children, onClick, badge }) => (
  <button
    onClick={onClick}
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: "6px",
      padding: "6px 14px",
      background: active ? "rgba(255,210,0,0.12)" : "rgba(255,255,255,0.04)",
      border: `1px solid ${active ? "rgba(255,210,0,0.5)" : "rgba(255,255,255,0.1)"}`,
      borderRadius: "2px",
      color: active ? "#ffd200" : "#888",
      fontFamily: "'DM Mono', monospace",
      fontSize: "11px",
      letterSpacing: "0.08em",
      textTransform: "uppercase",
      cursor: "pointer",
      transition: "all 0.15s",
      whiteSpace: "nowrap",
    }}
  >
    {children}
    {badge != null && (
      <span
        style={{
          background: active ? "#ffd200" : "#333",
          color: active ? "#0a0a0a" : "#888",
          borderRadius: "10px",
          padding: "1px 6px",
          fontSize: "10px",
          fontWeight: 600,
        }}
      >
        {badge}
      </span>
    )}
  </button>
);
