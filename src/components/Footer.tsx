import { type FC } from "react";

export const Footer: FC = () => (
  <footer
    style={{
      marginTop: "52px",
      paddingTop: "18px",
      borderTop: "1px solid rgba(255,255,255,0.05)",
      fontFamily: "'DM Mono', monospace",
      fontSize: "10px",
      letterSpacing: "0.08em",
      color: "#333",
      display: "flex",
      justifyContent: "space-between",
      flexWrap: "wrap",
      gap: "6px",
    }}
  >
    <span>Telegram Digest · AI-ревю на базі Claude</span>
    <span>posts_reviewed.json</span>
  </footer>
);
