import { type FC, useState, type MouseEvent } from "react";
import { type PostCardProps } from "../types";
import { formatDate } from "../utils";

export const PostCard: FC<PostCardProps> = ({ post, index, onMarkRead }) => {
  const [imgError, setImgError] = useState<boolean>(false);
  const isUnread = !post.read;

  const handleMouseEnter = (e: MouseEvent<HTMLElement>): void => {
    e.currentTarget.style.borderColor = "rgba(255,210,0,0.4)";
    e.currentTarget.style.transform = "translateY(-2px)";
  };

  const handleMouseLeave = (e: MouseEvent<HTMLElement>): void => {
    e.currentTarget.style.borderColor = isUnread
      ? "rgba(255,210,0,0.18)"
      : "rgba(255,255,255,0.06)";
    e.currentTarget.style.transform = "translateY(0)";
  };

  return (
    <article
      style={{
        background: isUnread
          ? "rgba(255,210,0,0.03)"
          : "rgba(255,255,255,0.02)",
        border: `1px solid ${isUnread ? "rgba(255,210,0,0.18)" : "rgba(255,255,255,0.06)"}`,
        borderRadius: "2px",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        transition: "border-color 0.2s, transform 0.2s",
        animation: "fadeUp 0.5s ease both",
        animationDelay: `${index * 0.07}s`,
        position: "relative",
      }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Unread dot */}
      {isUnread && (
        <div
          style={{
            position: "absolute",
            top: "12px",
            right: "12px",
            width: "7px",
            height: "7px",
            borderRadius: "50%",
            background: "#ffd200",
            boxShadow: "0 0 6px rgba(255,210,0,0.6)",
            zIndex: 2,
          }}
        />
      )}

      {/* Photo */}
      {post.photo && !imgError && (
        <div
          style={{
            position: "relative",
            aspectRatio: "16/9",
            overflow: "hidden",
          }}
        >
          <img
            src={post.photo}
            alt=""
            onError={() => setImgError(true)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              display: "block",
              filter: "brightness(0.88) saturate(0.8)",
            }}
          />
          <div
            style={{
              position: "absolute",
              inset: 0,
              background:
                "linear-gradient(to top, rgba(10,10,10,0.65) 0%, transparent 55%)",
            }}
          />
        </div>
      )}

      {/* Content */}
      <div
        style={{
          padding: "18px 20px 16px",
          flex: 1,
          display: "flex",
          flexDirection: "column",
          gap: "10px",
        }}
      >
        {/* Meta */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span
            style={{
              fontFamily: "'DM Mono', monospace",
              fontSize: "10px",
              letterSpacing: "0.1em",
              color: "#555",
              textTransform: "uppercase",
            }}
          >
            {post.channel}
          </span>
          <span style={{ color: "#2a2a2a" }}>·</span>
          <time
            dateTime={post.date}
            style={{
              fontFamily: "'DM Mono', monospace",
              fontSize: "10px",
              letterSpacing: "0.1em",
              color: "#555",
              textTransform: "uppercase",
            }}
          >
            {formatDate(post.date)}
          </time>
        </div>

        {/* Review */}
        <p
          style={{
            fontSize: "14.5px",
            lineHeight: "1.65",
            color: isUnread ? "#e8e5e0" : "#9a9590",
            margin: 0,
            fontFamily: "'Lora', Georgia, serif",
            flex: 1,
          }}
        >
          {post.review}
        </p>

        {/* Actions */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginTop: "4px",
          }}
        >
          <a
            href={post.link}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "5px",
              fontSize: "11px",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "#ffd200",
              textDecoration: "none",
              fontFamily: "'DM Mono', monospace",
              transition: "opacity 0.15s",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.6")}
            onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
          >
            <svg
              width="11"
              height="11"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
            >
              <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6" />
              <polyline points="15 3 21 3 21 9" />
              <line x1="10" y1="14" x2="21" y2="3" />
            </svg>
            Відкрити
          </a>

          {isUnread && (
            <button
              onClick={() => onMarkRead(post.id)}
              style={{
                background: "none",
                border: "none",
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: "4px",
                fontFamily: "'DM Mono', monospace",
                fontSize: "10px",
                letterSpacing: "0.08em",
                color: "#555",
                textTransform: "uppercase",
                padding: 0,
                transition: "color 0.15s",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.color = "#888")}
              onMouseLeave={(e) => (e.currentTarget.style.color = "#555")}
            >
              <svg
                width="11"
                height="11"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.2"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
              Прочитано
            </button>
          )}
        </div>
      </div>
    </article>
  );
};
