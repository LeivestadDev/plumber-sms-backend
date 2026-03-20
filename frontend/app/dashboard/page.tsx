import Link from "next/link";
import { redirect } from "next/navigation";
import { getCustomerId } from "@/lib/getCustomerId";
import { fetchCustomer, fetchConversations } from "@/lib/api/server";
import { StatusBadge } from "@/components/StatusBadge";
import { anonymizePhone, timeAgo, isToday, formatDateTime } from "@/lib/utils";

function StatCard({
  label,
  value,
  sub,
  icon,
  highlight,
}: {
  label: string;
  value: string | number;
  sub?: string;
  icon: React.ReactNode;
  highlight?: boolean;
}) {
  return (
    <div
      className={`rounded-2xl border p-6 transition-shadow hover:shadow-md ${
        highlight
          ? "border-red-200 bg-red-50"
          : "border-slate-200 bg-white"
      }`}
    >
      <div className="flex items-start justify-between mb-4">
        <p className="text-sm font-medium text-slate-500">{label}</p>
        <div
          className={`w-9 h-9 rounded-xl flex items-center justify-center ${
            highlight ? "bg-red-100" : "bg-blue-50"
          }`}
        >
          {icon}
        </div>
      </div>
      <p
        className={`text-3xl font-bold tracking-tight ${
          highlight ? "text-red-600" : "text-slate-900"
        }`}
      >
        {value}
      </p>
      {sub && <p className="text-xs text-slate-400 mt-1.5">{sub}</p>}
    </div>
  );
}

export default async function DashboardPage() {
  const customerId = await getCustomerId();
  if (!customerId) redirect("/onboarding");

  let customer, conversations;
  try {
    [customer, conversations] = await Promise.all([
      fetchCustomer(customerId),
      fetchConversations(customerId),
    ]);
  } catch {
    return (
      <div className="rounded-2xl border border-amber-200 bg-amber-50 p-8 max-w-lg mx-auto mt-16 text-center">
        <h2 className="text-lg font-semibold text-amber-900 mb-2">Serveren starter opp</h2>
        <p className="text-sm text-amber-700 mb-4">
          Backend-serveren vår starter opp — dette tar vanligvis 30–60 sekunder. Prøv å laste siden på nytt.
        </p>
        <a href="/dashboard" className="inline-block bg-amber-600 hover:bg-amber-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors">
          Last inn på nytt
        </a>
      </div>
    );
  }

  const todayCount = conversations.filter((c) => isToday(c.created_at)).length;
  const lastConv = conversations[0];
  const recent = conversations.slice(0, 10);

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">
          {customer.company_name}
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          SMS-nummer:{" "}
          <span className="font-mono font-medium text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
            {customer.twilio_number}
          </span>
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <StatCard
          label="Samtaler i dag"
          value={todayCount}
          icon={
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          }
        />
        <StatCard
          label="Samtaler denne uken"
          value={customer.stats.conversations_last_7_days}
          icon={
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          }
        />
        <StatCard
          label="Akutte varsler"
          value={customer.stats.urgent_alerts_sent}
          highlight={customer.stats.urgent_alerts_sent > 0}
          icon={
            <svg
              className={`w-5 h-5 ${customer.stats.urgent_alerts_sent > 0 ? "text-red-500" : "text-blue-600"}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          }
        />
        <StatCard
          label="Siste samtale"
          value={lastConv ? timeAgo(lastConv.created_at) : "–"}
          sub={lastConv ? anonymizePhone(lastConv.caller_phone) : "Ingen samtaler ennå"}
          icon={
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
      </div>

      {/* Recent conversations */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="font-semibold text-slate-900">Siste samtaler</h2>
          <Link
            href="/dashboard/conversations"
            className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1 transition-colors"
          >
            Se alle
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>

        {recent.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
            <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <p className="font-semibold text-slate-700 mb-1">Ingen samtaler ennå</p>
            <p className="text-sm text-slate-400">Systemet er klart og venter på den første meldingen!</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50 text-left">
                  <th className="px-6 py-3 font-medium text-slate-500 text-xs uppercase tracking-wider">Telefon</th>
                  <th className="px-6 py-3 font-medium text-slate-500 text-xs uppercase tracking-wider">Problem</th>
                  <th className="px-6 py-3 font-medium text-slate-500 text-xs uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 font-medium text-slate-500 text-xs uppercase tracking-wider">Tidspunkt</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((conv, i) => (
                  <tr
                    key={conv.id}
                    className={`hover:bg-blue-50/50 transition-colors border-b border-slate-50 last:border-0 ${
                      i % 2 === 1 ? "bg-slate-50/50" : "bg-white"
                    }`}
                  >
                    <td className="px-6 py-3.5 font-mono text-slate-700 whitespace-nowrap">
                      <Link
                        href={`/dashboard/conversations/${conv.id}`}
                        className="hover:text-blue-600 hover:underline underline-offset-2"
                      >
                        {anonymizePhone(conv.caller_phone)}
                      </Link>
                    </td>
                    <td className="px-6 py-3.5 text-slate-600 max-w-xs">
                      <p className="truncate">
                        {conv.problem_description ?? (
                          <span className="text-slate-400 italic">Ikke beskrevet</span>
                        )}
                      </p>
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
      </div>
    </div>
  );
}
