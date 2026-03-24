import { redirect } from "next/navigation";
import { getCustomerId } from "@/lib/getCustomerId";
import { fetchCustomer } from "@/lib/api/server";
import OnboardingWizard from "./OnboardingWizard";

export default async function OnboardingPage() {
  const customerId = await getCustomerId();

  if (customerId !== null) {
    // Verify the customer actually exists in the backend (database may have been reset)
    try {
      await fetchCustomer(customerId);
      redirect("/dashboard"); // Customer exists, go to dashboard
    } catch {
      // Customer not found in backend (stale ID) — fall through to show onboarding
    }
  }

  return <OnboardingWizard />;
}
