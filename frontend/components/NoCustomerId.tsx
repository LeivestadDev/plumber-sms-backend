export function NoCustomerId() {
  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 p-6 max-w-lg">
      <h2 className="text-base font-semibold text-amber-900 mb-2">
        Konto ikke koblet til backend
      </h2>
      <p className="text-sm text-amber-700 mb-4">
        Brukerkontoen din er ikke koblet til en kunde-ID i systemet ennå. En
        administrator må sette <code className="font-mono">customerId</code> i
        Clerk-brukerens <em>publicMetadata</em>, eller du kan legge til{" "}
        <code className="font-mono">CUSTOMER_ID=&lt;id&gt;</code> i{" "}
        <code className="font-mono">.env.local</code> for lokal utvikling.
      </p>
      <pre className="bg-amber-100 text-amber-800 rounded-lg p-3 text-xs">
        {`// Clerk Dashboard → Users → velg bruker\n// publicMetadata:\n{ "customerId": 1 }`}
      </pre>
    </div>
  );
}
