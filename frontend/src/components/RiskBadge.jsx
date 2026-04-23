export default function RiskBadge({ score = 0 }) {
  const label = score >= 80 ? "High" : score >= 50 ? "Medium" : "Low";

  return (
    <span data-risk={label.toLowerCase()}>
      {label} Risk: {score}
    </span>
  );
}
