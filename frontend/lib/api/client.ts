import axios from "axios";

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": process.env.ADMIN_API_KEY ?? "",
  },
});

export default apiClient;
