import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";
import { auth } from "@clerk/nextjs/server";
import { getCustomerId } from "@/lib/getCustomerId";

export async function POST(req: NextRequest) {
  try {
    const { userId } = await auth();
    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const stripeKey = process.env.STRIPE_SECRET_KEY;
    if (!stripeKey) {
      console.error("[checkout] STRIPE_SECRET_KEY er ikke satt");
      return NextResponse.json({ error: "Betalingstjenesten er ikke konfigurert" }, { status: 500 });
    }

    const { plan } = await req.json();

    const priceIds: Record<string, string | undefined> = {
      pilot: process.env.STRIPE_PILOT_PRICE_ID,
      standard: process.env.STRIPE_STANDARD_PRICE_ID,
    };

    const priceId = priceIds[plan];
    if (!priceId) {
      console.error(`[checkout] Mangler price ID for plan "${plan}"`);
      return NextResponse.json({ error: `Ugyldig plan eller manglende price ID for "${plan}"` }, { status: 400 });
    }

    const customerId = await getCustomerId();
    const origin = req.headers.get("origin") ?? "http://localhost:3000";

    console.log(`[checkout] Oppretter session — plan: ${plan}, priceId: ${priceId}, customerId: ${customerId}, origin: ${origin}`);

    const stripe = new Stripe(stripeKey);
    const session = await stripe.checkout.sessions.create({
      mode: "subscription",
      line_items: [{ price: priceId, quantity: 1 }],
      subscription_data: {
        trial_period_days: plan === "pilot" ? 14 : undefined,
        metadata: {
          customerId: String(customerId ?? ""),
          clerkUserId: userId,
        },
      },
      metadata: {
        customerId: String(customerId ?? ""),
        clerkUserId: userId,
      },
      success_url: `${origin}/dashboard/billing?success=1`,
      cancel_url: `${origin}/pricing?canceled=1`,
    });

    console.log("[checkout] Session opprettet:", session.id);
    return NextResponse.json({ url: session.url });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    console.error("[checkout] Feil:", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
