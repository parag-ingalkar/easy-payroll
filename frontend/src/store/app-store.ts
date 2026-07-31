"use client";

import { create } from "zustand";

export type ViewName =
  | "login"
  | "register"
  | "onboarding"
  | "dashboard"
  | "attendance"
  | "employees"
  | "employee-detail"
  | "payroll"
  | "payroll-run"
  | "settings"
  | "profile";

type AppState = {
  view: ViewName;
  params: Record<string, string>;
  setView: (view: ViewName, params?: Record<string, string>) => void;
  navigate: (view: ViewName, params?: Record<string, string>) => void;
  goBack: () => void;
};

export const useAppStore = create<AppState>((set, get) => ({
  view: "dashboard",
  params: {},
  setView: (view, params = {}) => set({ view, params }),
  navigate: (view, params = {}) => {
    set({ view, params });
    if (typeof window !== "undefined") {
      const hash = `#/${view}${Object.keys(params).length ? "?" + new URLSearchParams(params).toString() : ""}`;
      window.history.pushState({ view, params }, "", hash);
    }
  },
  goBack: () => {
    if (typeof window !== "undefined" && window.history.length > 1) {
      window.history.back();
    } else {
      set({ view: "dashboard", params: {} });
    }
  },
}));
