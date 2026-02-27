import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { agentAPI } from "../utils/api";
import {
  Sparkles,
  Target,
  Clock,
  TrendingUp,
  ChevronRight,
  Loader2,
  CheckCircle,
  AlertCircle,
  Lightbulb,
  BookOpen,
  Zap,
  BarChart3,
  ThumbsUp,
  Calendar,
  Code,
  RefreshCw,
  Star,
} from "lucide-react";

export default function Recommender() {
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recommendation, setRecommendation] = useState(null);
  const [recommendationType, setRecommendationType] = useState("learning"); // 'learning' or 'problem'
  const [userContext, setUserContext] = useState({
    time_of_day: new Date().getHours(),
    recent_sessions: 0,
    last_session_time: null,
    mood: "neutral",
  });
  const [userStats, setUserStats] = useState({
    level: "intermediate",
    strengths: [],
    weaknesses: [],
    completed_sessions: 0,
    average_score: 0,
  });

  useEffect(() => {
    const savedUserId = localStorage.getItem("interviewai_user_id");
    if (savedUserId) {
      setUserId(savedUserId);
      fetchUserStats(savedUserId);
    }
    updateTimeContext();
  }, []);

  const updateTimeContext = () => {
    const hour = new Date().getHours();
    let timeOfDay = "morning";
    if (hour >= 12 && hour < 17) timeOfDay = "afternoon";
    else if (hour >= 17 && hour < 21) timeOfDay = "evening";
    else if (hour >= 21 || hour < 5) timeOfDay = "night";

    setUserContext((prev) => ({
      ...prev,
      time_of_day: hour,
      period: timeOfDay,
    }));
  };

  const fetchUserStats = async (uid) => {
    try {
      const progress = await agentAPI.getUserProgress(uid);
      setUserStats((prev) => ({
        ...prev,
        completed_sessions: progress.total_sessions || 0,
        average_score: progress.average_score || 0,
      }));
    } catch (error) {
      console.error("Error fetching user stats:", error);
    }
  };

  const handleGetLearningRecommendation = async () => {
    setLoading(true);
    setRecommendationType("learning");
    try {
      const result = await agentAPI.getRecommendation(userId || "test_001");
      setRecommendation(result);
    } catch (error) {
      console.error("Error getting recommendation:", error);
      alert("Failed to get recommendation. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleGetProblemRecommendation = async () => {
    setLoading(true);
    setRecommendationType("problem");
    try {
      const result = await agentAPI.getProblemRecommendation(
        userId || "test_001"
      );
      setRecommendation(result);
    } catch (error) {
      console.error("Error getting problem recommendation:", error);
      alert("Failed to get problem recommendation. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getTimeBasedMessage = () => {
    const hour = userContext.time_of_day;
    if (hour < 12) return "Good morning! Ready for a productive session?";
    if (hour < 17) return "Good afternoon! Keep up the momentum.";
    if (hour < 21) return "Good evening! Perfect time for some practice.";
    return "Late night study session? You're dedicated!";
  };

  const getMoodEmoji = () => {
    const score = userStats.average_score;
    if (score >= 8) return "🌟";
    if (score >= 6) return "😊";
    if (score >= 4) return "😐";
    return "💪";
  };

  const renderLearningRecommendation = () => {
    if (!recommendation) return null;

    const primary = recommendation.primary_recommendation;

    return (
      <div className="space-y-6">
        {/* Primary Recommendation */}
        <div className="bg-gradient-to-r from-primary to-secondary rounded-lg p-6 text-white">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-sm opacity-90 mb-1 block">Next Action</span>
              <h2 className="text-2xl font-bold mb-2">{primary.action}</h2>
              <p className="text-lg mb-4">Topic: {primary.topic}</p>

              <div className="flex items-center space-x-4">
                <span className="flex items-center">
                  <Clock className="h-4 w-4 mr-1" />
                  {primary.duration_minutes} minutes
                </span>
                <span className="flex items-center">
                  <Target className="h-4 w-4 mr-1" />
                  {Math.round(primary.confidence * 100)}% confidence
                </span>
              </div>
            </div>
            <Sparkles className="h-12 w-12 opacity-50" />
          </div>
        </div>

        {/* Reasoning */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <Lightbulb className="h-5 w-5 text-yellow-500 mr-2" />
            Why this recommendation?
          </h3>
          <p className="text-gray-700">{recommendation.reasoning}</p>
        </div>

        {/* Resources */}
        {primary.resources && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-3">Resources</h3>
            <div className="space-y-3">
              {primary.resources.map((resource, index) => (
                <div key={index} className="flex items-center space-x-3">
                  {resource.type === "video" && (
                    <Zap className="h-5 w-5 text-red-500" />
                  )}
                  {resource.type === "practice" && (
                    <Code className="h-5 w-5 text-green-500" />
                  )}
                  {resource.type === "study" && (
                    <BookOpen className="h-5 w-5 text-blue-500" />
                  )}
                  <div>
                    <p className="font-medium">
                      {resource.type}:{" "}
                      {resource.topic || `${resource.count || 1} problems`}
                    </p>
                    {resource.duration && (
                      <p className="text-sm text-gray-600">
                        {resource.duration} minutes
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Success Criteria */}
        <div className="bg-green-50 rounded-lg p-4">
          <h3 className="font-semibold text-green-800 mb-2 flex items-center">
            <CheckCircle className="h-5 w-5 mr-2" />
            Success Criteria
          </h3>
          <p className="text-green-700">{primary.success_criteria}</p>
        </div>

        {/* Alternatives */}
        {recommendation.alternatives && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-3">Alternative Options</h3>
            <div className="space-y-3">
              {recommendation.alternatives.map((alt, index) => (
                <div
                  key={index}
                  className="border rounded-lg p-3 hover:bg-gray-50 cursor-pointer"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{alt.action}</p>
                      <p className="text-sm text-gray-600">{alt.topic}</p>
                    </div>
                    <span className="text-sm text-gray-500">
                      {alt.duration_minutes} min
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Impact Estimate */}
        {recommendation.estimated_impact && (
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4">
            <h3 className="font-semibold mb-2">Expected Impact</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Readiness</p>
                <p className="text-lg font-semibold text-green-600">
                  {recommendation.estimated_impact.readiness_impact}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Time Investment</p>
                <p className="text-lg font-semibold">
                  {recommendation.estimated_impact.time_investment}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderProblemRecommendation = () => {
    if (!recommendation?.recommendation) return null;

    const rec = recommendation.recommendation.recommendation;

    return (
      <div className="space-y-6">
        {/* Problem Card */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg p-6 text-white">
          <span className="text-sm opacity-90 mb-2 block">
            Recommended Problem
          </span>
          <h2 className="text-2xl font-bold mb-2">{rec.problem.title}</h2>

          <div className="flex items-center space-x-4 mb-4">
            <span
              className={`px-2 py-1 rounded text-sm ${
                rec.problem.difficulty === "Easy"
                  ? "bg-green-500"
                  : rec.problem.difficulty === "Medium"
                  ? "bg-yellow-500"
                  : "bg-red-500"
              }`}
            >
              {rec.problem.difficulty}
            </span>
            <span className="flex items-center">
              <Clock className="h-4 w-4 mr-1" />
              {rec.expected_time} min
            </span>
          </div>

          <a
            href={rec.problem.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center bg-white text-purple-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors"
          >
            Solve on LeetCode
            <ChevronRight className="h-4 w-4 ml-1" />
          </a>
        </div>

        {/* Company Context */}
        {rec.problem.company_context && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <Building2 className="h-5 w-5 text-primary mr-2" />
              Company Context
            </h3>
            <div className="space-y-2">
              <p className="text-gray-700">
                This problem was asked by{" "}
                {Object.keys(rec.problem.company_context).join(", ")}
              </p>
              {rec.problem.company_context.frequency && (
                <p className="text-sm text-gray-600">
                  Frequency: {rec.problem.company_context.frequency}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Topics */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-3">Topics</h3>
          <div className="flex flex-wrap gap-2">
            {rec.problem.topics?.map((topic, index) => (
              <span
                key={index}
                className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
              >
                {topic}
              </span>
            ))}
          </div>
        </div>

        {/* Learning Path */}
        {rec.learning_path && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-3">Your Learning Path</h3>
            <div className="space-y-3">
              {rec.learning_path.map((step, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      step.type === "current"
                        ? "bg-primary text-white"
                        : step.type === "prerequisite"
                        ? "bg-yellow-500 text-white"
                        : "bg-gray-200"
                    }`}
                  >
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-medium">{step.topic}</p>
                    <p className="text-sm text-gray-600">{step.reason}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {step.estimated_time}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Next Milestone */}
        {rec.next_milestone && (
          <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4">
            <h3 className="font-semibold mb-2 flex items-center">
              <Target className="h-5 w-5 text-green-600 mr-2" />
              Next Milestone
            </h3>
            <p className="text-gray-700">
              {rec.next_milestone.problems_remaining} more problems to reach{" "}
              {rec.next_milestone.next_level}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              Estimated: {rec.next_milestone.estimated_days} days
            </p>
          </div>
        )}
      </div>
    );
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI Recommender Agent
          </h1>
          <p className="text-gray-600">
            Personalized recommendations based on your context and progress
          </p>
        </div>

        {/* User Context Bar */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-4xl">{getMoodEmoji()}</div>
              <div>
                <h3 className="font-semibold text-gray-900">
                  {getTimeBasedMessage()}
                </h3>
                <p className="text-sm text-gray-600">
                  Completed {userStats.completed_sessions} sessions • Avg score:{" "}
                  {userStats.average_score}/10
                </p>
              </div>
            </div>
            <button
              onClick={() => {
                updateTimeContext();
                setRecommendation(null);
              }}
              className="p-2 hover:bg-white rounded-lg transition-colors"
              title="Refresh context"
            >
              <RefreshCw className="h-5 w-5 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          <button
            onClick={handleGetLearningRecommendation}
            disabled={loading}
            className={`p-6 rounded-xl border-2 transition-all ${
              recommendationType === "learning" && recommendation
                ? "border-primary bg-blue-50"
                : "border-gray-200 hover:border-primary hover:bg-blue-50"
            }`}
          >
            <Sparkles
              className={`h-8 w-8 mx-auto mb-2 ${
                recommendationType === "learning" && recommendation
                  ? "text-primary"
                  : "text-gray-400"
              }`}
            />
            <h3 className="font-semibold">Learning Recommendation</h3>
            <p className="text-sm text-gray-600">What to study next</p>
          </button>

          <button
            onClick={handleGetProblemRecommendation}
            disabled={loading}
            className={`p-6 rounded-xl border-2 transition-all ${
              recommendationType === "problem" && recommendation
                ? "border-primary bg-blue-50"
                : "border-gray-200 hover:border-primary hover:bg-blue-50"
            }`}
          >
            <Code
              className={`h-8 w-8 mx-auto mb-2 ${
                recommendationType === "problem" && recommendation
                  ? "text-primary"
                  : "text-gray-400"
              }`}
            />
            <h3 className="font-semibold">Problem Recommendation</h3>
            <p className="text-sm text-gray-600">Next coding challenge</p>
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
            <p className="text-gray-600">Analyzing your context...</p>
            <p className="text-sm text-gray-500 mt-2">
              Finding the best recommendation for you
            </p>
          </div>
        )}

        {/* Recommendation Display */}
        {!loading && recommendation && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            {recommendationType === "learning"
              ? renderLearningRecommendation()
              : renderProblemRecommendation()}
          </div>
        )}

        {/* Empty State */}
        {!loading && !recommendation && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <Sparkles className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-700 mb-2">
              No Recommendation Yet
            </h3>
            <p className="text-gray-500 mb-6">
              Click one of the buttons above to get a personalized
              recommendation
            </p>

            {/* Quick Tips */}
            <div className="grid grid-cols-2 gap-4 max-w-md mx-auto">
              <div className="text-left p-3 bg-gray-50 rounded-lg">
                <Clock className="h-5 w-5 text-primary mb-2" />
                <h4 className="font-medium text-sm">Time-based</h4>
                <p className="text-xs text-gray-600">
                  Recommendations adapt to time of day
                </p>
              </div>
              <div className="text-left p-3 bg-gray-50 rounded-lg">
                <BarChart3 className="h-5 w-5 text-secondary mb-2" />
                <h4 className="font-medium text-sm">Progress-based</h4>
                <p className="text-xs text-gray-600">
                  Based on your performance
                </p>
              </div>
              <div className="text-left p-3 bg-gray-50 rounded-lg">
                <Target className="h-5 w-5 text-purple-600 mb-2" />
                <h4 className="font-medium text-sm">Goal-oriented</h4>
                <p className="text-xs text-gray-600">
                  Aligned with target companies
                </p>
              </div>
              <div className="text-left p-3 bg-gray-50 rounded-lg">
                <TrendingUp className="h-5 w-5 text-orange-600 mb-2" />
                <h4 className="font-medium text-sm">Adaptive</h4>
                <p className="text-xs text-gray-600">
                  Adjusts difficulty based on skill
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
