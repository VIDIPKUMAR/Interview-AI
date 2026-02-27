import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { agentAPI } from "../utils/api";
import {
  User,
  Mail,
  Briefcase,
  Calendar,
  Target,
  Award,
  Clock,
  TrendingUp,
  BarChart3,
  BookOpen,
  Building2,
  Settings,
  Edit2,
  Save,
  X,
  Loader2,
  CheckCircle,
  AlertCircle,
  Star,
  Code,
  LogOut,
  RefreshCw,
} from "lucide-react";

export default function Profile() {
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [progress, setProgress] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    current_role: "",
    experience_years: 3,
    target_role: "",
    target_companies: [],
    timeline_weeks: 8,
    daily_practice_minutes: 90,
    learning_style: "visual",
    difficulty_preference: "adaptive",
  });

  const experienceLevels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15];
  const learningStyles = ["visual", "auditory", "reading", "kinesthetic"];
  const difficultyPreferences = ["adaptive", "easy", "medium", "hard"];
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
    "Product Manager",
    "Tech Lead",
  ];

  useEffect(() => {
    const savedUserId = localStorage.getItem("interviewai_user_id");
    if (savedUserId) {
      setUserId(savedUserId);
      fetchUserProfile(savedUserId);
      fetchUserProgress(savedUserId);
    }
    fetchCompanies();
  }, []);

  const fetchUserProfile = async (uid) => {
    setLoading(true);
    try {
      // In production, you'd have a dedicated endpoint
      // For now, create a mock profile from localStorage
      const savedName =
        localStorage.getItem("interviewai_user_name") || "John Doe";
      const savedEmail =
        localStorage.getItem("interviewai_user_email") || "john@example.com";
      const savedTargetCompanies = JSON.parse(
        localStorage.getItem("interviewai_target_companies") ||
          '["Google", "Microsoft"]'
      );

      const profile = {
        user_id: uid,
        name: savedName,
        email: savedEmail,
        current_role: "Software Engineer",
        experience_years: 5,
        member_since: "2024-01-15",
        last_active: new Date().toISOString(),
        interview_goal: {
          target_role: "Senior Software Engineer",
          target_companies: savedTargetCompanies,
          timeline_weeks: 8,
        },
        preferences: {
          learning_style: "visual",
          daily_practice_minutes: 90,
          difficulty_preference: "adaptive",
        },
      };

      setUserProfile(profile);
      setFormData({
        name: profile.name,
        email: profile.email,
        current_role: profile.current_role,
        experience_years: profile.experience_years,
        target_role: profile.interview_goal.target_role,
        target_companies: profile.interview_goal.target_companies,
        timeline_weeks: profile.interview_goal.timeline_weeks,
        daily_practice_minutes: profile.preferences.daily_practice_minutes,
        learning_style: profile.preferences.learning_style,
        difficulty_preference: profile.preferences.difficulty_preference,
      });
    } catch (error) {
      console.error("Error fetching profile:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserProgress = async (uid) => {
    try {
      const result = await agentAPI.getUserProgress(uid);
      setProgress(result);
    } catch (error) {
      console.error("Error fetching progress:", error);
    }
  };

  const fetchCompanies = async () => {
    try {
      const data = await agentAPI.listCompanies();
      setCompanies(data.companies || []);
    } catch (error) {
      console.error("Error fetching companies:", error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCompanyToggle = (companyName) => {
    setFormData((prev) => ({
      ...prev,
      target_companies: prev.target_companies.includes(companyName)
        ? prev.target_companies.filter((c) => c !== companyName)
        : [...prev.target_companies, companyName],
    }));
  };

  const handleSaveProfile = async () => {
    setSaving(true);
    try {
      // Save to localStorage (in production, this would be an API call)
      localStorage.setItem("interviewai_user_name", formData.name);
      localStorage.setItem("interviewai_user_email", formData.email);
      localStorage.setItem(
        "interviewai_target_companies",
        JSON.stringify(formData.target_companies)
      );

      // Update user profile
      setUserProfile((prev) => ({
        ...prev,
        name: formData.name,
        email: formData.email,
        current_role: formData.current_role,
        experience_years: formData.experience_years,
        interview_goal: {
          ...prev.interview_goal,
          target_role: formData.target_role,
          target_companies: formData.target_companies,
          timeline_weeks: formData.timeline_weeks,
        },
        preferences: {
          learning_style: formData.learning_style,
          daily_practice_minutes: formData.daily_practice_minutes,
          difficulty_preference: formData.difficulty_preference,
        },
      }));

      setEditMode(false);
      alert("Profile updated successfully!");
    } catch (error) {
      console.error("Error saving profile:", error);
      alert("Failed to save profile. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    if (confirm("Are you sure you want to logout?")) {
      localStorage.removeItem("interviewai_user_id");
      localStorage.removeItem("interviewai_user_name");
      localStorage.removeItem("interviewai_user_email");
      localStorage.removeItem("interviewai_target_companies");
      window.location.href = "/";
    }
  };

  const renderProfileView = () => (
    <div className="space-y-6">
      {/* Profile Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-4">
          <div className="w-20 h-20 bg-gradient-to-r from-primary to-secondary rounded-full flex items-center justify-center text-white text-3xl font-bold">
            {userProfile.name.charAt(0)}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {userProfile.name}
            </h2>
            <p className="text-gray-600">{userProfile.current_role}</p>
            <div className="flex items-center space-x-4 mt-2">
              <span className="flex items-center text-sm text-gray-500">
                <Mail className="h-4 w-4 mr-1" />
                {userProfile.email}
              </span>
              <span className="flex items-center text-sm text-gray-500">
                <Calendar className="h-4 w-4 mr-1" />
                Member since{" "}
                {new Date(userProfile.member_since).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>
        <button
          onClick={() => setEditMode(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          <Edit2 className="h-4 w-4" />
          <span>Edit Profile</span>
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <Briefcase className="h-5 w-5 text-primary mb-2" />
          <div className="text-2xl font-bold">
            {userProfile.experience_years}+
          </div>
          <div className="text-sm text-gray-600">Years Experience</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <Target className="h-5 w-5 text-secondary mb-2" />
          <div className="text-2xl font-bold">
            {userProfile.interview_goal.timeline_weeks}
          </div>
          <div className="text-sm text-gray-600">Weeks to Prepare</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <Clock className="h-5 w-5 text-purple-600 mb-2" />
          <div className="text-2xl font-bold">
            {userProfile.preferences.daily_practice_minutes}
          </div>
          <div className="text-sm text-gray-600">Daily Minutes</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <BookOpen className="h-5 w-5 text-orange-600 mb-2" />
          <div className="text-2xl font-bold capitalize">
            {userProfile.preferences.learning_style}
          </div>
          <div className="text-sm text-gray-600">Learning Style</div>
        </div>
      </div>

      {/* Target Companies */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Building2 className="h-5 w-5 text-primary mr-2" />
          Target Companies
        </h3>
        <div className="flex flex-wrap gap-2">
          {userProfile.interview_goal.target_companies.map((company) => (
            <span
              key={company}
              className="bg-blue-100 text-blue-800 px-4 py-2 rounded-lg"
            >
              {company}
            </span>
          ))}
        </div>
      </div>

      {/* Progress Overview */}
      {progress && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 text-secondary mr-2" />
            Progress Overview
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-600">Sessions</div>
              <div className="text-2xl font-bold">
                {progress.total_sessions || 0}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Avg Score</div>
              <div className="text-2xl font-bold">
                {progress.average_score || 0}/10
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Evaluations</div>
              <div className="text-2xl font-bold">
                {progress.evaluation_sessions || 0}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Last Active</div>
              <div className="text-sm font-medium">
                {progress.last_session
                  ? new Date(progress.last_session).toLocaleDateString()
                  : "Today"}
              </div>
            </div>
          </div>

          {/* Recommended Actions */}
          {progress.recommended_actions &&
            progress.recommended_actions.length > 0 && (
              <div className="mt-4 pt-4 border-t">
                <h4 className="font-medium text-gray-900 mb-2">
                  Recommended Actions
                </h4>
                <ul className="space-y-1">
                  {progress.recommended_actions.map((action, index) => (
                    <li
                      key={index}
                      className="flex items-start space-x-2 text-sm"
                    >
                      <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
        </div>
      )}
    </div>
  );

  const renderProfileEdit = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-900">Edit Profile</h2>
        <button
          onClick={() => setEditMode(false)}
          className="p-2 hover:bg-gray-100 rounded-lg"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Personal Info */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Personal Information</h3>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Full Name
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Role
            </label>
            <select
              name="current_role"
              value={formData.current_role}
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

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Experience (years)
            </label>
            <select
              name="experience_years"
              value={formData.experience_years}
              onChange={handleInputChange}
              className="input-field"
            >
              {experienceLevels.map((years) => (
                <option key={years} value={years}>
                  {years} years
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Interview Goals */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Interview Goals</h3>

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

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Companies
            </label>
            <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto p-2 border rounded-lg">
              {companies.slice(0, 30).map((company) => (
                <label
                  key={company.name}
                  className="flex items-center space-x-2"
                >
                  <input
                    type="checkbox"
                    checked={formData.target_companies.includes(company.name)}
                    onChange={() => handleCompanyToggle(company.name)}
                    className="text-primary"
                  />
                  <span className="text-sm">{company.name}</span>
                </label>
              ))}
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
              value={formData.timeline_weeks}
              onChange={handleInputChange}
              className="w-full"
            />
            <div className="text-center mt-2 text-primary font-semibold">
              {formData.timeline_weeks} weeks
            </div>
          </div>
        </div>

        {/* Preferences */}
        <div className="space-y-4 md:col-span-2">
          <h3 className="text-lg font-semibold">Learning Preferences</h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Learning Style
              </label>
              <select
                name="learning_style"
                value={formData.learning_style}
                onChange={handleInputChange}
                className="input-field"
              >
                {learningStyles.map((style) => (
                  <option key={style} value={style} className="capitalize">
                    {style}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Daily Practice (minutes)
              </label>
              <input
                type="number"
                name="daily_practice_minutes"
                value={formData.daily_practice_minutes}
                onChange={handleInputChange}
                min="30"
                max="240"
                step="15"
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Difficulty Preference
              </label>
              <select
                name="difficulty_preference"
                value={formData.difficulty_preference}
                onChange={handleInputChange}
                className="input-field"
              >
                {difficultyPreferences.map((pref) => (
                  <option key={pref} value={pref} className="capitalize">
                    {pref}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-4 pt-4 border-t">
        <button
          onClick={handleSaveProfile}
          disabled={saving}
          className="flex-1 btn-primary flex items-center justify-center space-x-2"
        >
          {saving ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              <span>Saving...</span>
            </>
          ) : (
            <>
              <Save className="h-5 w-5" />
              <span>Save Changes</span>
            </>
          )}
        </button>
        <button
          onClick={() => setEditMode(false)}
          className="flex-1 px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </div>
  );

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            User Profile
          </h1>
          <p className="text-gray-600">
            Manage your account and track your preparation journey
          </p>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
            <p className="text-gray-600">Loading profile...</p>
          </div>
        )}

        {/* Profile Content */}
        {!loading && userProfile && (
          <div className="bg-white rounded-xl shadow-lg p-8">
            {editMode ? renderProfileEdit() : renderProfileView()}

            {/* Logout Button */}
            {!editMode && (
              <div className="mt-8 pt-6 border-t">
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 text-red-600 hover:text-red-700"
                >
                  <LogOut className="h-5 w-5" />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        )}

        {/* Empty State - No User */}
        {!loading && !userProfile && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <User className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-700 mb-2">
              No Profile Found
            </h3>
            <p className="text-gray-500 mb-6">
              Complete the onboarding process to create your profile
            </p>
            <button
              onClick={() => (window.location.href = "/planner")}
              className="btn-primary"
            >
              Start Onboarding
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}
