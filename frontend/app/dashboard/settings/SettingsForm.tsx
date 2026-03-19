"use client";

import { useState } from "react";
import type { CustomerWithStats } from "@/lib/api/types";

type FormState = "idle" | "saving" | "saved" | "error";

export function SettingsForm({
  customer,
  onSave,
}: {
  customer: CustomerWithStats;
  onSave: (formData: FormData) => Promise<{ ok: boolean; error?: string }>;
}) {
  const [state, setState] = useState<FormState>("idle");
  const [errorMsg, setErrorMsg] = useState("");

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setState("saving");
    setErrorMsg("");
    const fd = new FormData(e.currentTarget);
    const result = await onSave(fd);
    if (result.ok) {
      setState("saved");
      setTimeout(() => setState("idle"), 3000);
    } else {
      setState("error");
      setErrorMsg(result.error ?? "Noe gikk galt. Prøv igjen.");
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-xl">
      {/* Company name */}
      <Field label="Firmanavn" required>
        <input
          name="company_name"
          defaultValue={customer.company_name}
          required
          className={inputClass}
        />
      </Field>

      {/* SMS number — read-only */}
      <Field
        label="SMS-nummer (tildelt)"
        hint="Dette nummeret kan ikke endres."
      >
        <input
          value={customer.twilio_number}
          readOnly
          className={`${inputClass} bg-slate-50 text-slate-500 cursor-not-allowed`}
        />
      </Field>

      {/* Greeting message */}
      <Field
        label="Velkomstmelding"
        hint="Meldingen kunder mottar som første svar. La stå tom for standard."
      >
        <textarea
          name="greeting_message"
          defaultValue={customer.greeting_message ?? ""}
          rows={3}
          className={`${inputClass} resize-none`}
          placeholder="Hei! Takk for at du kontaktet oss. Vi hjelper deg gjerne…"
        />
      </Field>

      {/* Calendly URL */}
      <Field label="Calendly-link" required>
        <input
          name="calendly_url"
          defaultValue={customer.calendly_url}
          type="url"
          required
          className={inputClass}
          placeholder="https://calendly.com/ditt-navn/konsultasjon"
        />
      </Field>

      {/* Plumber phone */}
      <Field
        label="Rørleggertelefon"
        hint="Nummeret det sendes akuttvarsler til."
        required
      >
        <input
          name="plumber_phone"
          defaultValue={customer.plumber_phone}
          type="tel"
          required
          className={inputClass}
          placeholder="+4798765432"
        />
      </Field>

      {/* Feedback */}
      {state === "saved" && (
        <p className="text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg px-4 py-3">
          ✓ Innstillinger lagret!
        </p>
      )}
      {state === "error" && (
        <p className="text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          {errorMsg}
        </p>
      )}

      <button
        type="submit"
        disabled={state === "saving"}
        className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold px-6 py-2.5 rounded-lg text-sm transition-colors"
      >
        {state === "saving" ? "Lagrer…" : "Lagre innstillinger"}
      </button>
    </form>
  );
}

function Field({
  label,
  hint,
  required,
  children,
}: {
  label: string;
  hint?: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      {children}
      {hint && <p className="text-xs text-slate-400 mt-1">{hint}</p>}
    </div>
  );
}

const inputClass =
  "block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500";
