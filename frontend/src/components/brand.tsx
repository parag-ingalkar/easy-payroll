"use client";

import { cn } from "@/lib/utils";

export function Logo({ className, size = 40 }: { className?: string; size?: number }) {
  return (
    <div
      className={cn(
        "relative flex items-center justify-center rounded-2xl bg-jungle-teal text-white shadow-sm",
        className
      )}
      style={{ width: size, height: size }}
    >
      <svg
        width={size * 0.58}
        height={size * 0.58}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <rect x="2" y="6" width="20" height="13" rx="2.5" />
        <path d="M2 10h20" />
        <path d="M7 15h4" />
        <circle cx="16.5" cy="14.5" r="1.5" />
      </svg>
    </div>
  );
}

export function Wordmark({ className }: { className?: string }) {
  return (
    <span className={cn("font-semibold tracking-tight text-graphite", className)}>
      Pagar<span className="text-jungle-teal">Pal</span>
    </span>
  );
}
