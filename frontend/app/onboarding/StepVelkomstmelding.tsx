"use client";

import { useState } from "react";
import type { OnboardingData } from "./OnboardingWizard";
import { Field, inputClass } from "./shared";

function defaultGreeting(companyName: string) {
  return `Hei! Du har nådd ${companyName || "oss"}. Hva kan vi hjelpe deg med?`;
}

export default function StepVelkomstmelding({
  defaultValue,
  companyName,
  onFinish,
  onBack,
  submitting,
  error,
}: {
  defaultValue: string;
  companyName: string;
  onFinish: (data: Partial<OnboardingData>) => void;
  onBack: () => void;
  submitting: boolean;
  error: string;
}) {
  const [value, setValue] = useState(
    defaultValue || defaultGreeting(companyName)
  );

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onFinish({ greeting_message: value.trim() === defaultGreeting(companyName) ? "" : value.trim() });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900 mb-1">Velkomstmelding</h2>
        <p className="text-sm text-slate-500">
          Dette er den første SMS-en kunder mottar. Valgfritt — standardtekst brukes om du ikke endrer den.
        </p>
      </div>

      <Field
        label="Melding"
        hint="Maks 160 tegn anbefales for å unngå delt SMS"
      >
        <textarea
          autoFocus
          value={value}
          onChange={(e) => setValue(e.target.value)}
          rows={4}
          className={`${inputClass} resize-none`}
        />
      </Field>

      {/* Live preview */}
      <div>
        <p className="text-xs font-medium text-slate-500 mb-2">Forhåndsvisning</p>
        <div className="bg-slate-100 rounded-2xl p-4">
          <div className="flex justify-start">
            <div className="max-w-[85%] bg-white text-slate-800 rounded-2xl rounded-bl-sm px-3 py-2 text-sm shadow-sm">
              {value || defaultGreeting(companyName)}
            </div>
          </div>
        </div>
      </div>

      <button
        type="button"
        onClick={() => setValue(defaultGreeting(companyName))}
        className="text-xs text-blue-600 hover:text-blue-700 underline underline-offset-2"
      >
        Bruk standard
      </button>

      {error && (
        <p className="text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          {error}
        </p>
      )}

      <div className="flex gap-3">
        <button
          type="button"
          onClick={onBack}
          disabled={submitting}
          className="flex-1 border border-slate-300 hover:border-slate-400 disabled:opacity-50 text-slate-700 font-semibold py-2.5 rounded-lg text-sm transition-colors"
        >
          ← Tilbake
        </button>
        <button
          type="submit"
          disabled={submitting}
          className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors"
        >
          {submitting ? "Oppretter konto…" : "Fullfør oppsett ✓"}
        </button>
      </div>
    </form>
  );
}
