"use client";

import { useState, useTransition } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import type { Conversation } from "@/lib/api/types";
import { StatusBadge } from "@/components/StatusBadge";
import { anonymizePhone, formatDateTime } from "@/lib/utils";

const STATUS_TABS = [
  { label: "Alle", value: "" },
  { label: "Aktive", value: "active" },
  { label: "Fullførte", value: "done" },
  { label: "Utløpte", value: "expired" },
] as const;

export function ConversationsClient({
  conversations,
  currentStatus,
}: {
  conversations: Conversation[];
  currentStatus: string;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [query, setQuery] = useState("");
  const [, startTransition] = useTransition();

  function setStatus(value: string) {
    const params = new URLSearchParams();
    if (value) params.set("status", value);
    startTransition(() => {
      router.push(`${pathname}?${params.toString()}`);
    });
  }

  const filtered = query.trim()
    ? conversations.filter(
        (c) =>
          c.caller_phone.includes(query) ||
          c.problem_description?.toLowerCase().includes(query.toLowerCase()) ||
          c.address?.toLowerCase().includes(query.toLowerCase())
      )
    : conversations;

  return (
    <div>
      {/* Search + filter bar */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Søk på telefonnummer eller problem…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full rounded-xl border border-slate-200 pl-10 pr-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
          />
        </div>
        <div className="flex gap-1 bg-slate-100 rounded-xl p-1 shrink-0">
          {STATUS_TABS.map((tab) => (
            <button
              key={tab.value}
              onClick={() => setStatus(tab.value)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                currentStatus === tab.value
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 px-6 text-center">
            <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            {query ? (
              <>
                <p className="font-semibold text-slate-700 mb-1">Ingen treff</p>
                <p className="text-sm text-slate-400">Ingen samtaler matcher &ldquo;{query}&rdquo;</p>
              </>
            ) : (
              <>
                <p className="font-semibold text-slate-700 mb-1">Ingen samtaler ennå</p>
                <p className="text-sm text-slate-400">Systemet er klart og venter på den første meldingen!</p>
              </>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50 text-left">
                  <th className="px-6 py-3 font-medium text-slate-500 text-xs uppercase tracking-wider">Telefon</th>
                  <th className="px-6 py-3 font-medium text-slate-500 text-xs uppercase tracking-wider">Problem</th>
                  <th className="px-6 py-3 font-medium text-slate-500 text-xs uppercase tracking-wider">Adresse</th>
                  <th className="px-6 py-3 font-medium text-slate-500 text-xs uppercase tracking-wider">Hastegrad</th>
                  <th className="px-6 py-3 font-medium text-slate-500 text-xs uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 font-medium text-slate-500 text-xs uppercase tracking-wider">Tidspunkt</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((conv, i) => (
                  <tr
                    key={conv.id}
                    className={`hover:bg-blue-50/40 transition-colors border-b border-slate-50 last:border-0 group ${
                      i % 2 === 1 ? "bg-slate-50/60" : "bg-white"
                    }`}
                  >
                    <td className="px-6 py-3.5 font-mono text-slate-700 whitespace-nowrap">
                      <Link
                        href={`/dashboard/conversations/${conv.id}`}
                        className="group-hover:text-blue-600 transition-colors underline-offset-2 hover:underline"
                      >
                        {anonymizePhone(conv.caller_phone)}
                      </Link>
                    </td>
                    <td className="px-6 py-3.5 text-slate-600 max-w-xs">
                      <p className="truncate">
                        {conv.problem_description ?? (
                          <span className="text-slate-400 italic">–</span>
                        )}
                      </p>
                    </td>
                    <td className="px-6 py-3.5 text-slate-500 max-w-[140px]">
                      <p className="truncate">
                        {conv.address ?? <span className="text-slate-300">–</span>}
                      </p>
                    </td>
                    <td className="px-6 py-3.5">
                      {conv.urgency ? (
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${
                            conv.urgency === "akutt"
                              ? "bg-red-50 text-red-700 ring-red-600/20"
                              : "bg-yellow-50 text-yellow-700 ring-yellow-600/20"
                          }`}
                        >
                          {conv.urgency}
                        </span>
                      ) : (
                        <span className="text-slate-300">–</span>
                      )}
                    </td>
                    <td className="px-6 py-3.5">
                      <StatusBadge step={conv.current_step} />
                    </td>
                    <td className="px-6 py-3.5 text-slate-500 whitespace-nowrap">
                      {formatDateTime(conv.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="px-6 py-3 border-t border-slate-100 bg-slate-50">
          <p className="text-xs text-slate-400">
            {filtered.length} samtale{filtered.length !== 1 ? "r" : ""}
            {query && ` (filtrert fra ${conversations.length})`}
          </p>
        </div>
      </div>
    </div>
  );
}
