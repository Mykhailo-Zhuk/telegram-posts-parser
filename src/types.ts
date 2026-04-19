export interface Post {
  id: number;
  channel: string;
  date: string; // ISO 8601
  text: string;
  review: string;
  link: string;
  photo: string | null;
  read: boolean;
}

export interface PillProps {
  active: boolean;
  children: React.ReactNode;
  onClick: () => void;
  badge?: number | null;
}

export interface PostCardProps {
  post: Post;
  index: number;
  onMarkRead: (id: number) => void;
}

export interface FetchFormProps {
  channelInput: string;
  onChannelChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  fetching: boolean;
  error: string;
}

export interface ToolbarProps {
  search: string;
  onSearchChange: (value: string) => void;
  unreadOnly: boolean;
  onUnreadToggle: () => void;
  unreadCount: number;
  channels: string[];
  activeChannel: string;
  onChannelSelect: (channel: string) => void;
}

export interface HeaderProps {
  filteredCount: number;
  totalCount: number;
  unreadCount: number;
  onMarkAllRead: () => void;
  children?: React.ReactNode;
}

export interface PostGridProps {
  posts: Post[];
  loading: boolean;
  onMarkRead: (id: number) => void;
  onResetFilters: () => void;
  showEmpty: boolean;
}
