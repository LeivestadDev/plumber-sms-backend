/**
 * Server-side API helpers using fetch() so Next.js can cache/dedupe requests.
 * Never import this file from a client component.
 */
import type { Customer, CustomerPatch, CustomerWithStats, Conversation, Message } from "./types";

function getConfig() {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL;
  const apiKey = process.env.ADMIN_API_KEY;
  if (!baseUrl) throw new Error("NEXT_PUBLIC_API_URL is not set");
  if (!apiKey) throw new Error("ADMIN_API_KEY is not set");
  return { baseUrl, apiKey };
}

function headers() {
  const { apiKey } = getConfig();
  return { "Content-Type": "application/json", "X-API-Key": apiKey };
}

function withTimeout(ms: number): AbortSignal {
  return AbortSignal.timeout(ms);
}

export async function fetchCustomer(id: number): Promise<CustomerWithStats> {
  const { baseUrl } = getConfig();
  const res = await fetch(`${baseUrl}/api/customers/${id}`, {
    headers: headers(),
    next: { revalidate: 60 },
    signal: withTimeout(8000),
  });
  if (res.status === 404) throw new Error("CUSTOMER_NOT_FOUND");
  if (!res.ok) throw new Error(`fetchCustomer failed: ${res.status}`);
  return res.json();
}

export async function fetchConversations(
  customerId: number,
  status?: string
): Promise<Conversation[]> {
  const { baseUrl } = getConfig();
  const url = new URL(`${baseUrl}/api/customers/${customerId}/conversations`);
  if (status) url.searchParams.set("status", status);
  const res = await fetch(url.toString(), {
    headers: headers(),
    next: { revalidate: 30 },
    signal: withTimeout(8000),
  });
  if (!res.ok) throw new Error(`fetchConversations failed: ${res.status}`);
  return res.json();
}

export async function fetchMessages(conversationId: number): Promise<Message[]> {
  const { baseUrl } = getConfig();
  const res = await fetch(`${baseUrl}/api/conversations/${conversationId}/messages`, {
    headers: headers(),
    next: { revalidate: 30 },
    signal: withTimeout(8000),
  });
  if (!res.ok) throw new Error(`fetchMessages failed: ${res.status}`);
  return res.json();
}

export async function updateCustomer(id: number, body: CustomerPatch): Promise<Customer> {
  const { baseUrl } = getConfig();
  const res = await fetch(`${baseUrl}/api/customers/${id}`, {
    method: "PATCH",
    headers: headers(),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`updateCustomer failed: ${res.status}`);
  return res.json();
}
