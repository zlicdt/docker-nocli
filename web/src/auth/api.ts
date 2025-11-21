const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8193";

export type AuthStatusResponse = {
  setup_required: boolean;
};

export type LoginResponse = {
  token: string;
};

export async function fetchAuthStatus(): Promise<AuthStatusResponse> {
  const res = await fetch(`${API_BASE}/status`);
  if (!res.ok) {
    throw new Error("Failed to fetch auth status");
  }
  const data = (await res.json()) as Partial<{ status: string; user_exist: boolean }>;
  return { setup_required: !data.user_exist };
}

export async function setupAdmin(username: string, password: string): Promise<void> {
  const res = await fetch(`${API_BASE}/auth/setup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    throw new Error("Failed to setup admin");
  }
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const res = await fetch(`${API_BASE}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    throw new Error("Login failed");
  }

  return res.json();
}
