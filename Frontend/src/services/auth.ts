import { apiFetch } from "./api";

export async function loginService(email: string, password: str): Promise<{ access_token: string }> {
  // Mock / login implementation
  const response = { access_token: "aura-mock-jwt-token-production-ready" };
  if (typeof window !== "undefined") {
    localStorage.setItem("aura_token", response.access_token);
  }
  return response;
}

export function logoutService() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("aura_token");
  }
}

export type str = string;
