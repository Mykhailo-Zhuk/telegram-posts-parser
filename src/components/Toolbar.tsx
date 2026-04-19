import { type FC } from "react";
import { type ToolbarProps } from "../types";
import { Pill } from "./Pill";

export const Toolbar: FC<ToolbarProps> = ({
  search,
  onSearchChange,
  unreadOnly,
  onUnreadToggle,
  unreadCount,
  channels,
  activeChannel,
  onChannelSelect,
}) => (
  <div
    style={{
      marginTop: "16px",
      display: "flex",
      flexWrap: "wrap",
      gap: "10px",
      alignItems: "center",
    }}
  >
    {/* Search */}
    <div style={{ position: "relative" }}>
      <svg
        width="13"
        height="13"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#444"
        strokeWidth="2"
        style={{
          position: "absolute",
          left: "12px",
          top: "50%",
          transform: "translateY(-50%)",
          pointerEvents: "none",
        }}
      >
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
      <input
        type="text"
        placeholder="Пошук..."
        value={search}
        onChange={(e) => onSearchChange(e.target.value)}
        style={{
          padding: "7px 14px 7px 34px",
          background: "rgba(255,255,255,0.04)",
          border: "1px solid rgba(255,255,255,0.09)",
          borderRadius: "2px",
          color: "#e0ddd8",
          fontFamily: "'DM Mono', monospace",
          fontSize: "12px",
          transition: "border-color 0.2s",
          width: "200px",
        }}
      />
    </div>

    <div
      style={{
        width: "1px",
        height: "22px",
        background: "rgba(255,255,255,0.08)",
      }}
    />

    {/* Unread toggle */}
    <Pill
      active={unreadOnly}
      onClick={onUnreadToggle}
      badge={unreadOnly ? null : unreadCount || null}
    >
      Непрочитані
    </Pill>

    <div
      style={{
        width: "1px",
        height: "22px",
        background: "rgba(255,255,255,0.08)",
      }}
    />

    {/* Channel switcher */}
    <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
      {channels.map((ch) => (
        <Pill
          key={ch}
          active={activeChannel === ch}
          onClick={() => onChannelSelect(ch)}
        >
          {ch}
        </Pill>
      ))}
    </div>
  </div>
);
