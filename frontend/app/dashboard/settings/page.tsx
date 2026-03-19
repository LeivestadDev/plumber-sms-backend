import { getCustomerId } from "@/lib/getCustomerId";
import { fetchCustomer, updateCustomer } from "@/lib/api/server";
import { NoCustomerId } from "@/components/NoCustomerId";
import { SettingsForm } from "./SettingsForm";
import { revalidatePath } from "next/cache";

export default async function SettingsPage() {
  const customerId = await getCustomerId();
  if (!customerId) return <NoCustomerId />;

  const customer = await fetchCustomer(customerId);

  async function saveSettings(
    formData: FormData
  ): Promise<{ ok: boolean; error?: string }> {
    "use server";
    try {
      await updateCustomer(customerId!, {
        company_name: formData.get("company_name") as string,
        greeting_message:
          (formData.get("greeting_message") as string) || null,
        calendly_url: formData.get("calendly_url") as string,
        plumber_phone: formData.get("plumber_phone") as string,
      });
      revalidatePath("/dashboard");
      revalidatePath("/dashboard/settings");
      return { ok: true };
    } catch (err) {
      return {
        ok: false,
        error: err instanceof Error ? err.message : "Ukjent feil",
      };
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Innstillinger</h1>
        <p className="text-slate-500 text-sm mt-0.5">
          Tilpass hvordan SvarDirekte oppfører seg for dine kunder
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <SettingsForm customer={customer} onSave={saveSettings} />
      </div>
    </div>
  );
}
