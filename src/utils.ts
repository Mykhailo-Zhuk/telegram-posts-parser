import { type Post } from "./types";

export const ALL_CHANNELS = "Всі канали" as const;

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("uk-UA", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

export function uniqueChannels(posts: Post[]): string[] {
  return [ALL_CHANNELS, ...Array.from(new Set(posts.map((p) => p.channel)))];
}
