import { TickerForm } from "@/components/ticker-form";

export default function HomePage() {
  return (
    <main className="mx-auto max-w-7xl px-5 pb-16 pt-8 sm:px-8">
      <div className="grid gap-8 lg:grid-cols-[1.25fr,0.75fr] lg:items-start">
        <TickerForm />
        <aside className="panel p-8">
          <p className="eyebrow">What you get</p>
          <div className="mt-5 space-y-5">
            {[
              "Latest 10-K resolution from the SEC with direct filing links.",
              "Normalized multi-year financial charts for the highest-signal metrics.",
              "A small scorecard and memo that cite exact filing snippets.",
              "An evidence drawer for reviewing the passage behind each claim.",
            ].map((item) => (
              <div key={item} className="rounded-[1.5rem] bg-sand/60 p-4">
                <p className="text-sm leading-7 text-ink/75">{item}</p>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </main>
  );
}

