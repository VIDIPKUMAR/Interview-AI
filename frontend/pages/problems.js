import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { agentAPI } from "../utils/api";
import {
  Code,
  Search,
  Filter,
  Clock,
  ChevronRight,
  Star,
  CheckCircle,
  AlertCircle,
  Loader2,
  BookOpen,
  TrendingUp,
  Award,
  Building2,
  ExternalLink,
  ThumbsUp,
  Zap,
  Brain,
  Copy,
  Check,
} from "lucide-react";

export default function Problems() {
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [problems, setProblems] = useState([]);
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedDifficulty, setSelectedDifficulty] = useState("all");
  const [selectedTopic, setSelectedTopic] = useState("all");
  const [selectedCompany, setSelectedCompany] = useState("all");
  const [code, setCode] = useState("");
  const [evaluation, setEvaluation] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [copied, setCopied] = useState(false);

  const difficulties = ["all", "Easy", "Medium", "Hard"];
  const topics = [
    "all",
    "arrays",
    "hash-table",
    "linked-list",
    "stack",
    "strings",
    "dynamic-programming",
    "graphs",
    "trees",
    "dfs",
    "bfs",
    "sorting",
    "two-pointers",
    "greedy",
    "recursion",
    "matrix",
    "design",
  ];

  // Sample problems database (in production, this would come from your API)
  const problemsDatabase = [
    {
      id: "two-sum",
      title: "Two Sum",
      difficulty: "Easy",
      topics: ["arrays", "hash-table"],
      companies: ["Google", "Amazon", "Microsoft", "Meta", "Apple"],
      url: "https://leetcode.com/problems/two-sum",
      description:
        "Given an array of integers nums and an integer target, return indices of the two numbers that add up to target.",
      acceptance: "47.5%",
      frequency: "🔥🔥🔥",
      solutionApproaches: [
        {
          name: "Brute Force",
          complexity: "O(n²)",
          code: "for i in range(len(nums)):\n    for j in range(i+1, len(nums)):\n        if nums[i] + nums[j] == target:\n            return [i, j]",
        },
        {
          name: "Hash Map",
          complexity: "O(n)",
          code: "seen = {}\nfor i, num in enumerate(nums):\n    complement = target - num\n    if complement in seen:\n        return [seen[complement], i]\n    seen[num] = i",
        },
      ],
    },
    {
      id: "valid-parentheses",
      title: "Valid Parentheses",
      difficulty: "Easy",
      topics: ["stack", "strings"],
      companies: ["Amazon", "Microsoft", "Google", "Facebook"],
      url: "https://leetcode.com/problems/valid-parentheses",
      description:
        'Given a string s containing just the characters "(", ")", "{", "}", "[" and "]", determine if the input string is valid.',
      acceptance: "40.2%",
      frequency: "🔥🔥🔥",
      solutionApproaches: [
        {
          name: "Stack",
          complexity: "O(n)",
          code: 'stack = []\nmapping = {")": "(", "}": "{", "]": "["}\nfor char in s:\n    if char in mapping:\n        if not stack or stack[-1] != mapping[char]:\n            return False\n        stack.pop()\n    else:\n        stack.append(char)\nreturn not stack',
        },
      ],
    },
    {
      id: "merge-two-sorted-lists",
      title: "Merge Two Sorted Lists",
      difficulty: "Easy",
      topics: ["linked-list", "recursion"],
      companies: ["Microsoft", "Amazon", "Google"],
      url: "https://leetcode.com/problems/merge-two-sorted-lists",
      description:
        "Merge two sorted linked lists and return it as a sorted list.",
      acceptance: "58.1%",
      frequency: "🔥🔥",
      solutionApproaches: [
        {
          name: "Iterative",
          complexity: "O(n+m)",
          code: "dummy = ListNode(0)\ncurr = dummy\nwhile l1 and l2:\n    if l1.val < l2.val:\n        curr.next = l1\n        l1 = l1.next\n    else:\n        curr.next = l2\n        l2 = l2.next\n    curr = curr.next\ncurr.next = l1 or l2\nreturn dummy.next",
        },
      ],
    },
    {
      id: "maximum-subarray",
      title: "Maximum Subarray",
      difficulty: "Medium",
      topics: ["arrays", "dynamic-programming"],
      companies: ["Google", "Amazon", "Microsoft", "LinkedIn"],
      url: "https://leetcode.com/problems/maximum-subarray",
      description:
        "Find the contiguous subarray with the largest sum and return its sum.",
      acceptance: "49.2%",
      frequency: "🔥🔥🔥",
      solutionApproaches: [
        {
          name: "Kadane's Algorithm",
          complexity: "O(n)",
          code: "max_sum = nums[0]\ncurr_sum = nums[0]\nfor num in nums[1:]:\n    curr_sum = max(num, curr_sum + num)\n    max_sum = max(max_sum, curr_sum)\nreturn max_sum",
        },
      ],
    },
    {
      id: "number-of-islands",
      title: "Number of Islands",
      difficulty: "Medium",
      topics: ["graphs", "dfs", "bfs", "matrix"],
      companies: ["Google", "Amazon", "Facebook", "Microsoft"],
      url: "https://leetcode.com/problems/number-of-islands",
      description:
        "Given an m x n 2D binary grid, count the number of islands.",
      acceptance: "53.5%",
      frequency: "🔥🔥🔥",
      solutionApproaches: [
        {
          name: "DFS",
          complexity: "O(m×n)",
          code: 'def dfs(grid, i, j):\n    if i<0 or i>=len(grid) or j<0 or j>=len(grid[0]) or grid[i][j]!="1":\n        return\n    grid[i][j] = "0"\n    dfs(grid, i+1, j)\n    dfs(grid, i-1, j)\n    dfs(grid, i, j+1)\n    dfs(grid, i, j-1)\n\ncount = 0\nfor i in range(len(grid)):\n    for j in range(len(grid[0])):\n        if grid[i][j] == "1":\n            dfs(grid, i, j)\n            count += 1\nreturn count',
        },
      ],
    },
    {
      id: "trapping-rain-water",
      title: "Trapping Rain Water",
      difficulty: "Hard",
      topics: ["arrays", "two-pointers", "stack"],
      companies: ["Google", "Amazon", "Microsoft", "Flipkart"],
      url: "https://leetcode.com/problems/trapping-rain-water",
      description:
        "Given n non-negative integers representing an elevation map, compute how much water it can trap after raining.",
      acceptance: "56.5%",
      frequency: "🔥🔥🔥",
      solutionApproaches: [
        {
          name: "Two Pointers",
          complexity: "O(n)",
          code: "left, right = 0, len(height)-1\nleft_max = right_max = water = 0\nwhile left < right:\n    if height[left] < height[right]:\n        if height[left] >= left_max:\n            left_max = height[left]\n        else:\n            water += left_max - height[left]\n        left += 1\n    else:\n        if height[right] >= right_max:\n            right_max = height[right]\n        else:\n            water += right_max - height[right]\n        right -= 1\nreturn water",
        },
      ],
    },
  ];

  useEffect(() => {
    const savedUserId = localStorage.getItem("interviewai_user_id");
    if (savedUserId) {
      setUserId(savedUserId);
    }
    setProblems(problemsDatabase);
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      const data = await agentAPI.listCompanies();
      setCompanies(data.companies || []);
    } catch (error) {
      console.error("Error fetching companies:", error);
    }
  };

  const handleProblemSelect = (problem) => {
    setSelectedProblem(problem);
    setCode("");
    setEvaluation(null);
  };

  const handleSubmitCode = async () => {
    if (!code.trim()) return;

    setLoading(true);
    try {
      const result = await agentAPI.submitCode({
        user_id: userId || "test_001",
        problem_id: selectedProblem.id,
        code: code,
        platform: "leetcode",
      });
      setEvaluation(result);
    } catch (error) {
      console.error("Error submitting code:", error);
      alert("Failed to evaluate code. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const filteredProblems = problems.filter((problem) => {
    const matchesSearch = problem.title
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    const matchesDifficulty =
      selectedDifficulty === "all" || problem.difficulty === selectedDifficulty;
    const matchesTopic =
      selectedTopic === "all" || problem.topics.includes(selectedTopic);
    const matchesCompany =
      selectedCompany === "all" || problem.companies.includes(selectedCompany);
    return matchesSearch && matchesDifficulty && matchesTopic && matchesCompany;
  });

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case "Easy":
        return "text-green-600 bg-green-50 border-green-200";
      case "Medium":
        return "text-yellow-600 bg-yellow-50 border-yellow-200";
      case "Hard":
        return "text-red-600 bg-red-50 border-red-200";
      default:
        return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Problem Solving Practice
          </h1>
          <p className="text-gray-600">
            Solve problems, get AI-powered feedback, and track your progress
          </p>
        </div>

        {/* Main Grid */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Problem List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-20">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <BookOpen className="h-5 w-5 text-primary mr-2" />
                Problems ({filteredProblems.length})
              </h2>

              {/* Search */}
              <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search problems..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="input-field pl-10"
                />
              </div>

              {/* Filters */}
              <div className="space-y-3 mb-4">
                <select
                  value={selectedDifficulty}
                  onChange={(e) => setSelectedDifficulty(e.target.value)}
                  className="input-field text-sm"
                >
                  {difficulties.map((d) => (
                    <option key={d} value={d}>
                      Difficulty: {d === "all" ? "All" : d}
                    </option>
                  ))}
                </select>

                <select
                  value={selectedTopic}
                  onChange={(e) => setSelectedTopic(e.target.value)}
                  className="input-field text-sm"
                >
                  {topics.map((t) => (
                    <option key={t} value={t}>
                      Topic: {t === "all" ? "All" : t}
                    </option>
                  ))}
                </select>

                <select
                  value={selectedCompany}
                  onChange={(e) => setSelectedCompany(e.target.value)}
                  className="input-field text-sm"
                >
                  <option value="all">All Companies</option>
                  {companies.slice(0, 10).map((c) => (
                    <option key={c.name} value={c.name}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Problem List */}
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {filteredProblems.map((problem) => (
                  <button
                    key={problem.id}
                    onClick={() => handleProblemSelect(problem)}
                    className={`w-full text-left p-3 rounded-lg border-2 transition-all ${
                      selectedProblem?.id === problem.id
                        ? "border-primary bg-blue-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="font-semibold text-gray-900">
                        {problem.title}
                      </h3>
                      <span
                        className={`text-xs px-2 py-1 rounded-full ${getDifficultyColor(
                          problem.difficulty
                        )}`}
                      >
                        {problem.difficulty}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>{problem.acceptance}</span>
                      <span>{problem.frequency}</span>
                    </div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {problem.companies.slice(0, 3).map((company) => (
                        <span
                          key={company}
                          className="text-xs bg-gray-100 px-2 py-0.5 rounded"
                        >
                          {company}
                        </span>
                      ))}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Problem Details & Code Editor */}
          <div className="lg:col-span-2">
            {selectedProblem ? (
              <div className="space-y-6">
                {/* Problem Header */}
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 mb-2">
                        {selectedProblem.title}
                      </h2>
                      <div className="flex items-center space-x-3">
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(
                            selectedProblem.difficulty
                          )}`}
                        >
                          {selectedProblem.difficulty}
                        </span>
                        <span className="text-sm text-gray-500">
                          Acceptance: {selectedProblem.acceptance}
                        </span>
                      </div>
                    </div>
                    <a
                      href={selectedProblem.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-1 text-primary hover:text-blue-700"
                    >
                      <span>Solve on LeetCode</span>
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </div>

                  <p className="text-gray-700 mb-4">
                    {selectedProblem.description}
                  </p>

                  {/* Topics */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {selectedProblem.topics.map((topic) => (
                      <span
                        key={topic}
                        className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>

                  {/* Companies */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">
                      Asked by:
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedProblem.companies.map((company) => (
                        <span
                          key={company}
                          className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm flex items-center"
                        >
                          <Building2 className="h-3 w-3 mr-1" />
                          {company}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Code Editor */}
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">Your Solution</h3>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => copyToClipboard(code)}
                        className="p-2 hover:bg-gray-100 rounded-lg"
                      >
                        {copied ? (
                          <Check className="h-4 w-4 text-green-500" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  <textarea
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    rows="12"
                    className="input-field font-mono text-sm"
                    placeholder={`def ${selectedProblem.id.replace("-", "_")}(${
                      selectedProblem.id === "two-sum" ? "nums, target" : "..."
                    }):\n    # Write your solution here\n    pass`}
                  />

                  <button
                    onClick={handleSubmitCode}
                    disabled={!code.trim() || loading}
                    className="mt-4 w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="h-5 w-5 animate-spin" />
                        <span>Evaluating...</span>
                      </>
                    ) : (
                      <>
                        <Zap className="h-5 w-5" />
                        <span>Submit for AI Evaluation</span>
                      </>
                    )}
                  </button>
                </div>

                {/* Evaluation Results */}
                {evaluation && (
                  <div className="bg-white rounded-xl shadow-lg p-6">
                    <h3 className="text-lg font-semibold mb-4">
                      AI Evaluation
                    </h3>

                    {/* Show raw evaluation for debugging - remove after fixing */}
                    <pre className="bg-gray-100 p-4 rounded-lg text-xs mb-4 overflow-auto">
                      {JSON.stringify(evaluation, null, 2)}
                    </pre>

                    {/* Complexity Analysis */}
                    {evaluation.analysis && evaluation.analysis.complexity && (
                      <div className="grid grid-cols-2 gap-4 mb-6">
                        <div className="bg-gray-50 rounded-lg p-4">
                          <div className="text-sm text-gray-600 mb-1">
                            Time Complexity
                          </div>
                          <div className="text-lg font-bold text-gray-900">
                            {typeof evaluation.analysis.complexity === "object"
                              ? evaluation.analysis.complexity.time || "O(n)"
                              : evaluation.analysis.complexity || "O(n)"}
                          </div>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-4">
                          <div className="text-sm text-gray-600 mb-1">
                            Space Complexity
                          </div>
                          <div className="text-lg font-bold text-gray-900">
                            {typeof evaluation.analysis.complexity === "object"
                              ? evaluation.analysis.complexity.space || "O(1)"
                              : "O(1)"}
                          </div>
                        </div>
                      </div>
                    )}
                    {/* Suggestions */}
                    {evaluation.analysis?.suggestions?.length > 0 && (
                      <div className="mb-6">
                        <h4 className="font-medium text-gray-900 mb-2">
                          Suggestions
                        </h4>
                        <ul className="space-y-2">
                          {evaluation.analysis.suggestions.map(
                            (suggestion, i) => (
                              <li
                                key={i}
                                className="flex items-start space-x-2 text-sm"
                              >
                                <span className="text-blue-500">•</span>
                                <span>{suggestion}</span>
                              </li>
                            )
                          )}
                        </ul>
                      </div>
                    )}

                    {/* Optimized Code */}
                    {evaluation.optimized_code && (
                      <div className="mt-4">
                        <h4 className="font-medium text-gray-900 mb-2">
                          Optimized Solution
                        </h4>
                        <pre className="bg-gray-900 text-white p-4 rounded-lg text-sm overflow-auto">
                          {evaluation.optimized_code}
                        </pre>
                      </div>
                    )}

                    {/* Feedback */}
                    {evaluation.feedback && (
                      <div className="space-y-4">
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">
                            Strengths
                          </h4>
                          <ul className="space-y-1">
                            {evaluation.feedback.strengths_highlighted?.map(
                              (s, i) => (
                                <li
                                  key={i}
                                  className="flex items-start space-x-2 text-sm"
                                >
                                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                                  <span>{s}</span>
                                </li>
                              )
                            )}
                          </ul>
                        </div>

                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">
                            Improvements
                          </h4>
                          <ul className="space-y-1">
                            {evaluation.feedback.improvement_areas?.map(
                              (area, i) => (
                                <li
                                  key={i}
                                  className="flex items-start space-x-2 text-sm"
                                >
                                  <AlertCircle className="h-4 w-4 text-orange-500 flex-shrink-0 mt-0.5" />
                                  <span>{area.suggestion || area.area}</span>
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      </div>
                    )}

                    {/* Next Steps */}
                    {evaluation.next_recommendation && (
                      <div className="mt-6 pt-4 border-t">
                        <h4 className="font-medium text-gray-900 mb-2">
                          Recommended Next
                        </h4>
                        <p className="text-sm text-gray-600">
                          {evaluation.next_recommendation.recommendation
                            ?.problem?.title || "Try another problem"}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-lg p-12 text-center">
                <Code className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-700 mb-2">
                  Select a Problem
                </h3>
                <p className="text-gray-500">
                  Choose a problem from the list to start coding
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
