import { currentUser } from "@clerk/nextjs/server";
import Stripe from "stripe";
import Link from "next/link";
import BillingActions from "./BillingActions";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

function formatDate(ts: number) {
  return new Date(ts * 1000).toLocaleDateString("nb-NO", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function getPlanName(priceId: string): string {
  if (priceId === process.env.STRIPE_PILOT_PRICE_ID) return "Pilot";
  if (priceId === process.env.STRIPE_STANDARD_PRICE_ID) return "Standard";
  return "Ukjent plan";
}

export default async function BillingPage({
  searchParams,
}: {
  searchParams: { success?: string };
}) {
  const user = await currentUser();
  const stripeCustomerId = user?.publicMetadata?.stripeCustomerId as string | undefined;

  let subscription: Stripe.Subscription | null = null;
  let planName = "";
  let isPilot = false;

  if (stripeCustomerId) {
    const { data } = await stripe.subscriptions.list({
      customer: stripeCustomerId,
      status: "all",
      limit: 1,
    });
    const active = data.find((s) => s.status === "active" || s.status === "trialing");
    if (active) {
      subscription = active;
      const priceId = active.items.data[0]?.price.id ?? "";
      planName = getPlanName(priceId);
      isPilot = planName === "Pilot";
    }
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-slate-900 mb-8">Fakturering</h1>

      {searchParams.success && (
        <div className="bg-green-50 border border-green-200 text-green-700 rounded-xl px-5 py-4 mb-6 text-sm">
          Abonnementet er aktivert. Velkommen til SvarDirekte!
        </div>
      )}

      {subscription ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-sm text-slate-500 mb-1">Nåværende plan</p>
              <p className="text-2xl font-bold text-slate-900">{planName}</p>
            </div>
            <span
              className={`text-xs font-bold px-3 py-1 rounded-full ${
                subscription.status === "trialing"
                  ? "bg-amber-100 text-amber-700"
                  : "bg-green-100 text-green-700"
              }`}
            >
              {subscription.status === "trialing" ? "PRØVEPERIODE" : "AKTIV"}
            </span>
          </div>

          <div className="grid sm:grid-cols-2 gap-6 py-6 border-t border-slate-100">
            {subscription.status === "trialing" && subscription.trial_end && (
              <div>
                <p className="text-sm text-slate-500 mb-1">Prøveperiode slutter</p>
                <p className="font-semibold text-slate-900">
                  {formatDate(subscription.trial_end)}
                </p>
              </div>
            )}
            {subscription.items.data[0]?.current_period_end && (
              <div>
                <p className="text-sm text-slate-500 mb-1">Neste betaling</p>
                <p className="font-semibold text-slate-900">
                  {formatDate(subscription.items.data[0].current_period_end)}
                </p>
              </div>
            )}
          </div>

          <BillingActions isPilot={isPilot} hasSubscription />
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center">
          <p className="text-slate-500 mb-4">Du har ingen aktiv plan.</p>
          <Link
            href="/pricing"
            className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-5 py-2.5 rounded-lg transition-colors"
          >
            Velg en plan
          </Link>
        </div>
      )}
    </div>
  );
}
