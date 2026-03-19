import Link from "next/link";
import LandingNav from "./LandingNav";
import SmsMockup from "./SmsMockup";
import FaqSection from "./FaqSection";

const STEPS = [
  {
    step: "1",
    icon: (
      <svg className="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    ),
    title: "Kunden sender en SMS",
    desc: "Kunden sender melding til ditt dedikerte SvarDirekte-nummer mens du er opptatt på jobb.",
  },
  {
    step: "2",
    icon: (
      <svg className="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    title: "AI svarer på sekunder",
    desc: "SvarDirekte svarer automatisk, avklarer hva kunden trenger og tilbyr ledige tider fra Calendly.",
  },
  {
    step: "3",
    icon: (
      <svg className="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    title: "Booking bekreftes automatisk",
    desc: "Kunden booker direkte i kalenderen din. Du får varsling og kan se historikken i dashboardet.",
  },
];

const TESTIMONIALS = [
  {
    quote: "Jeg mistet aldri en kunde, men nå er jeg sikker på det. SvarDirekte svarer mens jeg er under oppvasken med hendene fulle.",
    name: "Kjetil Andreassen",
    role: "Rørlegger, Bergen",
    initials: "KA",
  },
  {
    quote: "Satt opp på 10 minutter. Første booking kom samme dag. Det er akkurat det jeg trengte.",
    name: "Trond Henriksen",
    role: "Elektriker, Trondheim",
    initials: "TH",
  },
  {
    quote: "Kunder som sender SMS midt på natten får nå svar med én gang og booker time. Jeg vinner oppdraget før konkurrentene vet om det.",
    name: "Siri Moen",
    role: "Taktekker, Oslo",
    initials: "SM",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      <LandingNav />

      {/* Hero */}
      <section className="pt-28 pb-24 px-6 overflow-hidden">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left: copy */}
            <div>
              <div className="inline-flex items-center gap-2 bg-orange-50 text-orange-600 text-sm font-semibold px-4 py-1.5 rounded-full mb-6 border border-orange-100">
                <span className="w-2 h-2 rounded-full bg-orange-500 animate-pulse" />
                Nå i pilotperiode – begrenset antall plasser
              </div>
              <h1 className="text-5xl sm:text-6xl font-extrabold text-slate-900 leading-[1.1] mb-6 text-balance">
                Mist aldri en{" "}
                <span className="text-blue-600 relative">
                  kunde igjen
                  <svg className="absolute -bottom-2 left-0 w-full" viewBox="0 0 300 12" fill="none">
                    <path d="M2 8.5C50 3 150 1 298 8.5" stroke="#93c5fd" strokeWidth="3" strokeLinecap="round"/>
                  </svg>
                </span>
              </h1>
              <p className="text-xl text-slate-500 max-w-lg mb-10 leading-relaxed">
                SvarDirekte svarer automatisk på SMS fra kunder når du er opptatt – og booker dem direkte i kalenderen din. Du mister ikke oppdraget.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  href="/pricing"
                  className="bg-orange-500 hover:bg-orange-600 text-white font-bold px-8 py-4 rounded-xl text-lg transition-all duration-150 hover:scale-105 shadow-lg shadow-orange-200 text-center"
                >
                  Start 14 dagers gratis prøve
                </Link>
                <a
                  href="#how-it-works"
                  className="border border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-700 font-semibold px-8 py-4 rounded-xl text-lg transition-all duration-150 text-center"
                >
                  Se hvordan det fungerer
                </a>
              </div>
              <p className="text-sm text-slate-400 mt-4">
                Ingen kredittkort i prøveperioden · Avbryt når som helst
              </p>
            </div>

            {/* Right: SMS mockup */}
            <div className="flex justify-center lg:justify-end">
              <SmsMockup />
            </div>
          </div>
        </div>
      </section>

      {/* Trust bar */}
      <section className="py-8 px-6 border-y border-slate-100 bg-slate-50">
        <div className="max-w-4xl mx-auto">
          <p className="text-center text-xs font-semibold text-slate-400 uppercase tracking-widest mb-6">
            Integrerer sømløst med
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
            {[
              { name: "Calendly", icon: "🗓️" },
              { name: "Twilio", icon: "💬" },
              { name: "46elks", icon: "📱" },
            ].map(({ name, icon }) => (
              <div key={name} className="flex items-center gap-2">
                <span className="text-xl">{icon}</span>
                <span className="font-bold text-slate-600 text-sm">{name}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
              Slik fungerer SvarDirekte
            </h2>
            <p className="text-slate-500 max-w-xl mx-auto">
              Tre enkle steg – ingen koding, ingen teknisk oppsett.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {STEPS.map(({ step, icon, title, desc }) => (
              <div
                key={step}
                className="bg-white rounded-2xl p-8 shadow-sm border border-slate-100 hover:shadow-md hover:border-blue-100 transition-all duration-200 group"
              >
                <div className="w-14 h-14 bg-blue-50 group-hover:bg-blue-100 rounded-2xl flex items-center justify-center mb-5 transition-colors">
                  {icon}
                </div>
                <div className="text-xs font-bold text-blue-500 uppercase tracking-widest mb-2">
                  Steg {step}
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-3">{title}</h3>
                <p className="text-slate-500 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-24 px-6 bg-slate-50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
              Håndverkere elsker SvarDirekte
            </h2>
            <p className="text-slate-500">
              Over 40 norske fagfolk bruker SvarDirekte i dag.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {TESTIMONIALS.map(({ quote, name, role, initials }) => (
              <div
                key={name}
                className="bg-white rounded-2xl p-7 border border-slate-100 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex gap-1 mb-5">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <svg key={i} className="w-4 h-4 text-orange-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <p className="text-slate-700 text-sm leading-relaxed mb-6">
                  &ldquo;{quote}&rdquo;
                </p>
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center shrink-0">
                    <span className="text-white text-xs font-bold">{initials}</span>
                  </div>
                  <div>
                    <p className="font-semibold text-slate-900 text-sm">{name}</p>
                    <p className="text-slate-500 text-xs">{role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing preview */}
      <section id="pricing" className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
              Enkel, transparent prising
            </h2>
            <p className="text-slate-500 max-w-xl mx-auto">
              Ingen bindingstid, ingen skjulte kostnader. Start gratis i 14 dager.
            </p>
          </div>
          <div className="grid md:grid-cols-2 gap-8">
            {/* Pilot */}
            <div className="border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-white rounded-2xl p-8 relative overflow-hidden">
              <div className="absolute top-4 right-4 bg-orange-500 text-white text-[10px] font-bold px-2.5 py-1 rounded-full tracking-wide">
                MEST POPULÆR
              </div>
              <div className="inline-block bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full mb-4">
                PILOT
              </div>
              <div className="text-4xl font-extrabold text-slate-900 mb-1">
                299 kr
                <span className="text-lg font-normal text-slate-500">/mnd</span>
              </div>
              <p className="text-slate-500 text-sm mb-6">Begrenset tilbud for de første 50 kundene</p>
              <ul className="space-y-3 mb-8">
                {["1 SMS-nummer", "Automatisk samtaleflyt", "Akuttvarsler", "Calendly-integrasjon", "14 dagers gratis prøve"].map((f) => (
                  <li key={f} className="flex items-center gap-2.5 text-sm text-slate-700">
                    <span className="w-4 h-4 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold shrink-0">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
              <Link
                href="/pricing"
                className="block text-center bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl transition-all hover:scale-[1.02]"
              >
                Start gratis prøveperiode
              </Link>
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
                {["Alt i Pilot", "Avansert statistikk", "Prioritert support", "Tilpasset onboarding"].map((f) => (
                  <li key={f} className="flex items-center gap-2.5 text-sm text-slate-700">
                    <span className="w-4 h-4 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center text-xs font-bold shrink-0">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
              <Link
                href="/pricing"
                className="block text-center border border-slate-300 hover:border-slate-400 hover:bg-slate-50 text-slate-700 font-semibold py-3 rounded-xl transition-all"
              >
                Kom i gang
              </Link>
            </div>
          </div>
          <p className="text-center text-sm text-slate-400 mt-6">
            🛡️ 30 dagers pengene-tilbake-garanti · Ingen kredittkort i prøveperioden
          </p>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="py-24 px-6 bg-slate-50">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
              Vanlige spørsmål
            </h2>
            <p className="text-slate-500">Alt du lurer på, samlet på ett sted.</p>
          </div>
          <FaqSection />
        </div>
      </section>

      {/* Footer CTA */}
      <section className="py-24 px-6 bg-blue-600 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-1/4 w-96 h-96 rounded-full bg-white blur-3xl" />
          <div className="absolute bottom-0 right-1/4 w-64 h-64 rounded-full bg-white blur-3xl" />
        </div>
        <div className="max-w-2xl mx-auto text-center relative">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Klar til å aldri gå glipp av et oppdrag?
          </h2>
          <p className="text-blue-100 mb-8 text-lg">
            Kom i gang på 5 minutter. Ingen kredittkort påkrevd i prøveperioden.
          </p>
          <Link
            href="/pricing"
            className="inline-block bg-white text-blue-600 hover:bg-blue-50 font-bold px-10 py-4 rounded-xl text-lg transition-all hover:scale-105 shadow-lg"
          >
            Start gratis prøveperiode →
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-slate-100 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="grid sm:grid-cols-3 gap-8 mb-10">
            <div>
              <span className="text-blue-600 font-bold text-lg">SvarDirekte</span>
              <p className="text-slate-400 text-sm mt-2 max-w-xs">
                Automatisk SMS-håndtering for norske håndverkere.
              </p>
            </div>
            <div>
              <p className="font-semibold text-slate-700 text-sm mb-3">Produkt</p>
              <ul className="space-y-2">
                <li><a href="#how-it-works" className="text-sm text-slate-500 hover:text-slate-700 transition-colors">Slik fungerer det</a></li>
                <li><Link href="/pricing" className="text-sm text-slate-500 hover:text-slate-700 transition-colors">Priser</Link></li>
                <li><a href="#faq" className="text-sm text-slate-500 hover:text-slate-700 transition-colors">FAQ</a></li>
              </ul>
            </div>
            <div>
              <p className="font-semibold text-slate-700 text-sm mb-3">Konto</p>
              <ul className="space-y-2">
                <li><Link href="/sign-in" className="text-sm text-slate-500 hover:text-slate-700 transition-colors">Logg inn</Link></li>
                <li><Link href="/pricing" className="text-sm text-slate-500 hover:text-slate-700 transition-colors">Start gratis</Link></li>
                <li><Link href="/dashboard" className="text-sm text-slate-500 hover:text-slate-700 transition-colors">Dashboard</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-100 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-slate-400 text-sm">
              © {new Date().getFullYear()} SvarDirekte. Alle rettigheter forbeholdt.
            </p>
            <p className="text-slate-400 text-sm">
              post@svardirekte.no
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
