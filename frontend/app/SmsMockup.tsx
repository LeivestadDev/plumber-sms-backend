"use client";

import { useEffect, useState } from "react";

const MESSAGES = [
  { id: 1, from: "customer", text: "Hei! Jeg har vannlekkasje under kjøkkenvasken 🚨" },
  { id: 2, from: "bot", text: "Hei! Vi er opptatt på jobb nå, men skal hjelpe deg. Kan du si litt mer om problemet?" },
  { id: 3, from: "customer", text: "Det renner jevnt, trenger hjelp i dag" },
  { id: 4, from: "bot", text: "Forstått! Her er ledige tider for i dag 👇\n\ncal.example.no/booking\n\nBook direkte — vi bekrefter med én gang!" },
];

const DELAYS = [400, 1800, 3400, 5000];

export default function SmsMockup() {
  const [visible, setVisible] = useState(0);

  useEffect(() => {
    const timers = DELAYS.map((delay, i) =>
      setTimeout(() => setVisible(i + 1), delay)
    );
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div className="relative mx-auto w-72 sm:w-80">
      {/* Phone frame */}
      <div className="relative bg-slate-900 rounded-[2.5rem] p-3 shadow-2xl shadow-slate-900/40 ring-1 ring-white/10">
        {/* Screen */}
        <div className="bg-slate-100 rounded-[2rem] overflow-hidden">
          {/* Status bar */}
          <div className="bg-slate-800 px-5 py-2 flex items-center justify-between">
            <span className="text-white text-xs font-semibold">9:41</span>
            <div className="flex items-center gap-1">
              <div className="w-4 h-2 border border-white/60 rounded-sm">
                <div className="w-3/4 h-full bg-white/80 rounded-sm" />
              </div>
            </div>
          </div>

          {/* Header */}
          <div className="bg-white border-b border-slate-200 px-4 py-3 flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
              <span className="text-white text-xs font-bold">SD</span>
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-900">SvarDirekte</p>
              <p className="text-[10px] text-green-500 font-medium">● Aktiv</p>
            </div>
          </div>

          {/* Messages */}
          <div className="bg-slate-100 px-3 py-4 min-h-[280px] space-y-2">
            {MESSAGES.slice(0, visible).map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.from === "customer" ? "justify-end" : "justify-start"} animate-fade-up`}
                style={{ animationDelay: "0ms", animationFillMode: "both" }}
              >
                <div
                  className={`max-w-[80%] px-3 py-2 rounded-2xl text-xs leading-relaxed whitespace-pre-line ${
                    msg.from === "customer"
                      ? "bg-blue-600 text-white rounded-br-sm"
                      : "bg-white text-slate-800 shadow-sm rounded-bl-sm"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {visible > 0 && visible < MESSAGES.length && (
              <div className="flex justify-start">
                <div className="bg-white rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm flex items-center gap-1">
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-typing"
                      style={{ animationDelay: `${i * 0.2}s` }}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Input bar */}
          <div className="bg-white border-t border-slate-200 px-3 py-2 flex items-center gap-2">
            <div className="flex-1 bg-slate-100 rounded-full px-3 py-1.5">
              <p className="text-[11px] text-slate-400">Skriv en melding…</p>
            </div>
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center">
              <svg className="w-3.5 h-3.5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Glow effect */}
      <div className="absolute inset-0 -z-10 blur-3xl opacity-20 bg-blue-400 rounded-full scale-90 translate-y-4" />
    </div>
  );
}
