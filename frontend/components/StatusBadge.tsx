import { getStatus } from "@/lib/utils";

const config = {
  active: {
    label: "Aktiv",
    className: "bg-green-50 text-green-700 ring-green-600/20",
  },
  done: {
    label: "Fullført",
    className: "bg-blue-50 text-blue-700 ring-blue-600/20",
  },
  expired: {
    label: "Utløpt",
    className: "bg-slate-100 text-slate-500 ring-slate-500/20",
  },
} as const;

export function StatusBadge({ step }: { step: string }) {
  const status = getStatus(step);
  const { label, className } = config[status];
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${className}`}
    >
      {label}
    </span>
  );
}
