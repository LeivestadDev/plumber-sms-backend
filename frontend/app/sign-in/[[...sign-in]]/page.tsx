import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <a href="/" className="text-2xl font-bold text-blue-600">
            SvarDirekte
          </a>
          <p className="text-slate-500 mt-2 text-sm">Logg inn på dashboardet</p>
        </div>
        <SignIn fallbackRedirectUrl="/dashboard" />
      </div>
    </div>
  );
}
