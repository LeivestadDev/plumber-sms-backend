"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import StepFirmainformasjon from "./StepFirmainformasjon";
import StepKontaktinfo from "./StepKontaktinfo";
import StepCalendly from "./StepCalendly";
import StepVelkomstmelding from "./StepVelkomstmelding";
import WelcomeModal from "./WelcomeModal";

export interface OnboardingData {
  company_name: string;
  plumber_phone: string;
  calendly_url: string;
  greeting_message: string;
}

const STEPS = [
  "Firmainformasjon",
  "Kontaktinfo",
  "Calendly-lenke",
  "Velkomstmelding",
];

export default function OnboardingWizard() {
  const router = useRouter();

  const [step, setStep] = useState(0);
  const [data, setData] = useState<OnboardingData>({
    company_name: "",
    plumber_phone: "",
    calendly_url: "",
    greeting_message: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [createdTwilioNumber, setCreatedTwilioNumber] = useState("");
  const [showModal, setShowModal] = useState(false);

  function next(update: Partial<OnboardingData>) {
    setData((prev) => ({ ...prev, ...update }));
    setStep((s) => s + 1);
  }

  async function finish(update: Partial<OnboardingData>) {
    const final = { ...data, ...update };
    setData(final);
    setSubmitting(true);
    setError("");

    try {
      const res = await fetch("/api/onboarding", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(final),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.error ?? `Feil ${res.status}`);
      }

      const created = await res.json();
      setCreatedTwilioNumber(created.twilio_number ?? "");
      setShowModal(true);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Noe gikk galt. Prøv igjen.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg">
        {/* Logo */}
        <div className="text-center mb-8">
          <span className="text-2xl font-bold text-slate-900">SvarDirekte</span>
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex justify-between text-xs text-slate-500 mb-2">
            <span>Steg {step + 1} av {STEPS.length}</span>
            <span>{STEPS[step]}</span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-1.5">
            <div
              className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${((step + 1) / STEPS.length) * 100}%` }}
            />
          </div>
          <div className="flex mt-3 gap-2">
            {STEPS.map((label, i) => (
              <div key={i} className="flex-1 text-center">
                <div
                  className={`mx-auto w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold mb-1 ${
                    i < step
                      ? "bg-blue-600 text-white"
                      : i === step
                      ? "bg-blue-600 text-white ring-4 ring-blue-100"
                      : "bg-slate-200 text-slate-400"
                  }`}
                >
                  {i < step ? "✓" : i + 1}
                </div>
                <p className={`text-[10px] hidden sm:block ${i === step ? "text-blue-600 font-medium" : "text-slate-400"}`}>
                  {label}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Step card */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
          {step === 0 && (
            <StepFirmainformasjon defaultValue={data.company_name} onNext={next} />
          )}
          {step === 1 && (
            <StepKontaktinfo defaultValue={data.plumber_phone} onNext={next} onBack={() => setStep(0)} />
          )}
          {step === 2 && (
            <StepCalendly defaultValue={data.calendly_url} onNext={next} onBack={() => setStep(1)} />
          )}
          {step === 3 && (
            <StepVelkomstmelding
              defaultValue={data.greeting_message}
              companyName={data.company_name}
              onFinish={finish}
              onBack={() => setStep(2)}
              submitting={submitting}
              error={error}
            />
          )}
        </div>
      </div>

      {showModal && (
        <WelcomeModal
          twilioNumber={createdTwilioNumber}
          onClose={() => router.push("/dashboard")}
        />
      )}
    </div>
  );
}
