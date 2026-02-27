import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import AgentCard from "../components/AgentCard";
import {
  Calendar,
  Code,
  BookOpen,
  BarChart3,
  Building2,
  Sparkles,
  Users,
  Target,
  Clock,
  TrendingUp,
} from "lucide-react";
import { agentAPI } from "../utils/api";

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [userId, setUserId] = useState(null);

  useEffect(() => {
    // Check API health
    agentAPI.health().then(setHealth).catch(console.error);

    // Check for existing user in localStorage
    const savedUserId = localStorage.getItem("interviewai_user_id");
    if (savedUserId) {
      setUserId(savedUserId);
    }
  }, []);

  const agents = [
    {
      title: "Company DNA Analyzer",
      description: "Analyzes target companies and extracts interview patterns",
      icon: Building2,
      href: "/company-analyzer",
      color: "purple",
    },
    {
      title: "Planner",
      description: "Creates personalized learning paths",
      icon: Calendar,
      href: "/planner",
      color: "primary",
    },
    {
      title: "Evaluator",
      description: "Evaluates interview responses",
      icon: Code,
      href: "/evaluator",
      color: "secondary",
    },
    {
      title: "Tutor",
      description: "Provides personalized tutoring",
      icon: BookOpen,
      href: "/tutor",
      color: "orange",
    },
    {
      title: "Scheduler",
      description: "Optimizes study schedule",
      icon: Clock,
      href: "/scheduler",
      color: "purple",
    },
    {
      title: "Recommender",
      description: "Suggests next learning actions",
      icon: Sparkles,
      href: "/recommender",
      color: "primary",
    },
    {
      title: "Analytics",
      description: "Tracks performance and adapts",
      icon: BarChart3,
      href: "/analytics",
      color: "secondary",
    },
    {
      title: "Problem Solver",
      description: "Practice with company-specific problems",
      icon: Target,
      href: "/problems",
      color: "orange",
    },
  ];

  return (
    <Layout>
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          Welcome to{" "}
          <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            InterviewAI
          </span>
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Your 8-Agent AI System for Interview Preparation
        </p>
        {health && (
          <div className="mt-4 inline-flex items-center bg-green-100 text-green-700 px-4 py-2 rounded-full">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            System Status: Connected
          </div>
        )}
      </div>

      {/* Stats Section */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <Users className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold text-gray-900">50+</span>
          </div>
          <p className="text-gray-600">Companies Analyzed</p>
        </div>
        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <Target className="h-8 w-8 text-secondary" />
            <span className="text-2xl font-bold text-gray-900">100+</span>
          </div>
          <p className="text-gray-600">Practice Problems</p>
        </div>
        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <Clock className="h-8 w-8 text-purple-600" />
            <span className="text-2xl font-bold text-gray-900">8</span>
          </div>
          <p className="text-gray-600">AI Agents</p>
        </div>
        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="h-8 w-8 text-orange-600" />
            <span className="text-2xl font-bold text-gray-900">24/7</span>
          </div>
          <p className="text-gray-600">Personalized Learning</p>
        </div>
      </div>

      {/* Quick Start */}
      {!userId && (
        <div className="bg-gradient-to-r from-primary to-secondary rounded-2xl shadow-xl p-8 mb-12 text-white">
          <h2 className="text-2xl font-bold mb-4">Get Started in 30 Seconds</h2>
          <p className="mb-6 opacity-90">
            Complete the onboarding to get your personalized 8-week preparation
            plan
          </p>
          <button
            onClick={() => (window.location.href = "/planner")}
            className="bg-white text-primary px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            Start Onboarding →
          </button>
        </div>
      )}

      {/* Agents Grid */}
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Our AI Agents</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {agents.map((agent) => (
          <AgentCard key={agent.title} {...agent} />
        ))}
      </div>

      {/* Footer */}
      <footer className="mt-16 pt-8 border-t border-gray-200 text-center text-gray-600">
        <p>© 2024 InterviewAI - 8-Agent System for Interview Preparation</p>
      </footer>
    </Layout>
  );
}
