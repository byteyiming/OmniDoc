'use client';

import Link from 'next/link';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-white/5 bg-[#0B0F19] py-8 mt-auto">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between space-y-4 sm:flex-row sm:space-y-0">
          <div className="text-sm text-gray-500">
            © {currentYear} OmniDoc. Crafted by AI Agents.
          </div>
          <div className="flex items-center space-x-6">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1 text-sm text-gray-500 transition-colors hover:text-indigo-400"
            >
              <span>GitHub</span>
            </a>
            <Link
              href="#"
              className="text-sm text-gray-500 transition-colors hover:text-indigo-400"
            >
              Terms
            </Link>
            <Link
              href="#"
              className="text-sm text-gray-500 transition-colors hover:text-indigo-400"
            >
              Privacy
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
