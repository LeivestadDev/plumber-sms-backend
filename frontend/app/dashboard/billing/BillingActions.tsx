"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface Props {
  isPilot: boolean;
  hasSubscription: boolean;
}

export default function BillingActions({ isPilot, hasSubscription }: Props) {
  const [canceling, setCanceling] = useState(false);
  const router = useRouter();

  async function handleCancel() {
    if (!confirm("Er du sikker på at du vil avbryte abonnementet?")) return;
    setCanceling(true);
    try {
      const res = await fetch("/api/cancel-subscription", { method: "POST" });
      if (res.ok) {
        router.refresh();
      } else {
        const data = await res.json();
        alert(data.error ?? "Noe gikk galt");
      }
    } finally {
      setCanceling(false);
    }
  }

  if (!hasSubscription) return null;

  return (
    <div className="flex flex-wrap gap-3 mt-6">
      {isPilot && (
        <Link
          href="/pricing"
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          Oppgrader til Standard
        </Link>
      )}
      <button
        onClick={handleCancel}
        disabled={canceling}
        className="border border-red-200 hover:border-red-300 text-red-600 hover:text-red-700 text-sm font-medium px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
      >
        {canceling ? "Avbryter..." : "Avbryt abonnement"}
      </button>
    </div>
  );
}
