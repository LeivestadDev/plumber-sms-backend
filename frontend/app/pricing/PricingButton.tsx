"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

interface Props {
  plan: "pilot" | "standard";
  label: string;
  primary?: boolean;
}

export default function PricingButton({ plan, label, primary }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function handleClick() {
    setLoading(true);
    setError(null);
    console.log("[PricingButton] klikk — plan:", plan);

    try {
      const res = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan }),
      });

      console.log("[PricingButton] svar status:", res.status);

      if (res.status === 401) {
        router.push("/sign-in");
        return;
      }

      const data = await res.json();
      console.log("[PricingButton] svar body:", data);

      if (!res.ok || data.error) {
        setError(data.error ?? "Noe gikk galt. Prøv igjen.");
        return;
      }

      if (data.url) {
        window.location.href = data.url;
      }
    } catch (err) {
      console.error("[PricingButton] feil:", err);
      setError("Kunne ikke koble til betalingstjenesten. Prøv igjen.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-2">
      <button
        onClick={handleClick}
        disabled={loading}
        className={`w-full font-semibold py-3 rounded-xl transition-colors disabled:opacity-60 ${
          primary
            ? "bg-blue-600 hover:bg-blue-700 text-white"
            : "border border-slate-300 hover:border-slate-400 text-slate-700"
        }`}
      >
        {loading ? "Laster..." : label}
      </button>
      {error && (
        <p className="text-sm text-red-600 text-center">{error}</p>
      )}
    </div>
  );
}
