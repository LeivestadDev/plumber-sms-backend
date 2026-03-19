import apiClient from "./client";
import type { Customer, CustomerPatch, CustomerWithStats } from "./types";

export async function listCustomers(active?: boolean): Promise<Customer[]> {
  const params = active !== undefined ? { active } : {};
  const { data } = await apiClient.get<Customer[]>("/api/customers", { params });
  return data;
}

export async function getCustomer(id: number): Promise<CustomerWithStats> {
  const { data } = await apiClient.get<CustomerWithStats>(`/api/customers/${id}`);
  return data;
}

export async function patchCustomer(
  id: number,
  body: CustomerPatch
): Promise<Customer> {
  const { data } = await apiClient.patch<Customer>(`/api/customers/${id}`, body);
  return data;
}
