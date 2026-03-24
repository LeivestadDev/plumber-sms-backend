import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <a href="/" className="text-2xl font-bold text-blue-600">
            SvarDirekte
          </a>
          <p className="text-slate-500 mt-2 text-sm">
            Opprett konto og start gratis prøveperiode
          </p>
        </div>
        <SignUp fallbackRedirectUrl="/onboarding" />
      </div>
    </div>
  );
}
