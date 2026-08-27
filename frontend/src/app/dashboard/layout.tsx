import { AuthProvider } from "@/components/AuthContext";
import { Sidebar } from "@/components/Sidebar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <div className="flex min-h-screen bg-[#F5F6F8]">
        <Sidebar />
        <main className="flex-1 px-8 py-8">{children}</main>
      </div>
    </AuthProvider>
  );
}