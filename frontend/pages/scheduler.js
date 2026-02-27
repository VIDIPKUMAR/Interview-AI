import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { agentAPI } from "../utils/api";
import {
  Calendar,
  Clock,
  ChevronLeft,
  ChevronRight,
  Download,
  Calendar as CalendarIcon,
  BookOpen,
  Coffee,
  Moon,
  Sun,
  Zap,
  Target,
  CheckCircle,
  Loader2,
  Bell,
  MapPin,
} from "lucide-react";

export default function Scheduler() {
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [schedule, setSchedule] = useState(null);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [view, setView] = useState("week"); // 'day' or 'week'
  const [preferences, setPreferences] = useState({
    work_hours: "9 AM - 6 PM",
    timezone: "UTC",
    available_days: ["weekdays", "saturday"],
    max_daily_sessions: 3,
    session_length: "moderate",
    break_preferences: "pomodoro",
    intensity: "moderate",
    preferred_times: ["morning", "evening"],
  });

  const timeSlots = [
    "06:00",
    "07:00",
    "08:00",
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
    "18:00",
    "19:00",
    "20:00",
    "21:00",
    "22:00",
    "23:00",
  ];

  const daysOfWeek = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
  ];

  useEffect(() => {
    const savedUserId = localStorage.getItem("interviewai_user_id");
    if (savedUserId) {
      setUserId(savedUserId);
    }
  }, []);

  const formatDate = (date) => {
    return date.toISOString().split("T")[0];
  };

  const getWeekDates = () => {
    const start = new Date(selectedDate);
    start.setDate(start.getDate() - start.getDay() + 1); // Start from Monday
    const week = [];
    for (let i = 0; i < 7; i++) {
      const day = new Date(start);
      day.setDate(start.getDate() + i);
      week.push(day);
    }
    return week;
  };

  const handlePrevious = () => {
    const newDate = new Date(selectedDate);
    if (view === "day") {
      newDate.setDate(newDate.getDate() - 1);
    } else {
      newDate.setDate(newDate.getDate() - 7);
    }
    setSelectedDate(newDate);
  };

  const handleNext = () => {
    const newDate = new Date(selectedDate);
    if (view === "day") {
      newDate.setDate(newDate.getDate() + 1);
    } else {
      newDate.setDate(newDate.getDate() + 7);
    }
    setSelectedDate(newDate);
  };

  const handleCreateSchedule = async () => {
    setLoading(true);
    try {
      // First, get a learning plan
      const planResult = await agentAPI.createPlan({
        name: localStorage.getItem("interviewai_user_name") || "User",
        target_role: "SDE",
        target_companies: ["Google", "Microsoft"],
        experience: "3 years",
        daily_practice_minutes: 90,
      });

      // Create schedule
      const result = await agentAPI.createSchedule({
        user_id: userId || "test_001",
        learning_plan: planResult.learning_plan,
        constraints: {
          work_hours: preferences.work_hours,
          timezone: preferences.timezone,
          available_days: preferences.available_days,
          max_daily_sessions: preferences.max_daily_sessions,
        },
        preferences: {
          session_length: preferences.session_length,
          break_preferences: preferences.break_preferences,
          intensity: preferences.intensity,
        },
      });

      setSchedule(result);
    } catch (error) {
      console.error("Error creating schedule:", error);
      alert("Failed to create schedule. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getSessionForTimeSlot = (day, timeSlot) => {
    if (!schedule?.daily_schedule) return null;

    const daySchedule = schedule.daily_schedule.find(
      (d) => new Date(d.date).toDateString() === day.toDateString()
    );

    if (!daySchedule) return null;

    return daySchedule.sessions?.find((s) => s.time_slot.startsWith(timeSlot));
  };

  const getActivityColor = (type) => {
    switch (type) {
      case "theory_study":
        return "bg-blue-100 border-blue-300 text-blue-800";
      case "practice_problems":
        return "bg-green-100 border-green-300 text-green-800";
      case "review":
        return "bg-purple-100 border-purple-300 text-purple-800";
      case "mock_interview":
        return "bg-orange-100 border-orange-300 text-orange-800";
      default:
        return "bg-gray-100 border-gray-300 text-gray-800";
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case "theory_study":
        return <BookOpen className="h-4 w-4" />;
      case "practice_problems":
        return <Zap className="h-4 w-4" />;
      case "review":
        return <Target className="h-4 w-4" />;
      case "mock_interview":
        return <Calendar className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const renderPreferenceSelector = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Customize Your Schedule</h3>

      {/* Work Hours */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Work Hours
        </label>
        <select
          value={preferences.work_hours}
          onChange={(e) =>
            setPreferences((prev) => ({ ...prev, work_hours: e.target.value }))
          }
          className="input-field"
        >
          <option>9 AM - 5 PM</option>
          <option>9 AM - 6 PM</option>
          <option>10 AM - 7 PM</option>
          <option>Flexible / Remote</option>
          <option>Night Shift</option>
        </select>
      </div>

      {/* Available Days */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Available Days
        </label>
        <div className="space-y-2">
          {[
            "Weekdays Only",
            "Weekdays + Saturday",
            "Weekends Only",
            "All Days",
          ].map((option) => (
            <label key={option} className="flex items-center space-x-2">
              <input
                type="radio"
                name="available_days"
                value={option.toLowerCase().replace(/ /g, "_")}
                checked={preferences.available_days.includes(
                  option.toLowerCase().replace(/ /g, "_")
                )}
                onChange={(e) =>
                  setPreferences((prev) => ({
                    ...prev,
                    available_days: [e.target.value],
                  }))
                }
                className="text-primary"
              />
              <span>{option}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Session Preferences */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Session Length
          </label>
          <select
            value={preferences.session_length}
            onChange={(e) =>
              setPreferences((prev) => ({
                ...prev,
                session_length: e.target.value,
              }))
            }
            className="input-field"
          >
            <option value="short">Short (30-45 min)</option>
            <option value="moderate">Moderate (45-90 min)</option>
            <option value="long">Long (90-120 min)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Break Pattern
          </label>
          <select
            value={preferences.break_preferences}
            onChange={(e) =>
              setPreferences((prev) => ({
                ...prev,
                break_preferences: e.target.value,
              }))
            }
            className="input-field"
          >
            <option value="pomodoro">Pomodoro (25/5)</option>
            <option value="power">Power Hour (50/10)</option>
            <option value="deep">Deep Work (90/15)</option>
          </select>
        </div>
      </div>

      {/* Preferred Times */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Preferred Study Times
        </label>
        <div className="flex space-x-4">
          {["morning", "afternoon", "evening", "night"].map((time) => (
            <label key={time} className="flex items-center space-x-1">
              <input
                type="checkbox"
                checked={preferences.preferred_times.includes(time)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setPreferences((prev) => ({
                      ...prev,
                      preferred_times: [...prev.preferred_times, time],
                    }));
                  } else {
                    setPreferences((prev) => ({
                      ...prev,
                      preferred_times: prev.preferred_times.filter(
                        (t) => t !== time
                      ),
                    }));
                  }
                }}
                className="text-primary"
              />
              <span className="capitalize">{time}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Intensity */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Study Intensity
        </label>
        <div className="flex space-x-4">
          {["light", "moderate", "intense"].map((level) => (
            <label key={level} className="flex items-center space-x-1">
              <input
                type="radio"
                name="intensity"
                value={level}
                checked={preferences.intensity === level}
                onChange={(e) =>
                  setPreferences((prev) => ({
                    ...prev,
                    intensity: e.target.value,
                  }))
                }
                className="text-primary"
              />
              <span className="capitalize">{level}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Create Button */}
      <button
        onClick={handleCreateSchedule}
        disabled={loading}
        className="w-full btn-primary flex items-center justify-center space-x-2"
      >
        {loading ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Creating Optimal Schedule...</span>
          </>
        ) : (
          <>
            <CalendarIcon className="h-5 w-5" />
            <span>Generate My Schedule</span>
          </>
        )}
      </button>
    </div>
  );

  const renderDayView = () => (
    <div className="space-y-4">
      {/* Day Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold">
          {selectedDate.toLocaleDateString("en-US", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </h3>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">
            Total:{" "}
            {schedule?.daily_schedule?.find(
              (d) =>
                new Date(d.date).toDateString() === selectedDate.toDateString()
            )?.total_learning_time || 0}{" "}
            min
          </span>
        </div>
      </div>

      {/* Time Slots */}
      <div className="space-y-2">
        {timeSlots.map((timeSlot) => {
          const session = getSessionForTimeSlot(selectedDate, timeSlot);
          const hour = parseInt(timeSlot.split(":")[0]);
          let period = "neutral";
          if (hour >= 5 && hour < 12) period = "morning";
          else if (hour >= 12 && hour < 17) period = "afternoon";
          else if (hour >= 17 && hour < 21) period = "evening";
          else period = "night";

          return (
            <div
              key={timeSlot}
              className={`flex items-center border rounded-lg transition-all ${
                session ? "bg-white shadow-md" : "bg-gray-50"
              }`}
            >
              <div
                className={`w-24 px-4 py-3 font-medium border-r ${
                  period === "morning"
                    ? "text-yellow-600"
                    : period === "afternoon"
                    ? "text-orange-600"
                    : period === "evening"
                    ? "text-purple-600"
                    : "text-blue-600"
                }`}
              >
                {timeSlot}
              </div>

              <div className="flex-1 px-4 py-3">
                {session ? (
                  <div
                    className={`p-3 rounded-lg border ${getActivityColor(
                      session.activity_type
                    )}`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3">
                        {getActivityIcon(session.activity_type)}
                        <div>
                          <h4 className="font-medium">{session.topic}</h4>
                          <p className="text-sm opacity-90">
                            {session.activity_type.replace(/_/g, " ")}
                          </p>
                          {session.learning_objective && (
                            <p className="text-xs mt-1 opacity-75">
                              🎯 {session.learning_objective}
                            </p>
                          )}
                        </div>
                      </div>
                      <span className="text-sm font-medium">
                        {session.duration_minutes} min
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="text-gray-400 text-sm">
                    {preferences.preferred_times.includes(period) &&
                      !session && (
                        <span className="text-green-500">
                          ✨ Available for study
                        </span>
                      )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  const renderWeekView = () => {
    const weekDates = getWeekDates();

    return (
      <div className="space-y-4">
        {/* Week Header */}
        <div className="grid grid-cols-7 gap-2 mb-2">
          {daysOfWeek.map((day, index) => (
            <div key={day} className="text-center font-medium text-gray-700">
              {day.substring(0, 3)}
              <div className="text-sm text-gray-500">
                {weekDates[index].getDate()}
              </div>
            </div>
          ))}
        </div>

        {/* Week Grid */}
        <div className="grid grid-cols-7 gap-2">
          {weekDates.map((date, dayIndex) => {
            const daySchedule = schedule?.daily_schedule?.find(
              (d) => new Date(d.date).toDateString() === date.toDateString()
            );
            const isToday = date.toDateString() === new Date().toDateString();

            return (
              <div
                key={dayIndex}
                className={`border rounded-lg p-2 min-h-[200px] ${
                  isToday ? "border-primary bg-blue-50" : "border-gray-200"
                }`}
                onClick={() => {
                  setSelectedDate(date);
                  setView("day");
                }}
              >
                <div className="text-xs text-gray-500 mb-2">
                  {date.getDate()}{" "}
                  {date.toLocaleDateString("en-US", { month: "short" })}
                </div>

                {daySchedule?.sessions?.map((session, sessionIndex) => (
                  <div
                    key={sessionIndex}
                    className={`text-xs p-1 mb-1 rounded ${getActivityColor(
                      session.activity_type
                    )} cursor-pointer truncate`}
                    title={`${session.time_slot}: ${session.topic}`}
                  >
                    {session.topic}
                  </div>
                ))}

                {daySchedule?.total_learning_time > 0 && (
                  <div className="text-xs text-gray-500 mt-2">
                    {daySchedule.total_learning_time} min total
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI Scheduler Agent
          </h1>
          <p className="text-gray-600">
            Optimize your study schedule with cognitive science principles
          </p>
        </div>

        {/* Main Content */}
        <div className="grid md:grid-cols-3 gap-8">
          {/* Left Column - Preferences */}
          <div className="md:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-20">
              {!schedule ? (
                renderPreferenceSelector()
              ) : (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Schedule Created!</h3>
                  <div className="bg-green-50 rounded-lg p-4">
                    <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
                    <p className="text-sm text-green-700 text-center">
                      Your optimized schedule is ready
                    </p>
                  </div>

                  {/* Schedule Stats */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Total Sessions:</span>
                      <span className="font-semibold">
                        {schedule.schedule_metrics?.total_sessions}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Total Hours:</span>
                      <span className="font-semibold">
                        {schedule.schedule_metrics?.total_hours}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Mock Interviews:</span>
                      <span className="font-semibold">
                        {schedule.schedule_metrics?.mock_interviews}
                      </span>
                    </div>
                  </div>

                  {/* Optimization Techniques */}
                  <div>
                    <h4 className="font-medium text-sm mb-2">
                      Optimizations Applied:
                    </h4>
                    <ul className="space-y-1">
                      {schedule.optimization_techniques?.map((tech, index) => (
                        <li
                          key={index}
                          className="text-xs text-gray-600 flex items-start"
                        >
                          <CheckCircle className="h-3 w-3 text-green-500 mr-1 flex-shrink-0 mt-0.5" />
                          {tech.technique.replace(/_/g, " ")}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Action Buttons */}
                  <div className="space-y-2">
                    <button
                      onClick={() => setSchedule(null)}
                      className="w-full btn-primary"
                    >
                      Create New Schedule
                    </button>
                    <button className="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center justify-center space-x-2">
                      <Download className="h-4 w-4" />
                      <span>Export Calendar</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Calendar */}
          <div className="md:col-span-2">
            <div className="bg-white rounded-xl shadow-lg p-6">
              {/* Calendar Controls */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handlePrevious}
                    className="p-2 hover:bg-gray-100 rounded-lg"
                  >
                    <ChevronLeft className="h-5 w-5" />
                  </button>
                  <button
                    onClick={handleNext}
                    className="p-2 hover:bg-gray-100 rounded-lg"
                  >
                    <ChevronRight className="h-5 w-5" />
                  </button>
                  <span className="font-medium">
                    {view === "day"
                      ? selectedDate.toLocaleDateString("en-US", {
                          month: "long",
                          year: "numeric",
                        })
                      : `Week of ${getWeekDates()[0].toLocaleDateString(
                          "en-US",
                          { month: "short", day: "numeric" }
                        )}`}
                  </span>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setView("day")}
                    className={`px-3 py-1 rounded-lg text-sm ${
                      view === "day" ? "bg-primary text-white" : "bg-gray-100"
                    }`}
                  >
                    Day
                  </button>
                  <button
                    onClick={() => setView("week")}
                    className={`px-3 py-1 rounded-lg text-sm ${
                      view === "week" ? "bg-primary text-white" : "bg-gray-100"
                    }`}
                  >
                    Week
                  </button>
                </div>
              </div>

              {/* Calendar View */}
              {schedule ? (
                view === "day" ? (
                  renderDayView()
                ) : (
                  renderWeekView()
                )
              ) : (
                <div className="text-center py-12">
                  <CalendarIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-700 mb-2">
                    No Schedule Yet
                  </h3>
                  <p className="text-gray-500">
                    Set your preferences on the left to generate an optimized
                    study schedule
                  </p>
                </div>
              )}

              {/* Legend */}
              {schedule && (
                <div className="mt-6 pt-4 border-t border-gray-200">
                  <h4 className="text-sm font-medium mb-2">Activity Types</h4>
                  <div className="flex flex-wrap gap-3">
                    <div className="flex items-center space-x-1">
                      <div className="w-3 h-3 bg-blue-100 border border-blue-300 rounded"></div>
                      <span className="text-xs">Theory Study</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <div className="w-3 h-3 bg-green-100 border border-green-300 rounded"></div>
                      <span className="text-xs">Practice Problems</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <div className="w-3 h-3 bg-purple-100 border border-purple-300 rounded"></div>
                      <span className="text-xs">Review</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <div className="w-3 h-3 bg-orange-100 border border-orange-300 rounded"></div>
                      <span className="text-xs">Mock Interview</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
