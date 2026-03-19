import apiClient from "./client";
import type { Conversation, ConversationStatus, Message } from "./types";

export async function listConversations(
  customerId: number,
  status?: ConversationStatus
): Promise<Conversation[]> {
  const params = status ? { status } : {};
  const { data } = await apiClient.get<Conversation[]>(
    `/api/customers/${customerId}/conversations`,
    { params }
  );
  return data;
}

export async function listMessages(conversationId: number): Promise<Message[]> {
  const { data } = await apiClient.get<Message[]>(
    `/api/conversations/${conversationId}/messages`
  );
  return data;
}
