import Link from "next/link";
import { useRouter } from "next/router";
import {
  Home,
  Calendar,
  Code,
  BookOpen,
  BarChart3,
  Building2,
  Sparkles,
  Menu,
  X,
} from "lucide-react";
import { useState } from "react";

const Navbar = () => {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);

  const navItems = [
    { name: "Dashboard", href: "/", icon: Home },
    { name: "Planner", href: "/planner", icon: Calendar },
    { name: "Evaluator", href: "/evaluator", icon: Code },
    { name: "Tutor", href: "/tutor", icon: BookOpen },
    { name: "Scheduler", href: "/scheduler", icon: Calendar },
    { name: "Company Analyzer", href: "/company-analyzer", icon: Building2 },
    { name: "Recommender", href: "/recommender", icon: Sparkles },
    { name: "Analytics", href: "/analytics", icon: BarChart3 },
    { name: "Problems", href: "/problems", icon: Code },
  ];

  return (
    <nav className="bg-white shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center space-x-2">
            <Sparkles className="h-8 w-8 text-primary" />
            <span className="font-bold text-xl text-gray-900">InterviewAI</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex space-x-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                    ${
                      router.pathname === item.href
                        ? "bg-primary text-white"
                        : "text-gray-700 hover:bg-gray-100"
                    }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100"
          >
            {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden py-4 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className={`flex items-center space-x-2 px-4 py-3 rounded-lg text-sm font-medium
                    ${
                      router.pathname === item.href
                        ? "bg-primary text-white"
                        : "text-gray-700 hover:bg-gray-100"
                    }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
