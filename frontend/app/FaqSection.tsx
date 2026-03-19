"use client";

import { useState } from "react";

const FAQS = [
  {
    q: "Hva skjer etter at prøveperioden utløper?",
    a: "Etter 14 dager blir du automatisk belastet for Pilot-planen (299 kr/mnd). Du kan avbryte abonnementet når som helst i dashboard under «Fakturering» — ingen binding.",
  },
  {
    q: "Fungerer SvarDirekte med mitt eksisterende telefonnummer?",
    a: "SvarDirekte gir deg et dedikert SMS-nummer som kundene sender til. Du trenger ikke bytte mobilnummer — varslene fra kundene havner i dashboardet ditt.",
  },
  {
    q: "Hva om kunden sender noe systemet ikke forstår?",
    a: "Systemet er trent på vanlige henvendelser fra håndverkere. Dersom meldingen er uklar, sender SvarDirekte et vennlig oppfølgingsspørsmål. Du ser alle samtaler i dashboardet og kan følge opp manuelt om nødvendig.",
  },
  {
    q: "Kan jeg koble til mitt eget Calendly?",
    a: "Ja — du legger inn Calendly-lenken din under Innstillinger i dashboardet. SvarDirekte bruker den automatisk til å tilby tider til kundene dine.",
  },
  {
    q: "Er SvarDirekte GDPR-kompatibelt?",
    a: "Ja. Kundenes meldinger lagres på norske/europeiske servere, og du bestemmer selv hvor lenge historikken beholdes. Vi deler ingen data med tredjeparter uten ditt samtykke.",
  },
];

export default function FaqSection() {
  const [open, setOpen] = useState<number | null>(null);

  return (
    <div className="space-y-3">
      {FAQS.map((faq, i) => (
        <div
          key={i}
          className="border border-slate-200 rounded-xl overflow-hidden transition-shadow hover:shadow-sm"
        >
          <button
            onClick={() => setOpen(open === i ? null : i)}
            className="w-full flex items-center justify-between px-6 py-4 text-left"
          >
            <span className="font-medium text-slate-900 text-sm sm:text-base">
              {faq.q}
            </span>
            <span
              className={`ml-4 shrink-0 w-6 h-6 rounded-full flex items-center justify-center border border-slate-200 text-slate-500 transition-transform duration-200 ${
                open === i ? "rotate-45 bg-blue-50 border-blue-200 text-blue-600" : ""
              }`}
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
              </svg>
            </span>
          </button>
          {open === i && (
            <div className="px-6 pb-5 text-slate-600 text-sm leading-relaxed border-t border-slate-100 pt-4">
              {faq.a}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
