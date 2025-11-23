'use client';

export default function SkipLink() {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-[#007BFF] focus:text-white focus:rounded-[4px] focus:font-semibold focus:outline-none focus:ring-2 focus:ring-[#007BFF] focus:ring-offset-2"
    >
      Skip to main content
    </a>
  );
}

