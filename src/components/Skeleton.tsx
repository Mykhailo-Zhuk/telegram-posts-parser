import { type FC } from "react";

export const Skeleton: FC = () => (
  <div
    style={{
      display: "grid",
      gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
      gap: "16px",
    }}
  >
    {([1, 2, 3, 4] as const).map((i) => (
      <div
        key={i}
        style={{
          background: "rgba(255,255,255,0.03)",
          border: "1px solid rgba(255,255,255,0.05)",
          borderRadius: "2px",
          height: "200px",
          animation: "pulse 1.5s ease-in-out infinite",
          animationDelay: `${i * 0.1}s`,
        }}
      />
    ))}
  </div>
);
