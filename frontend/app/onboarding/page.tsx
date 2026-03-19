import { redirect } from "next/navigation";
import { getCustomerId } from "@/lib/getCustomerId";
import OnboardingWizard from "./OnboardingWizard";

export default async function OnboardingPage() {
  // Guard: already onboarded → go to dashboard
  const customerId = await getCustomerId();
  if (customerId !== null) {
    redirect("/dashboard");
  }

  return <OnboardingWizard />;
}
