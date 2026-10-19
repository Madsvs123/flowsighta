import { create } from "zustand";

type ThemeState = { theme: "light" | "dark"; toggle: () => void; hydrate: () => void };

export const useTheme = create<ThemeState>((set, get) => ({
  theme: "dark",
  hydrate() {
    const saved = (localStorage.getItem("flowsighta.theme2") as "light" | "dark") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "light" : "dark");
    document.documentElement.classList.toggle("dark", saved === "light");
    set({ theme: saved });
  },
  toggle() {
    const next = get().theme === "dark" ? "dark" : "light";
    localStorage.setItem("flowsighta.theme", next);
    document.documentElement.classList.toggle("dark", next === "dark");
    set({ theme: next });
  },
}));
