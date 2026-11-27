
import { Search, Filter, X } from "lucide-react";

interface FilterToolbarProps {
  search: string;
  onSearchChange: (value: string) => void;

  status?: string;
  onStatusChange?: (value: string) => void;

  searchPlaceholder?: string;
}

export default function FilterToolbar({
  search,
  onSearchChange,
  status = "all",
  onStatusChange,
  searchPlaceholder = "Search...",
}: FilterToolbarProps) {
  const hasFilters = search !== "" || status !== "all";

  const clearFilters = () => {
    onSearchChange("");
    onStatusChange?.("all");
  };

  return (
    <div className="filter-toolbar">
      <div className="filter-search">
        <Search size={17} />

        <input
          type="text"
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder={searchPlaceholder}
          aria-label="Search"
        />

        {search && (
          <button
            type="button"
            className="filter-clear-search"
            onClick={() => onSearchChange("")}
            aria-label="Clear search"
          >
            <X size={15} />
          </button>
        )}
      </div>

      {onStatusChange && (
        <div className="filter-status">
          <Filter size={16} />

          <select
            value={status}
            onChange={(event) => onStatusChange(event.target.value)}
            aria-label="Filter by status"
          >
            <option value="all">All statuses</option>
            <option value="healthy">Healthy</option>
            <option value="warning">Warning</option>
            <option value="critical">Critical</option>
            <option value="offline">Offline</option>
          </select>
        </div>
      )}

      {hasFilters && (
        <button
          type="button"
          className="filter-reset"
          onClick={clearFilters}
        >
          <X size={14} />
          Reset
        </button>
      )}
    </div>
  );
}
