import { BASE_URL } from "./url";

export const getCurrentUser = async () => {
  const res = await fetch(`${BASE_URL}/users/me`, {
    method: "GET",
    credentials: "include",
  });

  if (!res.ok) return null;
  return await res.json(); // { id, username, email }
};

export const login = async (username: string, password: string) => {
  const res = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json", // ✅ Important for Flask to parse JSON
    },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.msg || "Login failed");
  }

  const data = await res.json();
  return data;
};

export const signup = async (
  username: string,
  email: string,
  password: string
) => {
  const res = await fetch(`${BASE_URL}/signup`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json", // ✅ Important for Flask to parse JSON
    },
    body: JSON.stringify({ username, email, password }),
  });
  if (!res.ok) {
    return new Error("Error");
  }
  const data = await res.json();
  return data;
};

export const logout = async () => {
  const res = await fetch(`${BASE_URL}/logout`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) {
    return new Error("Error");
  }
  const data = await res.json();
  return data;
};
