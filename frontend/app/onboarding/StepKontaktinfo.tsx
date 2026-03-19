"use client";

import { useState } from "react";
import type { OnboardingData } from "./OnboardingWizard";
import { Field, inputClass } from "./shared";

function validatePhone(value: string): string {
  const stripped = value.replace(/\s+/g, "");
  if (!stripped) return "Mobilnummer er påkrevd";
  // Accept +47XXXXXXXX (8 digits after +47) or 8 bare digits
  if (/^\+47\d{8}$/.test(stripped) || /^\d{8}$/.test(stripped)) return "";
  return "Ugyldig nummer. Bruk +47XXXXXXXX eller 8 siffer";
}

function normalise(value: string): string {
  const stripped = value.replace(/\s+/g, "");
  if (/^\d{8}$/.test(stripped)) return `+47${stripped}`;
  return stripped;
}

export default function StepKontaktinfo({
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

  const error = touched ? validatePhone(value) : "";

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setTouched(true);
    if (validatePhone(value)) return;
    onNext({ plumber_phone: normalise(value) });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900 mb-1">Kontaktinfo</h2>
        <p className="text-sm text-slate-500">
          Nummeret som mottar akutt-varsler når en kunde trenger hjelp umiddelbart.
        </p>
      </div>

      <Field label="Mobilnummer for akutvarsler" required error={error}
        hint="Norsk mobilnummer — +47XXXXXXXX eller 8 siffer"
      >
        <input
          autoFocus
          type="tel"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onBlur={() => setTouched(true)}
          placeholder="+4798765432"
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
