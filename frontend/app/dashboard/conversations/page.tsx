import { getCustomerId } from "@/lib/getCustomerId";
import { fetchConversations } from "@/lib/api/server";
import { NoCustomerId } from "@/components/NoCustomerId";
import { ConversationsClient } from "./ConversationsClient";

export default async function ConversationsPage({
  searchParams,
}: {
  searchParams: { status?: string };
}) {
  const customerId = await getCustomerId();
  if (!customerId) return <NoCustomerId />;

  const status = searchParams.status ?? "";
  const conversations = await fetchConversations(
    customerId,
    status || undefined
  );

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Samtaler</h1>
        <p className="text-slate-500 text-sm mt-0.5">
          Full historikk over alle SMS-samtaler
        </p>
      </div>
      <ConversationsClient
        conversations={conversations}
        currentStatus={status}
      />
    </div>
  );
}
