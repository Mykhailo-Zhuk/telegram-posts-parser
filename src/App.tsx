import { useState, useEffect, useCallback, type FC } from "react";
import { Header, FetchForm, Toolbar, PostGrid, Footer } from "./components";
import { type Post } from "./types";
import { ALL_CHANNELS, uniqueChannels } from "./utils";

const App: FC = () => {
  // ── State ──────────────────────────────────────────────────────
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>("");
  const [activeChannel, setChannel] = useState<string>(ALL_CHANNELS);
  const [unreadOnly, setUnreadOnly] = useState<boolean>(false);
  const [channelInput, setChannelInput] = useState<string>("");
  const [fetching, setFetching] = useState<boolean>(false);
  const [fetchError, setFetchError] = useState<string>("");

  // ── Computed ───────────────────────────────────────────────────
  const channels = uniqueChannels(posts);

  const filtered: Post[] = posts.filter((p) => {
    const matchChannel =
      activeChannel === ALL_CHANNELS || p.channel === activeChannel;
    const matchUnread = !unreadOnly || !p.read;
    const q = search.toLowerCase();
    const matchSearch =
      !q ||
      p.review.toLowerCase().includes(q) ||
      p.text.toLowerCase().includes(q);
    return matchChannel && matchUnread && matchSearch;
  });

  const unreadCount: number = posts.filter(
    (p) =>
      !p.read &&
      (activeChannel === ALL_CHANNELS || p.channel === activeChannel),
  ).length;

  // ── Effects ────────────────────────────────────────────────────
  useEffect(() => {
    fetch("../posts_reviewed.json")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data) => {
        setPosts(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load posts:", err);
        setPosts([]);
        setLoading(false);
      });
  }, []);

  // ── Handlers ───────────────────────────────────────────────────
  const handleFetchPosts = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!channelInput.trim()) {
      setFetchError("Введи Username або ID групи");
      return;
    }

    setFetching(true);
    setFetchError("");

    try {
      const apiUrl = import.meta.env.VITE_API_URL || "/api";
      const response = await fetch(`${apiUrl}/fetch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ channel: channelInput.trim() }),
      });

      if (!response.ok) {
        const error = await response
          .json()
          .catch(() => ({ error: "Unknown error" }));
        throw new Error(error.error || `HTTP ${response.status}`);
      }

      const data = await response.json();
      setPosts(Array.isArray(data.posts) ? data.posts : []);
      setChannelInput("");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Помилка завантаження";
      setFetchError(message);
      console.error("Fetch error:", err);
    } finally {
      setFetching(false);
    }
  };

  const markRead = useCallback((id: number): void => {
    setPosts((prev) =>
      prev.map((p) => (p.id === id ? { ...p, read: true } : p)),
    );
  }, []);

  const markAllRead = useCallback((): void => {
    const visibleIds = new Set<number>(filtered.map((p) => p.id));
    setPosts((prev) =>
      prev.map((p) => (visibleIds.has(p.id) ? { ...p, read: true } : p)),
    );
  }, [filtered]);

  const resetFilters = (): void => {
    setSearch("");
    setUnreadOnly(false);
  };

  // ── Render ─────────────────────────────────────────────────────
  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Lora:ital,wght@0,400;0,500;0,600;1,400&family=Cormorant+Garamond:wght@300;400;500;600&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0a0a0a; color: #e0ddd8; font-family: 'Lora', Georgia, serif; min-height: 100vh; }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0%,100% { opacity:0.35; } 50% { opacity:0.12; } }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 2px; }
        input::placeholder { color: #444; }
        input:focus { outline: none; border-color: rgba(255,210,0,0.4) !important; }
        button:focus-visible { outline: 2px solid rgba(255,210,0,0.5); outline-offset: 2px; }
      `}</style>

      {/* Grain overlay */}
      <div
        style={{
          position: "fixed",
          inset: 0,
          pointerEvents: "none",
          zIndex: 100,
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E")`,
          opacity: 0.5,
        }}
      />

      <div
        style={{ maxWidth: "1100px", margin: "0 auto", padding: "0 24px 72px" }}
      >
        {/* Header */}
        <Header
          filteredCount={filtered.length}
          totalCount={posts.length}
          unreadCount={unreadCount}
          onMarkAllRead={markAllRead}
        >
          {/* Fetch Form */}
          <FetchForm
            channelInput={channelInput}
            onChannelChange={setChannelInput}
            onSubmit={handleFetchPosts}
            fetching={fetching}
            error={fetchError}
          />

          {/* Toolbar */}
          <Toolbar
            search={search}
            onSearchChange={setSearch}
            unreadOnly={unreadOnly}
            onUnreadToggle={() => setUnreadOnly((v) => !v)}
            unreadCount={unreadCount}
            channels={channels}
            activeChannel={activeChannel}
            onChannelSelect={setChannel}
          />
        </Header>

        {/* Post Grid */}
        <PostGrid
          posts={filtered}
          loading={loading}
          onMarkRead={markRead}
          onResetFilters={resetFilters}
          showEmpty={filtered.length === 0 && !loading}
        />

        {/* Footer */}
        <Footer />
      </div>
    </>
  );
};

export default App;
