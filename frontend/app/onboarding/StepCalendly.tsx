"use client";

import { useState } from "react";
import type { OnboardingData } from "./OnboardingWizard";
import { Field, inputClass } from "./shared";

function validateCalendly(value: string): string {
  if (!value.trim()) return "Calendly-lenke er påkrevd";
  try {
    const url = new URL(value.trim());
    if (!url.hostname.endsWith("calendly.com")) {
      return "Lenken må være fra calendly.com";
    }
  } catch {
    return "Ugyldig URL — eksempel: https://calendly.com/ditt-navn/konsultasjon";
  }
  return "";
}

export default function StepCalendly({
  defaultValue,
  onNext,
  onBack,
}: {
  defaultValue: string;
  onNext: (data: Partial<OnboardingData>) => void;
  onBack: () => void;
}) {
  const [value, setValue] = useState(defaultValue);
  const [touched, setTouched] = useState(false);

  const error = touched ? validateCalendly(value) : "";

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setTouched(true);
    if (validateCalendly(value)) return;
    onNext({ calendly_url: value.trim() });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900 mb-1">Calendly-lenke</h2>
        <p className="text-sm text-slate-500">
          Kunder som tar kontakt vil få denne lenken for å booke tid.
        </p>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3 text-sm text-blue-800">
        Finn lenken i Calendly under <strong>Event Types → Copy link</strong>
      </div>

      <Field label="Calendly-URL" required error={error}>
        <input
          autoFocus
          type="url"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onBlur={() => setTouched(true)}
          placeholder="https://calendly.com/ditt-navn/konsultasjon"
          className={`${inputClass} ${error ? "border-red-400 focus:ring-red-400" : ""}`}
        />
      </Field>

      <div className="flex gap-3">
        <button
          type="button"
          onClick={onBack}
          className="flex-1 border border-slate-300 hover:border-slate-400 text-slate-700 font-semibold py-2.5 rounded-lg text-sm transition-colors"
        >
          ← Tilbake
        </button>
        <button
          type="submit"
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors"
        >
          Neste →
        </button>
      </div>
    </form>
  );
}
