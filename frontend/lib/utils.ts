export function anonymizePhone(phone: string): string {
  // "+4712345678" → "+47 XXX XX 678"
  const cleaned = phone.replace(/\s/g, "");
  if (cleaned.length < 4) return phone;
  const last3 = cleaned.slice(-3);
  const prefix = cleaned.startsWith("+47") ? "+47" : cleaned.slice(0, 3);
  return `${prefix} XXX XX ${last3}`;
}

export function getStatus(step: string): "active" | "done" | "expired" {
  if (step === "done") return "done";
  if (step === "expired") return "expired";
  return "active";
}

export function timeAgo(dateStr: string): string {
  const date = new Date(dateStr);
  const diffMs = Date.now() - date.getTime();
  const diffMins = Math.floor(diffMs / 60_000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);
  if (diffMins < 1) return "Akkurat nå";
  if (diffMins < 60) return `${diffMins} min siden`;
  if (diffHours < 24) return `${diffHours} t siden`;
  if (diffDays === 1) return "I går";
  return `${diffDays} dager siden`;
}

export function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString("no-NO", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function isToday(dateStr: string): boolean {
  return new Date(dateStr).toDateString() === new Date().toDateString();
}
