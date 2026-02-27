import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { agentAPI } from "../utils/api";
import {
  Code,
  Send,
  Loader2,
  CheckCircle,
  XCircle,
  AlertCircle,
  TrendingUp,
  Clock,
  Cpu,
  Zap,
  BookOpen,
  Copy,
  Check,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/cjs/styles/prism";

export default function Evaluator() {
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const [activeTab, setActiveTab] = useState("submit");
  const [copied, setCopied] = useState(false);
  const [formData, setFormData] = useState({
    question: "",
    question_type: "technical",
    user_response: "",
    expected_areas: "",
    context: {
      experience_years: 3,
      target_role: "SDE",
      difficulty: "intermediate",
    },
  });

  const [codeData, setCodeData] = useState({
    problem_id: "two-sum",
    code: "",
    platform: "leetcode",
  });

  const questionTypes = [
    "technical",
    "behavioral",
    "system_design",
    "coding",
    "problem_solving",
  ];

  const popularProblems = [
    { id: "two-sum", title: "Two Sum", difficulty: "Easy" },
    { id: "valid-parentheses", title: "Valid Parentheses", difficulty: "Easy" },
    {
      id: "merge-two-sorted-lists",
      title: "Merge Two Sorted Lists",
      difficulty: "Easy",
    },
    { id: "maximum-subarray", title: "Maximum Subarray", difficulty: "Medium" },
    {
      id: "number-of-islands",
      title: "Number of Islands",
      difficulty: "Medium",
    },
    {
      id: "trapping-rain-water",
      title: "Trapping Rain Water",
      difficulty: "Hard",
    },
  ];

  useEffect(() => {
    // Get user ID from localStorage
    const savedUserId = localStorage.getItem("interviewai_user_id");
    if (savedUserId) {
      setUserId(savedUserId);
    }
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith("context.")) {
      const contextField = name.split(".")[1];
      setFormData((prev) => ({
        ...prev,
        context: {
          ...prev.context,
          [contextField]: value,
        },
      }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleCodeChange = (e) => {
    setCodeData((prev) => ({ ...prev, code: e.target.value }));
  };

  const handleSubmitQuestion = async () => {
    setLoading(true);
    try {
      const result = await agentAPI.evaluateResponse({
        user_id: userId || "test_001",
        question: formData.question,
        question_type: formData.question_type,
        user_response: formData.user_response,
        expected_areas: formData.expected_areas
          .split(",")
          .map((area) => area.trim()),
        context: formData.context,
      });
      setEvaluation(result);
      setActiveTab("results");
    } catch (error) {
      console.error("Error evaluating response:", error);
      alert("Failed to evaluate response. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitCode = async () => {
    setLoading(true);
    try {
      const result = await agentAPI.submitCode({
        user_id: userId || "test_001",
        problem_id: codeData.problem_id,
        code: codeData.code,
        platform: codeData.platform,
      });
      setEvaluation(result);
      setActiveTab("results");
    } catch (error) {
      console.error("Error submitting code:", error);
      alert("Failed to analyze code. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getScoreColor = (score) => {
    if (score >= 8) return "text-green-600";
    if (score >= 6) return "text-yellow-600";
    return "text-red-600";
  };

  const renderEvaluationResults = () => (
    <div className="space-y-6">
      {/* Overall Score */}
      <div className="bg-gradient-to-r from-primary to-secondary rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold mb-1">Overall Score</h3>
            <div className="text-4xl font-bold">
              {evaluation.scores?.overall || 0}/10
            </div>
            <div className="text-sm opacity-90 mt-1">
              {evaluation.scores?.normalized_overall || 0}% percentile
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm opacity-90">Confidence</div>
            <div className="text-2xl font-semibold">
              {Math.round(
                (evaluation.confidence_metrics?.confidence || 0) * 100
              )}
              %
            </div>
          </div>
        </div>
      </div>

      {/* Category Scores */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {evaluation.scores &&
          Object.entries(evaluation.scores)
            .filter(([key]) => !["overall", "normalized_overall"].includes(key))
            .map(([key, value]) => (
              <div key={key} className="bg-white rounded-lg shadow p-4">
                <div className="text-sm text-gray-600 capitalize mb-1">
                  {key.replace(/_/g, " ")}
                </div>
                <div className={`text-2xl font-bold ${getScoreColor(value)}`}>
                  {value}/10
                </div>
              </div>
            ))}
      </div>

      {/* Feedback Summary */}
      {evaluation.feedback && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-3">Feedback</h3>
          <p className="text-gray-700 mb-4">{evaluation.feedback.summary}</p>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-green-600 mb-2">Strengths</h4>
              <ul className="space-y-2">
                {evaluation.feedback.strengths_highlighted?.map(
                  (strength, i) => (
                    <li key={i} className="flex items-start space-x-2">
                      <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{strength}</span>
                    </li>
                  )
                )}
              </ul>
            </div>

            <div>
              <h4 className="font-medium text-orange-600 mb-2">
                Improvement Areas
              </h4>
              <ul className="space-y-2">
                {evaluation.feedback.improvement_areas?.map((area, i) => (
                  <li key={i} className="flex items-start space-x-2">
                    <AlertCircle className="h-5 w-5 text-orange-500 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700">
                      {area.suggestion || area.area}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Code Analysis Specific */}
      {evaluation.analysis && (
        <>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Code Analysis</h3>

            <div className="grid md:grid-cols-2 gap-6 mb-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Cpu className="h-5 w-5 text-primary" />
                  <span className="font-medium">Time Complexity</span>
                </div>
                <div className="text-lg font-semibold text-gray-900">
                  {evaluation.analysis.complexity_analysis?.time_complexity ||
                    "O(n)"}
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {evaluation.analysis.complexity_analysis?.time_explanation}
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Zap className="h-5 w-5 text-secondary" />
                  <span className="font-medium">Space Complexity</span>
                </div>
                <div className="text-lg font-semibold text-gray-900">
                  {evaluation.analysis.complexity_analysis?.space_complexity ||
                    "O(1)"}
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {evaluation.analysis.complexity_analysis?.space_explanation}
                </p>
              </div>
            </div>

            {evaluation.analysis.complexity_analysis?.bottlenecks?.length >
              0 && (
              <div className="mb-4">
                <h4 className="font-medium text-gray-700 mb-2">Bottlenecks</h4>
                <ul className="space-y-1">
                  {evaluation.analysis.complexity_analysis.bottlenecks.map(
                    (bottleneck, i) => (
                      <li
                        key={i}
                        className="flex items-start space-x-2 text-sm"
                      >
                        <AlertCircle className="h-4 w-4 text-red-500 flex-shrink-0 mt-0.5" />
                        <span>{bottleneck}</span>
                      </li>
                    )
                  )}
                </ul>
              </div>
            )}

            {evaluation.analysis.complexity_analysis?.optimizations?.length >
              0 && (
              <div>
                <h4 className="font-medium text-gray-700 mb-2">
                  Optimizations
                </h4>
                <ul className="space-y-1">
                  {evaluation.analysis.complexity_analysis.optimizations.map(
                    (opt, i) => (
                      <li
                        key={i}
                        className="flex items-start space-x-2 text-sm"
                      >
                        <Zap className="h-4 w-4 text-secondary flex-shrink-0 mt-0.5" />
                        <span>{opt}</span>
                      </li>
                    )
                  )}
                </ul>
              </div>
            )}
          </div>

          {/* Edge Cases */}
          {evaluation.analysis.edge_case_coverage && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-3">Edge Case Coverage</h3>
              <div className="flex items-center space-x-4 mb-4">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary rounded-full h-2"
                    style={{
                      width: `${
                        evaluation.analysis.edge_case_coverage.coverage_score ||
                        0
                      }%`,
                    }}
                  />
                </div>
                <span className="font-semibold">
                  {evaluation.analysis.edge_case_coverage.coverage_score || 0}%
                </span>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                {evaluation.analysis.edge_case_coverage.edge_cases_handled
                  ?.length > 0 && (
                  <div>
                    <h4 className="font-medium text-green-600 mb-2">
                      Handled ✓
                    </h4>
                    <ul className="space-y-1">
                      {evaluation.analysis.edge_case_coverage.edge_cases_handled.map(
                        (edge, i) => (
                          <li key={i} className="text-sm text-gray-700">
                            • {edge}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                )}

                {evaluation.analysis.edge_case_coverage.edge_cases_missing
                  ?.length > 0 && (
                  <div>
                    <h4 className="font-medium text-red-600 mb-2">Missing ✗</h4>
                    <ul className="space-y-1">
                      {evaluation.analysis.edge_case_coverage.edge_cases_missing.map(
                        (edge, i) => (
                          <li key={i} className="text-sm text-gray-700">
                            • {edge}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}

      {/* Next Steps */}
      {evaluation.next_recommendation && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-3">Recommended Next Steps</h3>
          <div className="space-y-3">
            <p className="text-gray-700">
              {evaluation.next_recommendation.recommendation?.instruction}
            </p>
            {evaluation.next_recommendation.recommendation?.problem && (
              <div className="bg-white rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold">
                      {
                        evaluation.next_recommendation.recommendation.problem
                          .title
                      }
                    </h4>
                    <p className="text-sm text-gray-600">
                      Difficulty:{" "}
                      {
                        evaluation.next_recommendation.recommendation.problem
                          .difficulty
                      }
                    </p>
                  </div>
                  <a
                    href={
                      evaluation.next_recommendation.recommendation.problem.url
                    }
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary text-sm"
                  >
                    Solve on LeetCode
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Try Again Button */}
      <button
        onClick={() => {
          setEvaluation(null);
          setActiveTab("submit");
        }}
        className="w-full btn-primary"
      >
        Evaluate Another Response
      </button>
    </div>
  );

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI Evaluator Agent
          </h1>
          <p className="text-gray-600">
            Get instant feedback on your interview responses and code solutions
          </p>
        </div>

        {/* Tabs */}
        <div className="flex space-x-4 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab("submit")}
            className={`px-4 py-2 font-medium transition-colors relative ${
              activeTab === "submit"
                ? "text-primary border-b-2 border-primary"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Submit Response
          </button>
          <button
            onClick={() => setActiveTab("code")}
            className={`px-4 py-2 font-medium transition-colors relative ${
              activeTab === "code"
                ? "text-primary border-b-2 border-primary"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Submit Code
          </button>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          {activeTab === "results" && evaluation ? (
            renderEvaluationResults()
          ) : activeTab === "submit" ? (
            <div className="space-y-6">
              {/* Question Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Question Type
                </label>
                <select
                  name="question_type"
                  value={formData.question_type}
                  onChange={handleInputChange}
                  className="input-field"
                >
                  {questionTypes.map((type) => (
                    <option key={type} value={type}>
                      {type.replace("_", " ").toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>

              {/* Question */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Interview Question
                </label>
                <textarea
                  name="question"
                  value={formData.question}
                  onChange={handleInputChange}
                  rows="3"
                  className="input-field"
                  placeholder="Enter the interview question..."
                />
              </div>

              {/* Expected Areas */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Expected Areas (comma-separated)
                </label>
                <input
                  type="text"
                  name="expected_areas"
                  value={formData.expected_areas}
                  onChange={handleInputChange}
                  className="input-field"
                  placeholder="e.g., time complexity, edge cases, optimization"
                />
              </div>

              {/* User Response */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Response
                </label>
                <textarea
                  name="user_response"
                  value={formData.user_response}
                  onChange={handleInputChange}
                  rows="6"
                  className="input-field font-mono"
                  placeholder="Type or paste your answer here..."
                />
              </div>

              {/* Context */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Experience (years)
                  </label>
                  <input
                    type="number"
                    name="context.experience_years"
                    value={formData.context.experience_years}
                    onChange={handleInputChange}
                    className="input-field"
                    min="0"
                    max="20"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Role
                  </label>
                  <input
                    type="text"
                    name="context.target_role"
                    value={formData.context.target_role}
                    onChange={handleInputChange}
                    className="input-field"
                    placeholder="e.g., SDE, ML Engineer"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                onClick={handleSubmitQuestion}
                disabled={
                  !formData.question || !formData.user_response || loading
                }
                className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>Evaluating...</span>
                  </>
                ) : (
                  <>
                    <Send className="h-5 w-5" />
                    <span>Evaluate Response</span>
                  </>
                )}
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Problem Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Problem
                </label>
                <select
                  value={codeData.problem_id}
                  onChange={(e) =>
                    setCodeData((prev) => ({
                      ...prev,
                      problem_id: e.target.value,
                    }))
                  }
                  className="input-field"
                >
                  {popularProblems.map((problem) => (
                    <option key={problem.id} value={problem.id}>
                      {problem.title} ({problem.difficulty})
                    </option>
                  ))}
                </select>
              </div>

              {/* Code Input */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Your Solution
                  </label>
                  <button
                    onClick={() => copyToClipboard(codeData.code)}
                    className="text-sm text-gray-500 hover:text-gray-700 flex items-center space-x-1"
                  >
                    {copied ? (
                      <>
                        <Check className="h-4 w-4" />
                        <span>Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                </div>
                <textarea
                  value={codeData.code}
                  onChange={handleCodeChange}
                  rows="12"
                  className="input-field font-mono text-sm"
                  placeholder={`def twoSum(nums, target):\n    # Write your solution here\n    pass`}
                />
              </div>

              {/* Quick Tips */}
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-medium text-blue-800 mb-2 flex items-center">
                  <BookOpen className="h-4 w-4 mr-2" />
                  Quick Tips
                </h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>
                    • Solve the problem on LeetCode first, then paste your
                    solution
                  </li>
                  <li>• Include your entire function/class definition</li>
                  <li>• Make sure your code is properly indented</li>
                  <li>
                    • Our AI will analyze complexity, edge cases, and provide
                    optimizations
                  </li>
                </ul>
              </div>

              {/* Submit Button */}
              <button
                onClick={handleSubmitCode}
                disabled={!codeData.code || loading}
                className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>Analyzing Code...</span>
                  </>
                ) : (
                  <>
                    <Code className="h-5 w-5" />
                    <span>Analyze Code</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
