"use client";

export default function WelcomeModal({
  twilioNumber,
  onClose,
}: {
  twilioNumber: string;
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 text-center animate-fade-up">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </div>

        <h2 className="text-2xl font-bold text-slate-900 mb-2">Velkommen til SvarDirekte!</h2>
        <p className="text-slate-500 text-sm mb-6">
          Kontoen din er satt opp og klar til bruk.
        </p>

        {twilioNumber && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl px-6 py-4 mb-6">
            <p className="text-xs font-medium text-blue-600 uppercase tracking-wide mb-1">
              Ditt SMS-nummer
            </p>
            <p className="text-2xl font-bold text-blue-900 tracking-wide">
              {twilioNumber}
            </p>
            <p className="text-xs text-blue-600 mt-1">
              Del dette nummeret med kundene dine
            </p>
          </div>
        )}

        <p className="text-sm text-slate-500 mb-6">
          Kunder som sender SMS til dette nummeret vil automatisk bli fulgt opp og booket inn i kalenderen din.
        </p>

        <button
          onClick={onClose}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg text-sm transition-colors"
        >
          Gå til dashboardet →
        </button>
      </div>
    </div>
  );
}
