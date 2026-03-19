"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useClerk } from "@clerk/nextjs";

export default function LandingNav() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const { user } = useClerk();

  useEffect(() => {
    function onScroll() {
      setScrolled(window.scrollY > 12);
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <nav
      className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        scrolled
          ? "bg-white/80 backdrop-blur-md border-b border-slate-100 shadow-sm"
          : "bg-white/0"
      }`}
    >
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold text-blue-600 shrink-0">
          SvarDirekte
        </Link>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-8">
          <a href="#how-it-works" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">
            Slik fungerer det
          </a>
          <a href="#pricing" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">
            Priser
          </a>
          <a href="#faq" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">
            FAQ
          </a>
        </div>

        <div className="hidden md:flex items-center gap-3">
          {user ? (
            <Link
              href="/dashboard"
              className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-all duration-150 hover:scale-105"
            >
              Dashboard
            </Link>
          ) : (
            <>
              <Link href="/sign-in" className="text-sm text-slate-600 hover:text-slate-900 font-medium transition-colors">
                Logg inn
              </Link>
              <Link
                href="/pricing"
                className="bg-orange-500 hover:bg-orange-600 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-all duration-150 hover:scale-105 shadow-sm shadow-orange-200"
              >
                Start gratis
              </Link>
            </>
          )}
        </div>

        {/* Mobile hamburger */}
        <button
          onClick={() => setOpen((v) => !v)}
          className="md:hidden p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          aria-label="Meny"
        >
          {open ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          )}
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden bg-white border-b border-slate-100 px-6 py-4 flex flex-col gap-4 shadow-lg">
          <a href="#how-it-works" onClick={() => setOpen(false)} className="text-sm text-slate-700 font-medium">
            Slik fungerer det
          </a>
          <a href="#pricing" onClick={() => setOpen(false)} className="text-sm text-slate-700 font-medium">
            Priser
          </a>
          <a href="#faq" onClick={() => setOpen(false)} className="text-sm text-slate-700 font-medium">
            FAQ
          </a>
          <div className="flex gap-3 pt-2 border-t border-slate-100">
            <Link href="/sign-in" className="text-sm text-slate-600 font-medium py-2">
              Logg inn
            </Link>
            <Link
              href="/pricing"
              className="bg-orange-500 text-white text-sm font-semibold px-4 py-2 rounded-lg"
            >
              Start gratis
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
