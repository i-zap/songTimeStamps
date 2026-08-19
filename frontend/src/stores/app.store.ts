import { create } from "zustand";

type AppView = "workspace" | "settings";

interface AppState {
  activeView: AppView;
  setActiveView: (view: AppView) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeView: "workspace",

  setActiveView: (view) => {
    set({ activeView: view });
  },
}));