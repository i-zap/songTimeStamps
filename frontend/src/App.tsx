import { useAppStore } from "./stores/app.store";
import WorkspacePage from "./features/workspace/WorkspacePage";

function App() {
  const activeView = useAppStore((state) => state.activeView);
  const setActiveView = useAppStore((state) => state.setActiveView);

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100">
      <header className="border-b border-zinc-800">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <h1 className="text-lg font-semibold">songTimeStamps</h1>

          <nav className="flex gap-2">
            <button
              className="rounded-md px-3 py-2 text-sm hover:bg-zinc-800"
              onClick={() => setActiveView("workspace")}
            >
              Workspace
            </button>

            <button
              className="rounded-md px-3 py-2 text-sm hover:bg-zinc-800"
              onClick={() => setActiveView("settings")}
            >
              Settings
            </button>
          </nav>
        </div>
      </header>

      {activeView === "workspace" ? (
        <WorkspacePage />
      ) : (
        <section className="mx-auto max-w-6xl px-6 py-16">
          <h2 className="text-3xl font-bold">Settings</h2>
          <p className="mt-3 text-zinc-400">
            Provider and application settings will live here.
          </p>
        </section>
      )}
    </main>
  );
}

export default App;