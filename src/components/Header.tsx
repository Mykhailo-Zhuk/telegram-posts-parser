import { type FC } from "react";
import { type HeaderProps } from "../types";

export const Header: FC<HeaderProps> = ({
  filteredCount,
  totalCount,
  unreadCount,
  onMarkAllRead,
  children,
}) => (
  <header
    style={{
      padding: "48px 0 36px",
      borderBottom: "1px solid rgba(255,255,255,0.07)",
      marginBottom: "32px",
      animation: "fadeUp 0.4s ease both",
    }}
  >
    <div
      style={{
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "16px",
        marginBottom: "24px",
      }}
    >
      <div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "9px",
            marginBottom: "8px",
          }}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#ffd200"
            strokeWidth="1.8"
          >
            <path d="M21.198 2.433a2.242 2.242 0 00-1.022.215l-16.5 7.5a2.25 2.25 0 00.152 4.179l4.274 1.198 2.348 7.04a2.25 2.25 0 003.822.786l2.15-2.586 4.124 3.003a2.25 2.25 0 003.434-1.738l1.998-16.5a2.25 2.25 0 00-2.78-2.097z" />
          </svg>
          <span
            style={{
              fontFamily: "'DM Mono', monospace",
              fontSize: "10px",
              letterSpacing: "0.16em",
              color: "#ffd200",
              textTransform: "uppercase",
            }}
          >
            Telegram Digest
          </span>
        </div>
        <h1
          style={{
            fontFamily: "'Cormorant Garamond', Georgia, serif",
            fontSize: "clamp(26px, 5vw, 42px)",
            fontWeight: 300,
            letterSpacing: "-0.01em",
            lineHeight: 1.1,
            color: "#f5f2ed",
          }}
        >
          Огляд постів
        </h1>
      </div>

      {/* Counter + Mark all */}
      <div
        style={{
          textAlign: "right",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-end",
          gap: "10px",
        }}
      >
        <div>
          <div
            style={{
              fontFamily: "'DM Mono', monospace",
              fontSize: "30px",
              fontWeight: 300,
              color: "#ffd200",
              lineHeight: 1,
            }}
          >
            {filteredCount}
          </div>
          <div
            style={{
              fontFamily: "'DM Mono', monospace",
              fontSize: "10px",
              letterSpacing: "0.12em",
              color: "#444",
              textTransform: "uppercase",
              marginTop: "3px",
            }}
          >
            {filteredCount === totalCount ? "записів" : `з ${totalCount}`}
          </div>
        </div>
        {unreadCount > 0 && (
          <button
            onClick={onMarkAllRead}
            style={{
              background: "none",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "2px",
              cursor: "pointer",
              display: "inline-flex",
              alignItems: "center",
              gap: "5px",
              fontFamily: "'DM Mono', monospace",
              fontSize: "10px",
              letterSpacing: "0.1em",
              color: "#666",
              textTransform: "uppercase",
              padding: "5px 10px",
              transition: "all 0.15s",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = "#aaa";
              e.currentTarget.style.borderColor = "rgba(255,255,255,0.2)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = "#666";
              e.currentTarget.style.borderColor = "rgba(255,255,255,0.1)";
            }}
          >
            <svg
              width="10"
              height="10"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
            Всі прочитані
          </button>
        )}
      </div>
    </div>

    {/* Children (FetchForm + Toolbar) */}
    {children}
  </header>
);
