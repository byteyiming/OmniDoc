import Sidebar from '@/components/Sidebar';
import ErrorBoundary from '@/components/ErrorBoundary';

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <main className="flex-1 overflow-y-auto custom-scrollbar">
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </main>
    </div>
  );
}
