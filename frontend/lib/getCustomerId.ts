import { currentUser } from "@clerk/nextjs/server";

/**
 * Resolves the FastAPI customer_id for the logged-in Clerk user.
 *
 * Priority:
 *  1. user.publicMetadata.customerId  (set by admin after creating the customer)
 *  2. CUSTOMER_ID env variable         (handy for local dev / single-tenant)
 */
export async function getCustomerId(): Promise<number | null> {
  const user = await currentUser();
  const meta = user?.publicMetadata?.customerId;
  if (meta !== undefined && meta !== null) {
    const n = Number(meta);
    if (!isNaN(n)) return n;
  }
  const env = process.env.CUSTOMER_ID;
  if (env) return parseInt(env, 10);
  return null;
}
