import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { agentAPI } from "../utils/api";
import {
  Building2,
  Search,
  TrendingUp,
  Award,
  AlertTriangle,
  Globe,
  Calendar,
  BarChart3,
  Users,
  Target,
  Sparkles,
  Loader2,
  ChevronRight,
  BookOpen,
  MapPin,
  Briefcase,
  Clock,
  Star,
  Shield,
  Lightbulb,
} from "lucide-react";

export default function CompanyAnalyzer() {
  const [loading, setLoading] = useState(false);
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [companyData, setCompanyData] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedIndustry, setSelectedIndustry] = useState("all");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [targetRole, setTargetRole] = useState("SDE");
  const [targetCompanies, setTargetCompanies] = useState([]);

  const industries = [
    "all",
    "Technology",
    "E-commerce",
    "Finance",
    "Gaming",
    "Automotive",
    "Aerospace",
    "Healthcare",
  ];

  const roles = [
    "SDE",
    "Senior SDE",
    "ML Engineer",
    "Data Scientist",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "DevOps Engineer",
    "System Design Engineer",
    "Product Manager",
  ];

  useEffect(() => {
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

  const handleCompanySelect = async (company) => {
    setSelectedCompany(company);
    setLoading(true);
    try {
      const data = await agentAPI.getCompanyProblems(company.name);
      setCompanyData(data);
    } catch (error) {
      console.error("Error fetching company data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeCompanies = async () => {
    if (targetCompanies.length === 0) return;

    setLoading(true);
    try {
      const result = await agentAPI.analyzeCompanies({
        target_companies: targetCompanies,
        target_role: targetRole,
      });
      setAnalysisResult(result);
    } catch (error) {
      console.error("Error analyzing companies:", error);
    } finally {
      setLoading(false);
    }
  };

  const toggleCompany = (companyName) => {
    setTargetCompanies((prev) =>
      prev.includes(companyName)
        ? prev.filter((c) => c !== companyName)
        : [...prev, companyName]
    );
  };

  const filteredCompanies = companies.filter((company) => {
    const matchesSearch = company.name
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    const matchesIndustry =
      selectedIndustry === "all" || company.industry === selectedIndustry;
    return matchesSearch && matchesIndustry;
  });

  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case "easy":
        return "text-green-600 bg-green-50";
      case "medium":
        return "text-yellow-600 bg-yellow-50";
      case "hard":
        return "text-red-600 bg-red-50";
      case "very hard":
        return "text-purple-600 bg-purple-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const renderCompanyList = () => (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-semibold mb-4 flex items-center">
        <Building2 className="h-5 w-5 text-primary mr-2" />
        Companies Database ({filteredCompanies.length})
      </h2>

      {/* Search and Filter */}
      <div className="space-y-4 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search companies..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-10"
          />
        </div>

        <select
          value={selectedIndustry}
          onChange={(e) => setSelectedIndustry(e.target.value)}
          className="input-field"
        >
          {industries.map((industry) => (
            <option key={industry} value={industry}>
              {industry === "all" ? "All Industries" : industry}
            </option>
          ))}
        </select>
      </div>

      {/* Company Grid */}
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {filteredCompanies.map((company) => (
          <button
            key={company.name}
            onClick={() => handleCompanySelect(company)}
            className={`w-full text-left p-3 rounded-lg border-2 transition-all ${
              selectedCompany?.name === company.name
                ? "border-primary bg-blue-50"
                : "border-gray-200 hover:border-gray-300"
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-gray-900">{company.name}</h3>
                <p className="text-sm text-gray-600">{company.industry}</p>
              </div>
              <div className="text-right">
                <span className="text-sm font-medium text-primary">
                  {company.problem_count} problems
                </span>
                {company.hq !== "Unknown" && (
                  <p className="text-xs text-gray-500 flex items-center mt-1">
                    <MapPin className="h-3 w-3 mr-1" />
                    {company.hq.split(",")[0]}
                  </p>
                )}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );

  const renderCompanyDetails = () => {
    if (!selectedCompany || !companyData) return null;

    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {selectedCompany.name}
            </h2>
            <div className="flex items-center space-x-4 mt-2">
              <span className="flex items-center text-sm text-gray-600">
                <MapPin className="h-4 w-4 mr-1" />
                {companyData.metadata?.hq || "Location N/A"}
              </span>
              <span className="flex items-center text-sm text-gray-600">
                <Briefcase className="h-4 w-4 mr-1" />
                {companyData.metadata?.industry || "Industry N/A"}
              </span>
            </div>
          </div>
          <div
            className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(
              companyData.metadata?.difficulty_bias
            )}`}
          >
            {companyData.metadata?.difficulty_bias || "Medium"} bias
          </div>
        </div>

        {/* Interview Process */}
        {companyData.metadata?.interview_process && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <Calendar className="h-5 w-5 text-primary mr-2" />
              Interview Process
            </h3>
            <ul className="space-y-2">
              {companyData.metadata.interview_process.map((step, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <ChevronRight className="h-4 w-4 text-primary flex-shrink-0 mt-1" />
                  <span className="text-gray-700">{step}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Focus Areas */}
        {companyData.metadata?.focus_areas && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <Target className="h-5 w-5 text-primary mr-2" />
              Key Focus Areas
            </h3>
            <div className="flex flex-wrap gap-2">
              {companyData.metadata.focus_areas.map((area, index) => (
                <span
                  key={index}
                  className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                >
                  {area}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Culture */}
        {companyData.metadata?.culture && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <Users className="h-5 w-5 text-primary mr-2" />
              Culture & Values
            </h3>
            <div className="flex flex-wrap gap-2">
              {companyData.metadata.culture.map((value, index) => (
                <span
                  key={index}
                  className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm"
                >
                  {value}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Common Problems */}
        <div>
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <BookOpen className="h-5 w-5 text-primary mr-2" />
            Frequently Asked Problems ({companyData.total_problems})
          </h3>
          <div className="space-y-3">
            {companyData.problems?.map((problem, index) => (
              <div
                key={index}
                className="border rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h4 className="font-semibold text-gray-900">
                      {problem.title}
                    </h4>
                    <div className="flex items-center space-x-3 mt-1">
                      <span
                        className={`text-xs px-2 py-1 rounded-full ${getDifficultyColor(
                          problem.difficulty
                        )}`}
                      >
                        {problem.difficulty}
                      </span>
                      <span className="text-xs text-gray-500">
                        {problem.topics?.join(" • ")}
                      </span>
                    </div>
                  </div>
                  <a
                    href={problem.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:text-blue-700 text-sm"
                  >
                    Solve →
                  </a>
                </div>

                {problem.company_frequency && (
                  <div className="mt-2 text-sm text-gray-600">
                    <span className="font-medium">
                      Asked {problem.company_frequency.frequency} times
                    </span>
                    {" • "}Last asked: {problem.company_frequency.last_asked}
                    {problem.company_frequency.role && (
                      <> • Roles: {problem.company_frequency.role.join(", ")}</>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderMultiCompanyAnalysis = () => (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-semibold mb-4 flex items-center">
        <BarChart3 className="h-5 w-5 text-primary mr-2" />
        Multi-Company Analysis
      </h2>

      {/* Selection */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Role
          </label>
          <select
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
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
            Select Companies to Compare
          </label>
          <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto p-2 border rounded-lg">
            {companies.slice(0, 20).map((company) => (
              <label key={company.name} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={targetCompanies.includes(company.name)}
                  onChange={() => toggleCompany(company.name)}
                  className="text-primary"
                />
                <span className="text-sm">{company.name}</span>
              </label>
            ))}
          </div>
        </div>

        <button
          onClick={handleAnalyzeCompanies}
          disabled={targetCompanies.length === 0 || loading}
          className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {loading ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Sparkles className="h-5 w-5" />
              <span>Analyze Selected Companies</span>
            </>
          )}
        </button>
      </div>

      {/* Analysis Results */}
      {analysisResult && (
        <div className="space-y-6">
          {/* Company Insights */}
          {Object.entries(analysisResult.company_insights || {}).map(
            ([company, insights]) => (
              <div key={company} className="border rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3">{company}</h3>

                {/* Core Topics */}
                <div className="mb-3">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">
                    Core Topics
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {insights.core_topics?.map((topic, i) => (
                      <span
                        key={i}
                        className="bg-gray-100 px-2 py-1 rounded text-sm"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Success Traits */}
                {insights.success_traits && (
                  <div className="mb-3">
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                      <Award className="h-4 w-4 text-green-500 mr-1" />
                      Success Traits
                    </h4>
                    <ul className="list-disc list-inside text-sm text-gray-600">
                      {insights.success_traits.slice(0, 3).map((trait, i) => (
                        <li key={i}>{trait}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Red Flags */}
                {insights.red_flags && (
                  <div className="mb-3">
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                      <AlertTriangle className="h-4 w-4 text-red-500 mr-1" />
                      Red Flags
                    </h4>
                    <ul className="list-disc list-inside text-sm text-gray-600">
                      {insights.red_flags.slice(0, 3).map((flag, i) => (
                        <li key={i}>{flag}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recent Trends */}
                {insights.recent_trends && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                      <TrendingUp className="h-4 w-4 text-blue-500 mr-1" />
                      Recent Trends
                    </h4>
                    <ul className="list-disc list-inside text-sm text-gray-600">
                      {insights.recent_trends.slice(0, 2).map((trend, i) => (
                        <li key={i}>{trend}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )
          )}

          {/* Consolidated Requirements */}
          {analysisResult.consolidated_requirements && (
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-3">
                Common Requirements Across Companies
              </h3>
              <div className="flex flex-wrap gap-2">
                {analysisResult.consolidated_requirements.priority_topics?.map(
                  (topic, i) => (
                    <span
                      key={i}
                      className="bg-white px-3 py-1 rounded-full text-sm shadow-sm"
                    >
                      {topic}
                    </span>
                  )
                )}
              </div>
            </div>
          )}

          {/* Company Tips */}
          {analysisResult.company_specific_tips && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Preparation Tips</h3>
              {Object.entries(analysisResult.company_specific_tips).map(
                ([company, tips]) => (
                  <div key={company} className="mb-3">
                    <h4 className="font-medium text-gray-800 mb-2">
                      {company}
                    </h4>
                    <ul className="space-y-1">
                      {tips.map((tip, i) => (
                        <li
                          key={i}
                          className="text-sm text-gray-600 flex items-start"
                        >
                          <Lightbulb className="h-4 w-4 text-yellow-500 mr-2 flex-shrink-0 mt-0.5" />
                          {tip}
                        </li>
                      ))}
                    </ul>
                  </div>
                )
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Company DNA Analyzer
          </h1>
          <p className="text-gray-600">
            Decode interview patterns across 50+ companies
          </p>
        </div>

        {/* Main Grid */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Company List */}
          <div className="lg:col-span-1">{renderCompanyList()}</div>

          {/* Middle Column - Company Details */}
          <div className="lg:col-span-1">
            {selectedCompany ? (
              loading ? (
                <div className="bg-white rounded-xl shadow-lg p-12 text-center">
                  <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
                  <p className="text-gray-600">Loading company data...</p>
                </div>
              ) : (
                renderCompanyDetails()
              )
            ) : (
              <div className="bg-white rounded-xl shadow-lg p-12 text-center">
                <Building2 className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-700 mb-2">
                  Select a Company
                </h3>
                <p className="text-gray-500">
                  Choose a company from the list to view detailed interview
                  patterns
                </p>
              </div>
            )}
          </div>

          {/* Right Column - Multi-Company Analysis */}
          <div className="lg:col-span-1">{renderMultiCompanyAnalysis()}</div>
        </div>

        {/* Stats Footer */}
        <div className="mt-8 bg-white rounded-xl shadow-lg p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {companies.length}
              </div>
              <div className="text-sm text-gray-600">Companies</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-secondary">
                {companies.reduce((acc, c) => acc + (c.problem_count || 0), 0)}
              </div>
              <div className="text-sm text-gray-600">Total Problems</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {new Set(companies.map((c) => c.industry)).size}
              </div>
              <div className="text-sm text-gray-600">Industries</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">24/7</div>
              <div className="text-sm text-gray-600">AI Analysis</div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
