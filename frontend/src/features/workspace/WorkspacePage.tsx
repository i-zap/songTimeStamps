import Button from "../../components/ui/Button";

function WorkspacePage() {
  return (
    <section className="mx-auto max-w-6xl px-6 py-16">
      <div>
        <p className="text-sm font-medium text-zinc-400">
          Song workspace
        </p>

        <h2 className="mt-2 text-4xl font-bold tracking-tight">
          Create synchronized lyrics.
        </h2>

        <p className="mt-4 max-w-2xl text-zinc-400">
          Add your audio and lyric layers to create a synchronized LRC file.
        </p>
      </div>

      <div className="mt-10 rounded-2xl border border-dashed border-zinc-700 p-12 text-center">
        <h3 className="text-lg font-semibold">
          Drop your audio file here
        </h3>
        <p className="mt-2 text-sm text-zinc-500">
          FLAC, MP3, WAV, M4A and more
        </p>
        <Button className="mt-6">
          Choose Audio
        </Button>
      </div>
    </section>
  );
}

export default WorkspacePage;