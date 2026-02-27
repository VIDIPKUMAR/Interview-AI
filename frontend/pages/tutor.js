import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { agentAPI } from "../utils/api";
import {
  BookOpen,
  Brain,
  PlayCircle,
  FileText,
  CheckCircle,
  AlertCircle,
  Loader2,
  Sparkles,
  Lightbulb,
  ChevronRight,
  Clock,
  BarChart,
  ThumbsUp,
  MessageCircle,
  Video,
  Code,
} from "lucide-react";
import ReactMarkdown from "react-markdown";

export default function Tutor() {
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [tutoring, setTutoring] = useState(null);
  const [activeTab, setActiveTab] = useState("learn");
  const [selectedTopic, setSelectedTopic] = useState("");
  const [customTopic, setCustomTopic] = useState("");
  const [difficulty, setDifficulty] = useState("intermediate");
  const [context, setContext] = useState({
    previous_topics: [],
    strengths: [],
    weaknesses: [],
  });

  const topics = [
    { id: "arrays", name: "Arrays & Strings", difficulty: "beginner" },
    { id: "linked-lists", name: "Linked Lists", difficulty: "beginner" },
    { id: "stacks-queues", name: "Stacks & Queues", difficulty: "beginner" },
    { id: "trees", name: "Trees & BST", difficulty: "intermediate" },
    { id: "graphs", name: "Graphs", difficulty: "intermediate" },
    {
      id: "dynamic-programming",
      name: "Dynamic Programming",
      difficulty: "advanced",
    },
    {
      id: "recursion",
      name: "Recursion & Backtracking",
      difficulty: "intermediate",
    },
    { id: "system-design", name: "System Design", difficulty: "advanced" },
    { id: "oop", name: "Object-Oriented Design", difficulty: "intermediate" },
    { id: "sorting", name: "Sorting Algorithms", difficulty: "beginner" },
  ];

  const difficulties = ["beginner", "intermediate", "advanced"];

  useEffect(() => {
    const savedUserId = localStorage.getItem("interviewai_user_id");
    if (savedUserId) {
      setUserId(savedUserId);
    }
  }, []);

  const handleTopicSelect = (topic) => {
    setSelectedTopic(topic);
    setCustomTopic("");
  };

  const handleCustomTopic = (e) => {
    setCustomTopic(e.target.value);
    setSelectedTopic("");
  };

  const handleAddPreviousTopic = () => {
    if (customTopic && !context.previous_topics.includes(customTopic)) {
      setContext((prev) => ({
        ...prev,
        previous_topics: [...prev.previous_topics, customTopic],
      }));
      setCustomTopic("");
    }
  };

  const handleAddStrength = () => {
    if (customTopic && !context.strengths.includes(customTopic)) {
      setContext((prev) => ({
        ...prev,
        strengths: [...prev.strengths, customTopic],
      }));
      setCustomTopic("");
    }
  };

  const handleAddWeakness = () => {
    if (customTopic && !context.weaknesses.includes(customTopic)) {
      setContext((prev) => ({
        ...prev,
        weaknesses: [...prev.weaknesses, customTopic],
      }));
      setCustomTopic("");
    }
  };

  const removeItem = (array, item, type) => {
    setContext((prev) => ({
      ...prev,
      [type]: prev[type].filter((i) => i !== item),
    }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const topicToUse = selectedTopic || customTopic || "Dynamic Programming";

      const result = await agentAPI.getTutoring({
        user_id: userId || "test_001",
        topic: topicToUse,
        difficulty: difficulty,
        context: context,
      });

      setTutoring(result);
      setActiveTab("lesson");
    } catch (error) {
      console.error("Error getting tutoring:", error);
      alert("Failed to get tutoring. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (diff) => {
    switch (diff) {
      case "beginner":
        return "text-green-600 bg-green-50";
      case "intermediate":
        return "text-yellow-600 bg-yellow-50";
      case "advanced":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const renderLesson = () => (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary to-secondary rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">{tutoring?.topic}</h2>
            <div className="flex items-center space-x-4">
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(
                  tutoring?.difficulty
                )}`}
              >
                {tutoring?.difficulty?.charAt(0).toUpperCase() +
                  tutoring?.difficulty?.slice(1)}
              </span>
              <span className="flex items-center">
                <Clock className="h-4 w-4 mr-1" />
                {tutoring?.estimated_completion_time?.total_minutes} minutes
              </span>
            </div>
          </div>
          <Sparkles className="h-12 w-12 opacity-50" />
        </div>
      </div>

      {/* Teaching Method */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-3 flex items-center">
          <Brain className="h-5 w-5 text-primary mr-2" />
          Teaching Method: {tutoring?.teaching_method?.replace(/_/g, " ")}
        </h3>
        <p className="text-gray-600">
          Personalized for your{" "}
          {tutoring?.teaching_method?.includes("visual")
            ? "visual"
            : "learning"}{" "}
          style
        </p>
      </div>

      {/* Learning Objectives */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Target className="h-5 w-5 text-primary mr-2" />
          Learning Objectives
        </h3>
        <ul className="space-y-3">
          {tutoring?.lesson?.learning_objectives?.map((obj, index) => (
            <li key={index} className="flex items-start space-x-3">
              <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
              <span className="text-gray-700">{obj}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Key Concepts */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Lightbulb className="h-5 w-5 text-yellow-500 mr-2" />
          Key Concepts
        </h3>
        <div className="space-y-4">
          {tutoring?.lesson?.key_concepts?.map((concept, index) => (
            <div key={index} className="border-l-4 border-primary pl-4">
              <h4 className="font-semibold text-gray-900 mb-2">
                {concept.concept}
              </h4>
              <p className="text-gray-700 mb-2">{concept.explanation}</p>
              {concept.example && (
                <div className="bg-gray-50 rounded p-3 mt-2">
                  <p className="text-sm font-medium text-gray-700 mb-1">
                    Example:
                  </p>
                  <p className="text-gray-600">{concept.example}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Real World Applications */}
      {tutoring?.lesson?.real_world_applications && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Code className="h-5 w-5 text-secondary mr-2" />
            Real World Applications
          </h3>
          <div className="grid gap-4">
            {tutoring.lesson.real_world_applications.map((app, index) => (
              <div key={index} className="bg-gray-50 rounded p-4">
                <h4 className="font-semibold text-gray-900 mb-2">
                  {app.scenario}
                </h4>
                <p className="text-gray-700 mb-2">{app.application}</p>
                <p className="text-sm text-gray-600">{app.relevance}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Common Interview Questions */}
      {tutoring?.lesson?.common_interview_questions && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <MessageCircle className="h-5 w-5 text-purple-500 mr-2" />
            Common Interview Questions
          </h3>
          <div className="space-y-4">
            {tutoring.lesson.common_interview_questions.map((q, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <p className="font-medium text-gray-900">{q.question}</p>
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(
                      q.difficulty
                    )}`}
                  >
                    {q.difficulty}
                  </span>
                </div>
                {q.expected_answer_elements && (
                  <div className="mt-2">
                    <p className="text-sm font-medium text-gray-700 mb-1">
                      Expected elements:
                    </p>
                    <ul className="list-disc list-inside text-sm text-gray-600">
                      {q.expected_answer_elements.map((element, i) => (
                        <li key={i}>{element}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Best Practices */}
      {tutoring?.lesson?.best_practices && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <ThumbsUp className="h-5 w-5 text-green-500 mr-2" />
            Best Practices
          </h3>
          <ul className="space-y-2">
            {tutoring.lesson.best_practices.map((practice, index) => (
              <li key={index} className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-1" />
                <span className="text-gray-700">{practice}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Common Pitfalls */}
      {tutoring?.lesson?.common_pitfalls && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
            Common Pitfalls to Avoid
          </h3>
          <div className="space-y-3">
            {tutoring.lesson.common_pitfalls.map((pitfall, index) => (
              <div key={index} className="bg-red-50 rounded p-3">
                <p className="font-medium text-red-800 mb-1">
                  {pitfall.pitfall}
                </p>
                <p className="text-sm text-red-700 mb-1">
                  Why: {pitfall.why_it_happens}
                </p>
                <p className="text-sm text-red-700">
                  Solution: {pitfall.how_to_avoid}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Practice Exercises */}
      {tutoring?.practice_exercises && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Code className="h-5 w-5 text-primary mr-2" />
            Practice Exercises
          </h3>
          <div className="space-y-4">
            {tutoring.practice_exercises.map((exercise, index) => (
              <div key={index} className="border rounded-lg overflow-hidden">
                <div className="bg-gray-50 px-4 py-3 border-b flex items-center justify-between">
                  <h4 className="font-semibold">Exercise {index + 1}</h4>
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(
                      exercise.difficulty
                    )}`}
                  >
                    {exercise.difficulty}
                  </span>
                </div>
                <div className="p-4">
                  <p className="text-gray-900 mb-3">
                    {exercise.problem_statement}
                  </p>

                  {exercise.hints && exercise.hints.length > 0 && (
                    <div className="mb-3">
                      <p className="text-sm font-medium text-gray-700 mb-1">
                        Hints:
                      </p>
                      <ul className="list-disc list-inside text-sm text-gray-600">
                        {exercise.hints.map((hint, i) => (
                          <li key={i}>{hint}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {exercise.solution_approach && (
                    <div className="bg-green-50 rounded p-3">
                      <p className="text-sm font-medium text-green-800 mb-1">
                        Approach:
                      </p>
                      <p className="text-sm text-green-700">
                        {exercise.solution_approach}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Summary */}
      {tutoring?.lesson?.summary && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-3">Key Takeaways</h3>
          <p className="text-gray-700 mb-4">{tutoring.lesson.summary}</p>
          <div className="flex flex-wrap gap-2">
            {tutoring.lesson.key_takeaways?.map((takeaway, index) => (
              <span
                key={index}
                className="bg-white px-3 py-1 rounded-full text-sm text-gray-700"
              >
                {takeaway}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Next Steps */}
      {tutoring?.next_steps && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Suggested Next Steps</h3>
          <div className="space-y-3">
            {tutoring.next_steps.map((step, index) => (
              <div key={index} className="flex items-start space-x-3">
                <ChevronRight className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">{step.topic}</p>
                  <p className="text-sm text-gray-600">{step.reason}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* New Session Button */}
      <button
        onClick={() => {
          setTutoring(null);
          setActiveTab("learn");
        }}
        className="w-full btn-primary"
      >
        Start New Tutoring Session
      </button>
    </div>
  );

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI Tutor Agent
          </h1>
          <p className="text-gray-600">
            Get personalized lessons tailored to your learning style
          </p>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          {activeTab === "lesson" && tutoring ? (
            renderLesson()
          ) : (
            <div className="space-y-8">
              {/* Topic Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Choose a Topic
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
                  {topics.map((topic) => (
                    <button
                      key={topic.id}
                      onClick={() => handleTopicSelect(topic.name)}
                      className={`p-3 rounded-lg border-2 text-left transition-all ${
                        selectedTopic === topic.name
                          ? "border-primary bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <div className="font-medium text-gray-900">
                        {topic.name}
                      </div>
                      <span
                        className={`text-xs px-2 py-1 rounded-full mt-1 inline-block ${getDifficultyColor(
                          topic.difficulty
                        )}`}
                      >
                        {topic.difficulty}
                      </span>
                    </button>
                  ))}
                </div>

                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={customTopic}
                    onChange={handleCustomTopic}
                    placeholder="Or type a custom topic..."
                    className="input-field flex-1"
                  />
                </div>
              </div>

              {/* Difficulty */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Difficulty Level
                </label>
                <div className="flex space-x-3">
                  {difficulties.map((level) => (
                    <button
                      key={level}
                      onClick={() => setDifficulty(level)}
                      className={`flex-1 p-3 rounded-lg border-2 capitalize transition-all ${
                        difficulty === level
                          ? "border-primary bg-blue-50 text-primary"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>

              {/* Context Builder */}
              <div className="space-y-4">
                <h3 className="font-medium text-gray-900">
                  Learning Context (Optional)
                </h3>

                {/* Previous Topics */}
                <div>
                  <label className="block text-sm text-gray-600 mb-2">
                    Topics you already know
                  </label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {context.previous_topics.map((topic, index) => (
                      <span
                        key={index}
                        className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center"
                      >
                        {topic}
                        <button
                          onClick={() =>
                            removeItem(
                              context.previous_topics,
                              topic,
                              "previous_topics"
                            )
                          }
                          className="ml-2 text-blue-600 hover:text-blue-800"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      placeholder="Add a topic you know..."
                      className="input-field flex-1"
                      value={customTopic}
                      onChange={handleCustomTopic}
                      onKeyPress={(e) =>
                        e.key === "Enter" && handleAddPreviousTopic()
                      }
                    />
                    <button
                      onClick={handleAddPreviousTopic}
                      className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
                    >
                      Add
                    </button>
                  </div>
                </div>

                {/* Strengths */}
                <div>
                  <label className="block text-sm text-gray-600 mb-2">
                    Your strengths in this topic
                  </label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {context.strengths.map((strength, index) => (
                      <span
                        key={index}
                        className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm flex items-center"
                      >
                        {strength}
                        <button
                          onClick={() =>
                            removeItem(context.strengths, strength, "strengths")
                          }
                          className="ml-2 text-green-600 hover:text-green-800"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      placeholder="Add a strength..."
                      className="input-field flex-1"
                      value={customTopic}
                      onChange={handleCustomTopic}
                      onKeyPress={(e) =>
                        e.key === "Enter" && handleAddStrength()
                      }
                    />
                    <button
                      onClick={handleAddStrength}
                      className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
                    >
                      Add
                    </button>
                  </div>
                </div>

                {/* Weaknesses */}
                <div>
                  <label className="block text-sm text-gray-600 mb-2">
                    Areas you struggle with
                  </label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {context.weaknesses.map((weakness, index) => (
                      <span
                        key={index}
                        className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm flex items-center"
                      >
                        {weakness}
                        <button
                          onClick={() =>
                            removeItem(
                              context.weaknesses,
                              weakness,
                              "weaknesses"
                            )
                          }
                          className="ml-2 text-red-600 hover:text-red-800"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      placeholder="Add a weakness..."
                      className="input-field flex-1"
                      value={customTopic}
                      onChange={handleCustomTopic}
                      onKeyPress={(e) =>
                        e.key === "Enter" && handleAddWeakness()
                      }
                    />
                    <button
                      onClick={handleAddWeakness}
                      className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
                    >
                      Add
                    </button>
                  </div>
                </div>
              </div>

              {/* Start Button */}
              <button
                onClick={handleSubmit}
                disabled={(!selectedTopic && !customTopic) || loading}
                className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>Preparing Your Lesson...</span>
                  </>
                ) : (
                  <>
                    <PlayCircle className="h-5 w-5" />
                    <span>Start Learning</span>
                  </>
                )}
              </button>

              {/* Tips */}
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-medium text-blue-800 mb-2 flex items-center">
                  <Lightbulb className="h-4 w-4 mr-2" />
                  Pro Tips
                </h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>
                    • The more context you provide, the more personalized your
                    lesson
                  </li>
                  <li>• Tell us your strengths so we can build on them</li>
                  <li>• Be specific about your weaknesses for targeted help</li>
                  <li>• Lessons adapt to your preferred learning style</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
