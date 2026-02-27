import Link from "next/link";

export default function AgentCard({
  title,
  description,
  icon: Icon,
  href,
  color = "primary",
}) {
  const colorClasses = {
    primary: "bg-blue-50 text-blue-600 border-blue-200",
    secondary: "bg-green-50 text-green-600 border-green-200",
    purple: "bg-purple-50 text-purple-600 border-purple-200",
    orange: "bg-orange-50 text-orange-600 border-orange-200",
  };

  return (
    <Link href={href}>
      <div className="agent-card cursor-pointer group">
        <div
          className={`w-12 h-12 rounded-lg ${colorClasses[color]} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
        >
          <Icon className="h-6 w-6" />
        </div>
        <h3 className="text-xl font-semibold mb-2">{title}</h3>
        <p className="text-gray-600">{description}</p>
      </div>
    </Link>
  );
}
