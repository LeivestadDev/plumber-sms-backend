import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";
import { clerkClient } from "@clerk/nextjs/server";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

async function patchCustomer(customerId: string, body: Record<string, unknown>) {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL;
  const apiKey = process.env.ADMIN_API_KEY;
  const res = await fetch(`${baseUrl}/api/customers/${customerId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", "X-API-Key": apiKey! },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    console.error(`patchCustomer failed for ${customerId}: ${res.status}`);
  }
}

export async function POST(req: NextRequest) {
  const body = await req.text();
  const sig = req.headers.get("stripe-signature");

  if (!sig) {
    return NextResponse.json({ error: "No signature" }, { status: 400 });
  }

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch {
    return NextResponse.json({ error: "Invalid signature" }, { status: 400 });
  }

  switch (event.type) {
    case "checkout.session.completed": {
      const session = event.data.object as Stripe.Checkout.Session;
      const { customerId, clerkUserId } = session.metadata ?? {};
      const stripeCustomerId = session.customer as string;
      const stripeSubscriptionId = session.subscription as string;

      if (customerId) {
        await patchCustomer(customerId, { is_active: true });
      }

      if (clerkUserId && stripeCustomerId) {
        const clerk = await clerkClient();
        const user = await clerk.users.getUser(clerkUserId);
        await clerk.users.updateUser(clerkUserId, {
          publicMetadata: {
            ...user.publicMetadata,
            stripeCustomerId,
            stripeSubscriptionId,
          },
        });
      }
      break;
    }

    case "customer.subscription.deleted": {
      const sub = event.data.object as Stripe.Subscription;
      const { customerId, clerkUserId } = sub.metadata ?? {};

      if (customerId) {
        await patchCustomer(customerId, { is_active: false });
      }

      if (clerkUserId) {
        const clerk = await clerkClient();
        const user = await clerk.users.getUser(clerkUserId);
        const meta = { ...user.publicMetadata };
        delete (meta as Record<string, unknown>).stripeSubscriptionId;
        await clerk.users.updateUser(clerkUserId, { publicMetadata: meta });
      }
      break;
    }

    case "invoice.payment_failed": {
      const invoice = event.data.object as Stripe.Invoice;
      console.log("Payment failed — customer:", invoice.customer, "invoice:", invoice.id);
      break;
    }
  }

  return NextResponse.json({ received: true });
}
