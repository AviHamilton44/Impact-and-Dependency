
const colorMap = {
  'VL': 'bg-green-500 text-green-950',
  'L': 'bg-lime-500 text-lime-950',
  'M': 'bg-yellow-500 text-yellow-950',
  'H': 'bg-orange-500 text-orange-950',
  'VH': 'bg-red-500 text-red-950'
};

const labelMap = {
  'VL': 'Very Low',
  'L': 'Low',
  'M': 'Moderate',
  'H': 'High',
  'VH': 'Very High'
};

export default function StatusBadge({ level, className = '' }) {
  const colorClass = colorMap[level] || 'bg-gray-500 text-white';
  const label = labelMap[level] || level;
  
  return (
    <span className={`px-2 py-1 rounded-md text-xs font-semibold tracking-wide ${colorClass} ${className}`}>
      {label}
    </span>
  );
}
