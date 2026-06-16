"use client";

import { useState } from "react";
import {
  Sparkles,
  ArrowRight,
  Eye,
  HelpCircle,
  Volume2,
  Code2,
  ShieldCheck,
  Zap,
  Copy,
  Check,
  Network,
  LineChart,
} from "lucide-react";

import { AnimatedGradientText } from "@/components/ui/animated-gradient-text";
import { ShimmerButton } from "@/components/ui/shimmer-button";
import { BentoGrid, BentoCard } from "@/components/ui/bento-grid";
import { Marquee } from "@/components/ui/marquee";
import { BorderBeam } from "@/components/ui/border-beam";
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ArchitectureBeam } from "@/components/architecture-beam";

const SNIPPET = `<script
  src="https://your-ava-host/widget.js"
  data-tenant="lyvica"
  data-endpoint="https://your-ava-host">
</script>`;

const MARQUEE: { name: string; src?: string }[] = [
  { name: "CrewAI", src: "/logos/crewai.png" },
  { name: "TrueFoundry", src: "/logos/truefoundry.png" },
  { name: "Capgemini", src: "/logos/capgemini.png" },
];

const FEATURES = [
  {
    Icon: Eye,
    name: "Reads your app’s state",
    description:
      "Ava captures the live DOM — disabled buttons, validation errors, ARIA — not screenshots.",
  },
  {
    Icon: HelpCircle,
    name: "Knows why it’s blocked",
    description:
      "RAG over your product docs explains the business logic behind every blocked action.",
  },
  {
    Icon: Volume2,
    name: "Voice avatar",
    description:
      "Ava speaks the answer and highlights the exact element the user needs to fix.",
  },
  {
    Icon: Code2,
    name: "Drop-in & multi-tenant",
    description:
      "One script tag. Ava is a platform — onboard any SaaS as a tenant in minutes.",
  },
  {
    Icon: ShieldCheck,
    name: "Production-grade",
    description:
      "Every model call runs through the TrueFoundry gateway: fallbacks, guardrails, observability.",
  },
  {
    Icon: Zap,
    name: "Fast & reliable",
    description:
      "A lean CrewAI crew returns a structured answer in seconds, with a safe deterministic fallback.",
  },
];

const PRODUCTION = [
  {
    Icon: Network,
    title: "Multi-agent orchestration",
    body: "CrewAI runs Perception and Knowledge in parallel, then a Guide. Specialized agents, one reliable answer.",
    beam: true,
  },
  {
    Icon: ShieldCheck,
    title: "Gateway & guardrails",
    body: "Every LLM call flows through TrueFoundry — model fallbacks, rate limits and safety — deployed and observable.",
    beam: false,
  },
  {
    Icon: LineChart,
    title: "Evaluated & iterated",
    body: "An offline eval crew scores answers on every change, so reliability is measured, not hoped for.",
    beam: false,
  },
];

function Section({
  id,
  className,
  children,
}: {
  id?: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className={`w-full py-20 sm:py-28 ${className ?? ""}`}>
      <div className="mx-auto w-full max-w-6xl px-6">{children}</div>
    </section>
  );
}

export default function Home() {
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard?.writeText(SNIPPET);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <main className="relative flex flex-col overflow-x-hidden">
      {/* ambient glow */}
      <div className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-[600px] bg-[radial-gradient(60%_60%_at_50%_0%,rgba(124,92,255,0.18),transparent)]" />

      {/* nav */}
      <header className="sticky top-0 z-50 w-full border-b border-border/60 bg-background/70 backdrop-blur-md">
        <div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-6">
          <a href="#" className="flex items-center gap-2 font-semibold">
            <span className="grid h-7 w-7 place-items-center rounded-lg bg-primary text-primary-foreground">
              A
            </span>
            Ava
          </a>
          <nav className="hidden items-center gap-8 text-sm text-muted-foreground sm:flex">
            <a href="#how" className="transition-colors hover:text-foreground">
              How it works
            </a>
            <a href="#features" className="transition-colors hover:text-foreground">
              Features
            </a>
            <a href="#embed" className="transition-colors hover:text-foreground">
              Embed
            </a>
          </nav>
          <a
            href="#embed"
            className="inline-flex h-9 items-center rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
          >
            Get started
          </a>
        </div>
      </header>

      {/* hero */}
      <Section className="pt-24 sm:pt-32">
        <div className="flex flex-col items-center text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-card/50 px-4 py-1.5 text-sm">
            <Sparkles className="h-4 w-4 text-primary" />
            <AnimatedGradientText colorFrom="#a78bfa" colorTo="#7c5cff">
              Powered by CrewAI × TrueFoundry
            </AnimatedGradientText>
          </div>

          <h1 className="max-w-4xl text-4xl font-semibold tracking-tight text-balance sm:text-6xl">
            Support that understands your app’s state —{" "}
            <span className="text-primary">not just its pixels.</span>
          </h1>

          <p className="mt-6 max-w-2xl text-lg text-muted-foreground text-pretty">
            Ava is an embedded AI agent that reads your interface, knows{" "}
            <em className="text-foreground not-italic">why</em> a button is
            disabled, and guides your users by voice — step by step.
          </p>

          <div className="mt-9 flex flex-col items-center gap-3 sm:flex-row">
            <a href="#embed">
              <ShimmerButton
                background="rgba(124,92,255,1)"
                className="h-12 px-7 text-base font-medium"
              >
                Add Ava to your app
              </ShimmerButton>
            </a>
            <a
              href="#how"
              className="inline-flex h-12 items-center gap-2 rounded-full border border-border px-6 text-base font-medium transition-colors hover:bg-muted"
            >
              See how it works
              <ArrowRight className="h-4 w-4" />
            </a>
          </div>
        </div>
      </Section>

      {/* trust marquee */}
      <div className="w-full border-y border-border/60 py-6">
        <p className="mb-4 text-center text-xs uppercase tracking-widest text-muted-foreground">
          The production agent stack
        </p>
        <Marquee pauseOnHover className="[--duration:30s]">
          {MARQUEE.map((m) =>
            m.src ? (
              <div
                key={m.name}
                className="mx-5 flex h-14 items-center rounded-xl bg-white px-6 shadow-sm ring-1 ring-black/5"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={m.src}
                  alt={m.name}
                  className="h-7 w-auto object-contain"
                />
              </div>
            ) : (
              <span
                key={m.name}
                className="mx-8 flex h-14 items-center text-lg font-medium text-muted-foreground/70"
              >
                {m.name}
              </span>
            )
          )}
        </Marquee>
      </div>

      {/* problem */}
      <Section>
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            Generic chatbots don’t know your app.
          </h2>
          <p className="mt-5 text-lg text-muted-foreground text-pretty">
            They see text, not state. They can’t tell a user that{" "}
            <span className="text-foreground">Publish</span> is greyed out
            because no domain is connected. Ava reads the DOM, maps it to your
            product docs, and answers the real question:{" "}
            <span className="text-foreground">why is this blocked?</span>
          </p>
        </div>
      </Section>

      {/* how it works */}
      <Section id="how" className="pt-0">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            How Ava works
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground text-pretty">
            Ava captures the live UI state and runs a CrewAI crew — Perception
            and Knowledge in parallel, then a Guide — returning what to say,
            which element to highlight, and the next step.
          </p>
        </div>

        <Card className="relative overflow-hidden p-4 sm:p-8">
          <ArchitectureBeam />
          <div className="mt-6 grid grid-cols-2 gap-4 text-sm text-muted-foreground sm:grid-cols-4">
            <div>
              <span className="font-medium text-foreground">Perception</span> —
              reads the DOM, finds the blocked element and why.
            </div>
            <div>
              <span className="font-medium text-foreground">Knowledge</span> —
              RAG over your product docs.
            </div>
            <div>
              <span className="font-medium text-foreground">Guide</span> —
              reconciles both into one clear answer.
            </div>
            <div>
              <span className="font-medium text-foreground">Output</span> —
              speech, highlight selector, next step.
            </div>
          </div>
          <BorderBeam size={120} duration={10} colorFrom="#7c5cff" colorTo="#c4b5fd" />
        </Card>
      </Section>

      {/* features */}
      <Section id="features" className="pt-0">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            Built to actually help
          </h2>
        </div>
        <BentoGrid className="auto-rows-[15rem] grid-cols-1 lg:grid-cols-3">
          {FEATURES.map((f) => (
            <BentoCard
              key={f.name}
              name={f.name}
              className="col-span-1"
              Icon={f.Icon}
              description={f.description}
              href="#embed"
              cta="Learn more"
              background={
                <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-primary/15 blur-3xl" />
              }
            />
          ))}
        </BentoGrid>
      </Section>

      {/* embed */}
      <Section id="embed">
        <div className="grid items-center gap-10 lg:grid-cols-2">
          <div>
            <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
              Add Ava in one line
            </h2>
            <p className="mt-5 text-lg text-muted-foreground text-pretty">
              Drop the script into your app, tag a few elements with{" "}
              <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-sm text-foreground">
                data-ava
              </code>
              , and Ava is live for your users. It is a multi-tenant platform —
              your product is just a tenant.
            </p>
            <ul className="mt-6 space-y-3 text-sm text-muted-foreground">
              {[
                "No SDK, no rebuild — a single script tag.",
                "Per-tenant docs, selectors and language.",
                "Hosted on TrueFoundry, served through the AI gateway.",
              ].map((t) => (
                <li key={t} className="flex items-start gap-2">
                  <Check className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                  {t}
                </li>
              ))}
            </ul>
          </div>

          <div className="relative rounded-2xl border border-border bg-card">
            <div className="flex items-center justify-between border-b border-border px-4 py-2.5">
              <div className="flex items-center gap-1.5">
                <span className="h-3 w-3 rounded-full bg-destructive/70" />
                <span className="h-3 w-3 rounded-full bg-yellow-500/70" />
                <span className="h-3 w-3 rounded-full bg-green-500/70" />
              </div>
              <button
                onClick={copy}
                className="inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              >
                {copied ? (
                  <>
                    <Check className="h-3.5 w-3.5 text-primary" /> Copied
                  </>
                ) : (
                  <>
                    <Copy className="h-3.5 w-3.5" /> Copy
                  </>
                )}
              </button>
            </div>
            <pre className="overflow-x-auto p-5 font-mono text-sm leading-relaxed text-foreground">
              <code>{SNIPPET}</code>
            </pre>
            <BorderBeam size={90} duration={8} colorFrom="#7c5cff" colorTo="#c4b5fd" />
          </div>
        </div>
      </Section>

      {/* production */}
      <Section className="pt-0">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            From prototype to production
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground text-pretty">
            Ava is not a demo. It is orchestrated, evaluated, and deployed like a
            real product.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {PRODUCTION.map((p) => (
            <Card key={p.title} className="relative overflow-hidden p-6">
              <p.Icon className="h-8 w-8 text-primary" />
              <h3 className="mt-4 text-lg font-semibold">{p.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground text-pretty">
                {p.body}
              </p>
              {p.beam && (
                <BorderBeam size={80} duration={7} colorFrom="#7c5cff" colorTo="#c4b5fd" />
              )}
            </Card>
          ))}
        </div>
      </Section>

      {/* cta */}
      <Section>
        <Card className="relative overflow-hidden p-10 text-center sm:p-16">
          <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(50%_120%_at_50%_0%,rgba(124,92,255,0.18),transparent)]" />
          <h2 className="text-3xl font-semibold tracking-tight text-balance sm:text-4xl">
            Bring Ava to your product
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-muted-foreground text-pretty">
            Turn every confused user into a guided one — without writing a
            support article.
          </p>
          <div className="mt-8 flex justify-center">
            <a href="#embed">
              <ShimmerButton
                background="rgba(124,92,255,1)"
                className="h-12 px-7 text-base font-medium"
              >
                Get started
              </ShimmerButton>
            </a>
          </div>
          <BorderBeam size={160} duration={12} colorFrom="#7c5cff" colorTo="#c4b5fd" />
        </Card>
      </Section>

      {/* footer */}
      <footer className="w-full border-t border-border/60">
        <div className="mx-auto flex w-full max-w-6xl flex-col items-center justify-between gap-4 px-6 py-10 text-sm text-muted-foreground sm:flex-row">
          <div className="flex items-center gap-2">
            <span className="grid h-6 w-6 place-items-center rounded-md bg-primary text-xs text-primary-foreground">
              A
            </span>
            <span className="font-medium text-foreground">Ava</span>
          </div>
          <Separator className="sm:hidden" />
          <p>Built for the Capgemini × TrueFoundry × CrewAI hackathon.</p>
        </div>
      </footer>
    </main>
  );
}
