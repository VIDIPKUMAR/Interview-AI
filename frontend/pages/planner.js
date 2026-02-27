import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Layout from "../components/Layout";
import { agentAPI } from "../utils/api";
import {
  Calendar,
  Target,
  Clock,
  TrendingUp,
  ChevronRight,
  Sparkles,
  BookOpen,
  CheckCircle,
  AlertCircle,
} from "lucide-react";

export default function Planner() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [formData, setFormData] = useState({
    name: "",
    target_role: "Software Engineer",
    target_companies: [],
    experience: "3",
    daily_practice_minutes: 90,
    learning_style: "visual",
    timeline_weeks: 8,
  });

  const experienceLevels = ["0-2 years", "3-5 years", "5-8 years", "8+ years"];
  const learningStyles = ["visual", "auditory", "reading", "kinesthetic"];
  const roles = [
    "Software Engineer",
    "Senior Software Engineer",
    "SDE Intern",
    "ML Engineer",
    "Data Scientist",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "DevOps Engineer",
    "System Design Engineer",
  ];

  useEffect(() => {
    // Fetch list of companies
    agentAPI
      .listCompanies()
      .then((data) => setCompanies(data.companies || []))
      .catch(console.error);
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCompanyToggle = (company) => {
    setFormData((prev) => ({
      ...prev,
      target_companies: prev.target_companies.includes(company)
        ? prev.target_companies.filter((c) => c !== company)
        : [...prev.target_companies, company],
    }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      // First, create learning plan
      const planResult = await agentAPI.createPlan({
        name: formData.name,
        target_role: formData.target_role,
        target_companies: formData.target_companies,
        experience: formData.experience,
        daily_practice_minutes: formData.daily_practice_minutes,
        learning_style: formData.learning_style,
        timeline_weeks: formData.timeline_weeks,
      });

      // Log the full response to see its structure
      console.log("Full API Response:", planResult);

      // Check if response has user_id directly or nested
      if (planResult.user_id) {
        localStorage.setItem("interviewai_user_id", planResult.user_id);
      }
      // If user_id is nested inside another object
      else if (planResult.data?.user_id) {
        localStorage.setItem("interviewai_user_id", planResult.data.user_id);
      }
      // If user_id is in the learning_plan object
      else if (planResult.learning_plan?.user_id) {
        localStorage.setItem(
          "interviewai_user_id",
          planResult.learning_plan.user_id
        );
      }

      setPlan(planResult);
      setStep(3);
    } catch (error) {
      console.error("Error creating plan:", error);
      alert("Failed to create learning plan. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Name
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            className="input-field"
            placeholder="John Doe"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Role
          </label>
          <select
            name="target_role"
            value={formData.target_role}
            onChange={handleInputChange}
            className="input-field"
          >
            {roles.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Experience Level
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {experienceLevels.map((level) => (
            <button
              key={level}
              onClick={() =>
                setFormData((prev) => ({ ...prev, experience: level }))
              }
              className={`p-3 rounded-lg border-2 transition-all ${
                formData.experience === level
                  ? "border-primary bg-blue-50 text-primary"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              {level}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Learning Style
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {learningStyles.map((style) => (
            <button
              key={style}
              onClick={() =>
                setFormData((prev) => ({ ...prev, learning_style: style }))
              }
              className={`p-3 rounded-lg border-2 capitalize transition-all ${
                formData.learning_style === style
                  ? "border-primary bg-blue-50 text-primary"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              {style}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Daily Practice (minutes)
          </label>
          <input
            type="range"
            name="daily_practice_minutes"
            min="30"
            max="180"
            step="15"
            value={formData.daily_practice_minutes}
            onChange={handleInputChange}
            className="w-full"
          />
          <div className="text-center mt-2 text-lg font-semibold text-primary">
            {formData.daily_practice_minutes} minutes
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Timeline (weeks)
          </label>
          <input
            type="range"
            name="timeline_weeks"
            min="4"
            max="16"
            step="1"
            value={formData.timeline_weeks}
            onChange={handleInputChange}
            className="w-full"
          />
          <div className="text-center mt-2 text-lg font-semibold text-primary">
            {formData.timeline_weeks} weeks
          </div>
        </div>
      </div>

      <button
        onClick={() => setStep(2)}
        disabled={
          !formData.name ||
          !formData.target_role ||
          !formData.experience ||
          !formData.learning_style
        }
        className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Next: Select Companies
      </button>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Select Target Companies</h3>
        <p className="text-gray-600 mb-4">
          Choose the companies you're preparing for. We have data for{" "}
          {companies.length} companies!
        </p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-h-96 overflow-y-auto p-2">
          {companies.map((company) => (
            <button
              key={company.name}
              onClick={() => handleCompanyToggle(company.name)}
              className={`p-3 rounded-lg border-2 text-left transition-all ${
                formData.target_companies.includes(company.name)
                  ? "border-primary bg-blue-50 text-primary"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              <div className="font-medium">{company.name}</div>
              <div className="text-xs text-gray-500 mt-1">
                {company.industry} • {company.problem_count} problems
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="flex space-x-4">
        <button
          onClick={() => setStep(1)}
          className="flex-1 px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Back
        </button>
        <button
          onClick={handleSubmit}
          disabled={formData.target_companies.length === 0 || loading}
          className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Creating Plan..." : "Generate My Plan"}
        </button>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-8">
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
        <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Plan Created Successfully!
        </h2>
        <p className="text-gray-600">
          Your personalized 8-week learning plan is ready
        </p>
      </div>

      {plan && (
        <>
          {/* Overview Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-4">
              <Clock className="h-6 w-6 text-primary mb-2" />
              <div className="text-2xl font-bold">
                {plan.estimated_preparation_time?.total_hours || 60}h
              </div>
              <div className="text-sm text-gray-600">Total Hours</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <Calendar className="h-6 w-6 text-secondary mb-2" />
              <div className="text-2xl font-bold">
                {plan.learning_plan?.total_duration_weeks || 8}
              </div>
              <div className="text-sm text-gray-600">Weeks</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <Target className="h-6 w-6 text-purple-600 mb-2" />
              <div className="text-2xl font-bold">
                {plan.learning_plan?.phases?.length || 4}
              </div>
              <div className="text-sm text-gray-600">Learning Phases</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <TrendingUp className="h-6 w-6 text-orange-600 mb-2" />
              <div className="text-2xl font-bold">
                {plan.estimated_preparation_time?.estimated_completion_date ||
                  "2024-04-15"}
              </div>
              <div className="text-sm text-gray-600">Est. Completion</div>
            </div>
          </div>

          {/* Learning Phases */}
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Your Learning Journey</h3>
            {plan.learning_plan?.phases?.map((phase, index) => (
              <div
                key={index}
                className="bg-white rounded-lg shadow-lg overflow-hidden"
              >
                <div className="bg-gradient-to-r from-primary to-secondary text-white px-6 py-3">
                  <h4 className="font-semibold">
                    Phase {index + 1}: {phase.phase_name}
                  </h4>
                  <p className="text-sm opacity-90">
                    Duration: {phase.duration_weeks} weeks
                  </p>
                </div>
                <div className="p-6">
                  <div className="mb-4">
                    <h5 className="font-medium text-gray-700 mb-2">
                      Focus Areas:
                    </h5>
                    <div className="flex flex-wrap gap-2">
                      {phase.focus_areas?.map((area, i) => (
                        <span
                          key={i}
                          className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm"
                        >
                          {area}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="mb-4">
                    <h5 className="font-medium text-gray-700 mb-2">
                      Learning Objectives:
                    </h5>
                    <ul className="list-disc list-inside space-y-1">
                      {phase.learning_objectives?.map((obj, i) => (
                        <li key={i} className="text-gray-600 text-sm">
                          {obj}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h5 className="font-medium text-gray-700 mb-2">
                      Resources:
                    </h5>
                    <div className="flex flex-wrap gap-2">
                      {phase.resources?.map((resource, i) => (
                        <span
                          key={i}
                          className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm flex items-center"
                        >
                          <BookOpen className="h-3 w-3 mr-1" />
                          {resource}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Milestones */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold mb-4">Key Milestones</h3>
            <div className="space-y-4">
              {plan.milestones?.map((milestone, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white font-semibold">
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-medium">{milestone.description}</p>
                    <p className="text-sm text-gray-600">
                      Week {milestone.week}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button
              onClick={() => router.push("/scheduler")}
              className="flex-1 btn-primary"
            >
              Create Schedule
            </button>
            <button
              onClick={() => router.push("/problems")}
              className="flex-1 bg-secondary text-white px-6 py-2 rounded-lg hover:bg-green-600 transition-colors"
            >
              Start Practicing
            </button>
          </div>
        </>
      )}
    </div>
  );
  console.log("Form state:", {
    name: formData.name,
    role: formData.target_role,
    experience: formData.experience,
    style: formData.learning_style,
    buttonEnabled: !(
      !formData.name ||
      !formData.target_role ||
      !formData.experience ||
      !formData.learning_style
    ),
  });

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {step === 1 && "Create Your Learning Plan"}
            {step === 2 && "Select Target Companies"}
            {step === 3 && "Your Personalized Plan"}
          </h1>
          <p className="text-gray-600">
            {step === 1 && "Tell us about yourself to get started"}
            {step === 2 && "Choose the companies you want to target"}
            {step === 3 && "Here's your customized 8-week preparation plan"}
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex justify-between mb-8">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex-1 flex items-center">
              <div
                className={`flex-1 h-1 ${
                  i <= step ? "bg-primary" : "bg-gray-200"
                }`}
              />
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  i <= step
                    ? "bg-primary text-white"
                    : "bg-gray-200 text-gray-600"
                }`}
              >
                {i}
              </div>
              <div
                className={`flex-1 h-1 ${
                  i < step ? "bg-primary" : "bg-gray-200"
                }`}
              />
            </div>
          ))}
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
        </div>
      </div>
    </Layout>
  );
}
