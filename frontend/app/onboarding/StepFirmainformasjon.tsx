"use client";

import { useState } from "react";
import type { OnboardingData } from "./OnboardingWizard";
import { Field, inputClass } from "./shared";

export default function StepFirmainformasjon({
  defaultValue,
  onNext,
}: {
  defaultValue: string;
  onNext: (data: Partial<OnboardingData>) => void;
}) {
  const [value, setValue] = useState(defaultValue);
  const [touched, setTouched] = useState(false);

  const error = touched && !value.trim() ? "Firmanavn er påkrevd" : "";

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setTouched(true);
    if (!value.trim()) return;
    onNext({ company_name: value.trim() });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900 mb-1">Firmainformasjon</h2>
        <p className="text-sm text-slate-500">Hva heter bedriften din?</p>
      </div>

      <Field label="Firmanavn" required error={error}>
        <input
          autoFocus
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onBlur={() => setTouched(true)}
          placeholder="Olsen Rørlegger AS"
          className={`${inputClass} ${error ? "border-red-400 focus:ring-red-400" : ""}`}
        />
      </Field>

      <button
        type="submit"
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors"
      >
        Neste →
      </button>
    </form>
  );
}
