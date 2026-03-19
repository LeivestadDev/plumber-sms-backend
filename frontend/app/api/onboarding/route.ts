import { auth, clerkClient } from "@clerk/nextjs/server";
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const { userId } = await auth();
  if (!userId) {
    return NextResponse.json({ error: "Ikke innlogget" }, { status: 401 });
  }

  const baseUrl = process.env.NEXT_PUBLIC_API_URL;
  const apiKey = process.env.ADMIN_API_KEY;
  if (!baseUrl || !apiKey) {
    return NextResponse.json({ error: "Serverkonfigurasjon mangler" }, { status: 500 });
  }

  const body = await req.json();
  const { company_name, plumber_phone, calendly_url, greeting_message } = body;

  if (!company_name || !plumber_phone || !calendly_url) {
    return NextResponse.json({ error: "Påkrevde felter mangler" }, { status: 400 });
  }

  // Use the TWILIO_NUMBER from env as the assigned number
  const twilioNumber = process.env.TWILIO_NUMBER;
  if (!twilioNumber) {
    return NextResponse.json({ error: "Intet SMS-nummer er konfigurert" }, { status: 500 });
  }

  const payload: Record<string, unknown> = {
    company_name,
    plumber_phone,
    calendly_url,
    twilio_number: twilioNumber,
    is_active: true,
  };
  if (greeting_message) {
    payload.greeting_message = greeting_message;
  }

  const res = await fetch(`${baseUrl}/api/customers`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": apiKey,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    return NextResponse.json(
      { error: err.detail ?? `Backend feil ${res.status}` },
      { status: res.status }
    );
  }

  const customer = await res.json();

  // Store customerId in Clerk publicMetadata so getCustomerId() works
  const clerk = await clerkClient();
  await clerk.users.updateUserMetadata(userId, {
    publicMetadata: { customerId: customer.id },
  });

  return NextResponse.json(customer, { status: 201 });
}
