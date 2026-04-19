import { type FC } from "react";
import { type FetchFormProps } from "../types";

export const FetchForm: FC<FetchFormProps> = ({
  channelInput,
  onChannelChange,
  onSubmit,
  fetching,
  error,
}) => (
  <>
    <form
      onSubmit={onSubmit}
      style={{
        marginTop: "24px",
        display: "flex",
        gap: "10px",
        alignItems: "flex-end",
        flexWrap: "wrap",
        marginBottom: "16px",
      }}
    >
      <div style={{ flex: 1, minWidth: "200px" }}>
        <label
          style={{
            display: "block",
            fontFamily: "'DM Mono', monospace",
            fontSize: "10px",
            letterSpacing: "0.1em",
            color: "#555",
            textTransform: "uppercase",
            marginBottom: "6px",
          }}
        >
          Канал або група
        </label>
        <input
          type="text"
          placeholder="@channel_name або -1001234567890"
          value={channelInput}
          onChange={(e) => onChannelChange(e.target.value)}
          disabled={fetching}
          style={{
            width: "100%",
            padding: "8px 12px",
            background: "rgba(255,255,255,0.04)",
            border: `1px solid ${
              error ? "rgba(255,100,100,0.5)" : "rgba(255,255,255,0.09)"
            }`,
            borderRadius: "2px",
            color: "#e0ddd8",
            fontFamily: "'DM Mono', monospace",
            fontSize: "12px",
            transition: "border-color 0.2s",
            opacity: fetching ? 0.6 : 1,
          }}
        />
      </div>
      <button
        type="submit"
        disabled={fetching || !channelInput.trim()}
        style={{
          padding: "8px 18px",
          background: fetching ? "rgba(255,210,0,0.1)" : "rgba(255,210,0,0.12)",
          border: `1px solid ${
            fetching ? "rgba(255,210,0,0.3)" : "rgba(255,210,0,0.5)"
          }`,
          borderRadius: "2px",
          color: "#ffd200",
          fontFamily: "'DM Mono', monospace",
          fontSize: "11px",
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          cursor: fetching ? "not-allowed" : "pointer",
          opacity: fetching ? 0.6 : 1,
          transition: "all 0.15s",
        }}
        onMouseEnter={(e) => {
          if (!fetching && channelInput.trim()) {
            e.currentTarget.style.background = "rgba(255,210,0,0.18)";
            e.currentTarget.style.borderColor = "rgba(255,210,0,0.6)";
          }
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = "rgba(255,210,0,0.12)";
          e.currentTarget.style.borderColor = "rgba(255,210,0,0.5)";
        }}
      >
        {fetching ? "Завантаження..." : "Завантажити"}
      </button>
    </form>

    {error && (
      <div
        style={{
          padding: "10px 12px",
          background: "rgba(255,100,100,0.08)",
          border: "1px solid rgba(255,100,100,0.3)",
          borderRadius: "2px",
          color: "#ff6464",
          fontFamily: "'DM Mono', monospace",
          fontSize: "11px",
          marginBottom: "16px",
        }}
      >
        ❌ {error}
      </div>
    )}
  </>
);
