import Link from "next/link";
import PricingButton from "./PricingButton";

const PILOT_FEATURES = [
  "1 SMS-nummer",
  "Automatisk samtaleflyt",
  "Akuttvarsler",
  "Calendly-integrasjon",
  "14 dagers gratis prøve",
];

const STANDARD_FEATURES = [
  "Alt i Pilot",
  "Avansert statistikk",
  "Prioritert support",
  "Tilpasset onboarding",
];

export default function PricingPage({
  searchParams,
}: {
  searchParams: { canceled?: string };
}) {
  return (
    <div className="min-h-screen bg-white">
      <nav className="border-b border-slate-100 bg-white">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-blue-600">
            SvarDirekte
          </Link>
          <Link href="/sign-in" className="text-sm text-slate-600 hover:text-slate-900 font-medium transition-colors">
            Logg inn
          </Link>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-20">
        <div className="text-center mb-14">
          <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 mb-4">
            Velg din plan
          </h1>
          <p className="text-slate-500 max-w-xl mx-auto text-lg">
            Ingen bindingstid. Avbryt når som helst.
          </p>
          {searchParams.canceled && (
            <div className="mt-6 inline-flex items-center gap-2 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-xl px-5 py-3">
              <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Betalingen ble avbrutt — ingen belastning har skjedd.
            </div>
          )}
        </div>

        <div className="grid md:grid-cols-2 gap-8 items-start">
          {/* Pilot — featured */}
          <div className="border-2 border-blue-300 bg-gradient-to-br from-blue-50 to-white rounded-2xl p-8 relative shadow-md shadow-blue-100">
            <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
              <span className="bg-orange-500 text-white text-xs font-bold px-4 py-1.5 rounded-full shadow-sm whitespace-nowrap">
                MEST POPULÆR
              </span>
            </div>
            <div className="inline-block bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full mb-4 mt-2">
              PILOT
            </div>
            <div className="text-4xl font-extrabold text-slate-900 mb-1">
              299 kr
              <span className="text-lg font-normal text-slate-500">/mnd</span>
            </div>
            <p className="text-slate-500 text-sm mb-6">Begrenset tilbud for de første 5 kundene</p>
            <ul className="space-y-3 mb-8">
              {PILOT_FEATURES.map((f) => (
                <li key={f} className="flex items-center gap-3 text-sm text-slate-700">
                  <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold shrink-0">✓</span>
                  {f}
                </li>
              ))}
            </ul>
            <PricingButton plan="pilot" label="Start 14 dagers gratis prøve" primary />
          </div>

          {/* Standard */}
          <div className="border border-slate-200 rounded-2xl p-8">
            <div className="inline-block bg-slate-100 text-slate-600 text-xs font-bold px-3 py-1 rounded-full mb-4">
              STANDARD
            </div>
            <div className="text-4xl font-extrabold text-slate-900 mb-1">
              1 499 kr
              <span className="text-lg font-normal text-slate-500">/mnd</span>
            </div>
            <p className="text-slate-500 text-sm mb-6">For etablerte håndverkere og servicevirksomheter</p>
            <ul className="space-y-3 mb-8">
              {STANDARD_FEATURES.map((f) => (
                <li key={f} className="flex items-center gap-3 text-sm text-slate-700">
                  <span className="w-5 h-5 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center text-xs font-bold shrink-0">✓</span>
                  {f}
                </li>
              ))}
            </ul>
            <PricingButton plan="standard" label="Kom i gang" />
          </div>
        </div>

        {/* Trust signals */}
        <div className="mt-10 flex flex-wrap justify-center items-center gap-6 text-sm text-slate-500">
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            30 dagers pengene-tilbake-garanti
          </span>
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            Sikker betaling via Stripe
          </span>
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
            </svg>
            Ingen binding, avbryt når som helst
          </span>
        </div>

        {/* Integrations */}
        <div className="mt-14 pt-10 border-t border-slate-100 text-center">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-6">
            Integrerer med
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
            {[
              { name: "Calendly", icon: "🗓️" },
              { name: "Twilio", icon: "💬" },
              { name: "46elks", icon: "📱" },
            ].map(({ name, icon }) => (
              <div key={name} className="flex items-center gap-2">
                <span className="text-2xl">{icon}</span>
                <span className="font-bold text-slate-600">{name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
