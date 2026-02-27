import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { agentAPI } from "../utils/api";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Clock,
  Target,
  Award,
  AlertTriangle,
  CheckCircle,
  Loader2,
  Calendar,
  Brain,
  Zap,
  BookOpen,
  Download,
  Filter,
  ChevronDown,
  ChevronUp,
  Star,
  Activity,
} from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from "recharts";

export default function Analytics() {
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [timeRange, setTimeRange] = useState("week"); // 'week', 'month', 'all'
  const [expandedSections, setExpandedSections] = useState({
    overview: true,
    patterns: true,
    topics: true,
    adaptations: true,
    predictions: true,
  });

  const COLORS = [
    "#3b82f6",
    "#10b981",
    "#8b5cf6",
    "#f59e0b",
    "#ef4444",
    "#ec4899",
  ];

  useEffect(() => {
    const savedUserId = localStorage.getItem("interviewai_user_id");
    if (savedUserId) {
      setUserId(savedUserId);
      fetchAnalytics(savedUserId);
    }
  }, []);

  const fetchAnalytics = async (uid) => {
    setLoading(true);
    try {
      const result = await agentAPI.getAnalytics(uid);
      setAnalytics(result);
    } catch (error) {
      console.error("Error fetching analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const getScoreColor = (score) => {
    if (score >= 8) return "text-green-600";
    if (score >= 6) return "text-yellow-600";
    return "text-red-600";
  };

  const getTrendIcon = (value) => {
    if (value > 0) return <TrendingUp className="h-4 w-4 text-green-500" />;
    if (value < 0) return <TrendingDown className="h-4 w-4 text-red-500" />;
    return null;
  };

  const prepareTopicData = () => {
    if (!analytics?.performance_patterns?.topic_mastery) return [];
    return Object.entries(analytics.performance_patterns.topic_mastery).map(
      ([topic, score]) => ({
        topic,
        score,
      })
    );
  };

  const prepareAccuracyData = () => {
    if (!analytics?.performance_patterns?.accuracy_trend) return [];
    return analytics.performance_patterns.accuracy_trend.map(
      (value, index) => ({
        session: `Session ${index + 1}`,
        score: value,
      })
    );
  };

  const renderOverview = () => {
    const metrics = analytics?.metrics || {};
    const patterns = analytics?.performance_patterns || {};

    return (
      <div className="space-y-6">
        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between mb-2">
              <Clock className="h-5 w-5 text-primary" />
              <span className="text-xs text-gray-500">Total</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {metrics.total_sessions || 0}
            </div>
            <div className="text-sm text-gray-600">Sessions Completed</div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between mb-2">
              <Target className="h-5 w-5 text-secondary" />
              <span className="text-xs text-gray-500">Avg</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {metrics.avg_score || 0}/10
            </div>
            <div className="text-sm text-gray-600">Average Score</div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="h-5 w-5 text-purple-600" />
              <span className="text-xs text-gray-500">Change</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {metrics.improvement_rate || 0}%
            </div>
            <div className="text-sm text-gray-600">Improvement Rate</div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between mb-2">
              <Activity className="h-5 w-5 text-orange-600" />
              <span className="text-xs text-gray-500">Consistency</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {metrics.consistency || 0}%
            </div>
            <div className="text-sm text-gray-600">Consistency Score</div>
          </div>
        </div>

        {/* Executive Summary */}
        {analytics?.report?.executive_summary && (
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
            <h3 className="font-semibold text-gray-900 mb-2">
              Executive Summary
            </h3>
            <p className="text-gray-700">
              {analytics.report.executive_summary}
            </p>
          </div>
        )}

        {/* Accuracy Trend Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Performance Trend</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={prepareAccuracyData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="session" />
                <YAxis domain={[0, 10]} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#3b82f6"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    );
  };

  const renderPatterns = () => {
    const patterns = analytics?.performance_patterns || {};

    return (
      <div className="space-y-6">
        {/* Strong vs Weak Areas */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
              Strong Areas
            </h3>
            {patterns.strong_topics?.length > 0 ? (
              <ul className="space-y-2">
                {patterns.strong_topics.map((topic, index) => (
                  <li key={index} className="flex items-center justify-between">
                    <span className="text-gray-700">{topic}</span>
                    <span className="text-green-600 font-medium">
                      ✓ Mastered
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500">No strong areas identified yet</p>
            )}
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
              Needs Improvement
            </h3>
            {patterns.weak_topics?.length > 0 ? (
              <ul className="space-y-2">
                {patterns.weak_topics.map((topic, index) => (
                  <li key={index} className="flex items-center justify-between">
                    <span className="text-gray-700">{topic}</span>
                    <span className="text-red-600 font-medium">
                      Focus needed
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500">No weak areas identified yet</p>
            )}
          </div>
        </div>

        {/* Error Patterns */}
        {patterns.most_common_errors?.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">
              Common Error Patterns
            </h3>
            <div className="space-y-3">
              {patterns.most_common_errors.map((error, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-gray-700">{error.error}</span>
                  <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">
                    {error.count} occurrences
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Learning Rate */}
        {patterns.learning_rate !== undefined && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Learning Velocity</h3>
            <div className="flex items-center space-x-4">
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 rounded-full"
                    style={{
                      width: `${Math.min(100, patterns.learning_rate)}%`,
                    }}
                  />
                </div>
              </div>
              <span className="text-2xl font-bold text-green-600">
                {patterns.learning_rate}%
              </span>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              {patterns.plateau_detected
                ? "⚠️ Learning plateau detected - try varying your practice"
                : "📈 Consistent improvement - keep up the great work!"}
            </p>
          </div>
        )}
      </div>
    );
  };

  const renderTopicMastery = () => {
    const topicData = prepareTopicData();

    return (
      <div className="space-y-6">
        {/* Topic Mastery Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Topic Mastery</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topicData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 10]} />
                <YAxis dataKey="topic" type="category" width={100} />
                <Tooltip />
                <Bar dataKey="score" fill="#3b82f6">
                  {topicData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Topic Heatmap */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Topic Heatmap</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {topicData.map((topic, index) => (
              <div key={index} className="text-center">
                <div className="text-sm font-medium text-gray-700 mb-1">
                  {topic.topic}
                </div>
                <div
                  className={`text-2xl font-bold ${getScoreColor(topic.score)}`}
                >
                  {topic.score}/10
                </div>
                <div className="w-full bg-gray-200 h-2 rounded-full mt-2">
                  <div
                    className={`h-full rounded-full ${
                      topic.score >= 8
                        ? "bg-green-500"
                        : topic.score >= 6
                        ? "bg-yellow-500"
                        : "bg-red-500"
                    }`}
                    style={{ width: `${topic.score * 10}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderAdaptations = () => {
    const adaptations = analytics?.adaptations || {};

    return (
      <div className="space-y-6">
        {/* System Adaptations */}
        {Object.entries(adaptations).map(
          ([type, items]) =>
            items.length > 0 && (
              <div key={type} className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4 capitalize">
                  {type.replace(/_/g, " ")}
                </h3>
                <div className="space-y-4">
                  {items.map((item, index) => (
                    <div key={index} className="border-l-4 border-primary pl-4">
                      <p className="font-medium text-gray-900">{item.action}</p>
                      <p className="text-sm text-gray-600 mt-1">
                        {item.reason}
                      </p>
                      {item.new_difficulty && (
                        <span className="inline-block mt-2 bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                          New difficulty: {item.new_difficulty}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )
        )}

        {/* Recommended Focus */}
        {analytics?.recommended_focus?.length > 0 && (
          <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Target className="h-5 w-5 text-orange-600 mr-2" />
              Recommended Focus Areas
            </h3>
            <div className="space-y-3">
              {analytics.recommended_focus.map((focus, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div
                    className={`w-2 h-2 rounded-full mt-2 ${
                      focus.priority === "high"
                        ? "bg-red-500"
                        : focus.priority === "medium"
                        ? "bg-yellow-500"
                        : "bg-green-500"
                    }`}
                  />
                  <div>
                    <p className="font-medium text-gray-900">{focus.area}</p>
                    <p className="text-sm text-gray-600">
                      {focus.suggested_action}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderPredictions = () => {
    const predictions = analytics?.predictions || {};

    return (
      <div className="space-y-6">
        {/* Readiness Projection */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">
            Interview Readiness Projection
          </h3>
          <div className="flex items-center justify-between mb-4">
            <span className="text-gray-600">Current</span>
            <span className="text-gray-600">4 Weeks</span>
          </div>
          <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="absolute h-full bg-blue-500 rounded-full"
              style={{
                width: `${predictions.projected_readiness_4weeks || 0}%`,
              }}
            />
          </div>
          <p className="text-right mt-2 text-2xl font-bold text-blue-600">
            {predictions.projected_readiness_4weeks || 0}%
          </p>
        </div>

        {/* Confidence Interval */}
        {predictions.confidence_interval && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">
              Score Confidence Interval
            </h3>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">
                Lower: {predictions.confidence_interval.lower}
              </span>
              <span className="text-gray-600">
                Upper: {predictions.confidence_interval.upper}
              </span>
            </div>
            <div className="relative h-2 bg-gray-200 rounded-full mt-2">
              <div
                className="absolute h-full bg-green-500 rounded-full"
                style={{
                  left: `${
                    (predictions.confidence_interval.lower / 10) * 100
                  }%`,
                  right: `${
                    100 - (predictions.confidence_interval.upper / 10) * 100
                  }%`,
                  width: `${
                    ((predictions.confidence_interval.upper -
                      predictions.confidence_interval.lower) /
                      10) *
                    100
                  }%`,
                }}
              />
            </div>
          </div>
        )}

        {/* Risk Assessment */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold mb-2">Burnout Risk</h3>
            <div
              className={`text-2xl font-bold ${
                predictions.burnout_risk === "high"
                  ? "text-red-600"
                  : predictions.burnout_risk === "medium"
                  ? "text-yellow-600"
                  : "text-green-600"
              }`}
            >
              {predictions.burnout_risk?.toUpperCase() || "LOW"}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold mb-2">Sessions to Target</h3>
            <div className="text-2xl font-bold text-purple-600">
              {predictions.estimated_sessions_to_target || 0}
            </div>
          </div>
        </div>

        {/* Persistent Weak Areas */}
        {predictions.persistent_weak_areas?.length > 0 && (
          <div className="bg-red-50 rounded-lg p-6">
            <h3 className="font-semibold text-red-800 mb-2">
              Persistent Weak Areas
            </h3>
            <p className="text-red-700 mb-3">
              These topics need extra attention in your upcoming sessions:
            </p>
            <div className="flex flex-wrap gap-2">
              {predictions.persistent_weak_areas.map((area, index) => (
                <span
                  key={index}
                  className="bg-red-200 text-red-800 px-3 py-1 rounded-full text-sm"
                >
                  {area}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderAchievements = () => {
    const achievements = analytics?.report?.achievements || [];

    if (achievements.length === 0) return null;

    return (
      <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Award className="h-5 w-5 text-yellow-600 mr-2" />
          Achievements Unlocked
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {achievements.map((achievement, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl mb-2">{achievement.icon}</div>
              <div className="font-semibold text-sm">{achievement.title}</div>
              <div className="text-xs text-gray-600">
                {achievement.description}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const sections = [
    {
      id: "overview",
      title: "Overview",
      icon: BarChart3,
      content: renderOverview,
    },
    {
      id: "patterns",
      title: "Performance Patterns",
      icon: Brain,
      content: renderPatterns,
    },
    {
      id: "topics",
      title: "Topic Mastery",
      icon: BookOpen,
      content: renderTopicMastery,
    },
    {
      id: "adaptations",
      title: "System Adaptations",
      icon: Zap,
      content: renderAdaptations,
    },
    {
      id: "predictions",
      title: "Predictions & Insights",
      icon: TrendingUp,
      content: renderPredictions,
    },
  ];

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Performance Analytics
          </h1>
          <p className="text-gray-600">
            Deep insights into your learning journey and AI-powered adaptations
          </p>
        </div>

        {/* Time Range Filter */}
        <div className="flex items-center justify-end space-x-2 mb-6">
          <Filter className="h-4 w-4 text-gray-400" />
          {["week", "month", "all"].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 rounded-lg text-sm ${
                timeRange === range
                  ? "bg-primary text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {range.charAt(0).toUpperCase() + range.slice(1)}
            </button>
          ))}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
            <p className="text-gray-600">Analyzing your performance data...</p>
          </div>
        )}

        {/* Analytics Display */}
        {!loading && analytics && (
          <div className="space-y-4">
            {/* Achievements */}
            {renderAchievements()}

            {/* Sections */}
            {sections.map((section) => {
              const Icon = section.icon;
              const isExpanded = expandedSections[section.id];

              return (
                <div
                  key={section.id}
                  className="bg-white rounded-xl shadow-lg overflow-hidden"
                >
                  <button
                    onClick={() => toggleSection(section.id)}
                    className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <Icon className="h-5 w-5 text-primary" />
                      <h2 className="text-xl font-semibold">{section.title}</h2>
                    </div>
                    {isExpanded ? (
                      <ChevronUp className="h-5 w-5 text-gray-400" />
                    ) : (
                      <ChevronDown className="h-5 w-5 text-gray-400" />
                    )}
                  </button>

                  {isExpanded && (
                    <div className="px-6 pb-6">{section.content()}</div>
                  )}
                </div>
              );
            })}

            {/* Export Button */}
            <div className="flex justify-end">
              <button
                onClick={() => {
                  // Export analytics as JSON
                  const dataStr = JSON.stringify(analytics, null, 2);
                  const dataUri =
                    "data:application/json;charset=utf-8," +
                    encodeURIComponent(dataStr);
                  const exportFileDefaultName = `analytics_${userId}_${new Date().toISOString()}.json`;
                  const linkElement = document.createElement("a");
                  linkElement.setAttribute("href", dataUri);
                  linkElement.setAttribute("download", exportFileDefaultName);
                  linkElement.click();
                }}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <Download className="h-4 w-4" />
                <span>Export Analytics</span>
              </button>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !analytics && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <BarChart3 className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-700 mb-2">
              No Analytics Yet
            </h3>
            <p className="text-gray-500">
              Complete some practice sessions to see your performance analytics
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
}
