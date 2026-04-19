import { type FC } from "react";
import { type PostGridProps } from "../types";
import { PostCard } from "./PostCard";
import { Skeleton } from "./Skeleton";

export const PostGrid: FC<PostGridProps> = ({
  posts,
  loading,
  onMarkRead,
  onResetFilters,
  showEmpty,
}) => {
  if (loading) {
    return <Skeleton />;
  }

  if (showEmpty) {
    return (
      <p
        style={{
          color: "#3a3a3a",
          fontFamily: "'DM Mono', monospace",
          fontSize: "13px",
          letterSpacing: "0.06em",
        }}
      >
        Немає результатів ·{" "}
        <span
          style={{
            cursor: "pointer",
            textDecoration: "underline",
            textDecorationColor: "#2a2a2a",
          }}
          onClick={onResetFilters}
        >
          скинути фільтри
        </span>
      </p>
    );
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
        gap: "14px",
      }}
    >
      {posts.map((post, i) => (
        <PostCard key={post.id} post={post} index={i} onMarkRead={onMarkRead} />
      ))}
    </div>
  );
};
