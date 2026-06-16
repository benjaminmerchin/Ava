"use client";

import React, { forwardRef, useRef } from "react";
import {
  MousePointerClick,
  Eye,
  BookOpen,
  Compass,
  Volume2,
} from "lucide-react";

import { AnimatedBeam } from "@/components/ui/animated-beam";
import { cn } from "@/lib/utils";

const Node = forwardRef<
  HTMLDivElement,
  { className?: string; children: React.ReactNode }
>(({ className, children }, ref) => (
  <div
    ref={ref}
    className={cn(
      "z-10 flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2 text-xs font-medium shadow-[0_0_24px_-14px_var(--color-primary)] sm:text-sm",
      className
    )}
  >
    {children}
  </div>
));
Node.displayName = "Node";

const FROM = "#7c5cff";
const TO = "#c4b5fd";

export function ArchitectureBeam() {
  const containerRef = useRef<HTMLDivElement>(null);
  const domRef = useRef<HTMLDivElement>(null);
  const percRef = useRef<HTMLDivElement>(null);
  const knowRef = useRef<HTMLDivElement>(null);
  const guideRef = useRef<HTMLDivElement>(null);
  const outRef = useRef<HTMLDivElement>(null);

  return (
    <div
      ref={containerRef}
      className="relative mx-auto flex h-[340px] w-full max-w-3xl items-center justify-between px-1 sm:px-6"
    >
      <div className="flex flex-col">
        <Node ref={domRef}>
          <MousePointerClick className="h-4 w-4 text-primary" />
          DOM state
        </Node>
      </div>

      <div className="flex flex-col gap-16">
        <Node ref={percRef}>
          <Eye className="h-4 w-4 text-primary" />
          Perception
        </Node>
        <Node ref={knowRef}>
          <BookOpen className="h-4 w-4 text-primary" />
          Knowledge
        </Node>
      </div>

      <div className="flex flex-col">
        <Node ref={guideRef}>
          <Compass className="h-4 w-4 text-primary" />
          Guide
        </Node>
      </div>

      <div className="flex flex-col">
        <Node ref={outRef} className="border-primary/40">
          <Volume2 className="h-4 w-4 text-primary" />
          Voice + highlight
        </Node>
      </div>

      <AnimatedBeam
        containerRef={containerRef}
        fromRef={domRef}
        toRef={percRef}
        curvature={-40}
        gradientStartColor={FROM}
        gradientStopColor={TO}
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={domRef}
        toRef={knowRef}
        curvature={40}
        gradientStartColor={FROM}
        gradientStopColor={TO}
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={percRef}
        toRef={guideRef}
        curvature={40}
        gradientStartColor={FROM}
        gradientStopColor={TO}
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={knowRef}
        toRef={guideRef}
        curvature={-40}
        gradientStartColor={FROM}
        gradientStopColor={TO}
      />
      <AnimatedBeam
        containerRef={containerRef}
        fromRef={guideRef}
        toRef={outRef}
        gradientStartColor={FROM}
        gradientStopColor={TO}
      />
    </div>
  );
}
