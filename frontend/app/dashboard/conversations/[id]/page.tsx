import Link from "next/link";
import { notFound } from "next/navigation";
import { getCustomerId } from "@/lib/getCustomerId";
import { fetchConversations, fetchMessages } from "@/lib/api/server";
import { StatusBadge } from "@/components/StatusBadge";
import { anonymizePhone, formatDateTime } from "@/lib/utils";

export default async function ConversationDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const conversationId = parseInt(params.id, 10);
  if (isNaN(conversationId)) notFound();

  const customerId = await getCustomerId();
  if (!customerId) notFound();

  // Fetch messages and the conversation list to find this one
  const [messages, allConversations] = await Promise.all([
    fetchMessages(conversationId),
    fetchConversations(customerId),
  ]);

  const conv = allConversations.find((c) => c.id === conversationId);
  if (!conv) notFound();

  return (
    <div className="max-w-2xl">
      {/* Back */}
      <Link
        href="/dashboard/conversations"
        className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-900 mb-6"
      >
        ← Tilbake til samtaler
      </Link>

      {/* Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-1">
              Innringer
            </p>
            <p className="text-lg font-mono font-semibold text-slate-900">
              {anonymizePhone(conv.caller_phone)}
            </p>
          </div>
          <StatusBadge step={conv.current_step} />
        </div>
        <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
          {conv.problem_description && (
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-0.5">
                Problem
              </p>
              <p className="text-slate-700">{conv.problem_description}</p>
            </div>
          )}
          {conv.address && (
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-0.5">
                Adresse
              </p>
              <p className="text-slate-700">{conv.address}</p>
            </div>
          )}
          {conv.urgency && (
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-0.5">
                Hastegrad
              </p>
              <p
                className={`font-medium ${
                  conv.urgency === "akutt" ? "text-red-600" : "text-yellow-700"
                }`}
              >
                {conv.urgency}
              </p>
            </div>
          )}
          <div>
            <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-0.5">
              Startet
            </p>
            <p className="text-slate-700">{formatDateTime(conv.created_at)}</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <h2 className="font-semibold text-slate-900 mb-3">
        Meldingshistorikk
        <span className="ml-2 text-sm font-normal text-slate-400">
          ({messages.length} meldinger)
        </span>
      </h2>

      {messages.length === 0 ? (
        <p className="text-slate-400 text-sm">Ingen meldinger funnet.</p>
      ) : (
        <div className="space-y-3">
          {messages.map((msg) => {
            const isInbound = msg.direction === "inbound";
            return (
              <div
                key={msg.id}
                className={`flex ${isInbound ? "justify-start" : "justify-end"}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2.5 ${
                    isInbound
                      ? "bg-slate-100 text-slate-900 rounded-tl-sm"
                      : "bg-blue-600 text-white rounded-tr-sm"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.body}</p>
                  <p
                    className={`text-xs mt-1 ${
                      isInbound ? "text-slate-400" : "text-blue-200"
                    }`}
                  >
                    {formatDateTime(msg.created_at)}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
