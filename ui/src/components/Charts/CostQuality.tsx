import { useQuery } from '@tanstack/react-query';
import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { analyticsApi } from '../../api/client';
import { useFilters } from '../../state/useFilters';

interface CostQualityProps {
  className?: string;
}

export function CostQuality({ className = "" }: CostQualityProps) {
  const { selectedScenario, selectedModels, selectedLengthBins, selectedJudgeType } = useFilters();

  const { data, isLoading, error } = useQuery({
    queryKey: ['cost_quality', selectedScenario, selectedModels, selectedLengthBins, selectedJudgeType],
    queryFn: async () => {
      return analyticsApi.costQuality({
        scenario: selectedScenario || undefined,
        model: selectedModels.length > 0 ? selectedModels.join(',') : undefined,
        length_bin: selectedLengthBins.length > 0 ? selectedLengthBins : undefined,
        judge_type: selectedJudgeType || undefined,
      });
    },
  });

  if (isLoading) {
    return (
      <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
        <h3 className="text-lg font-semibold mb-4">Cost vs Quality</h3>
        <div className="h-80 flex items-center justify-center">
          <div className="animate-pulse text-muted-foreground">Loading...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
        <h3 className="text-lg font-semibold mb-4">Cost vs Quality</h3>
        <div className="h-80 flex items-center justify-center">
          <div className="text-destructive">Error loading data</div>
        </div>
      </div>
    );
  }

  if (!data?.data || data.data.length === 0) {
    return (
      <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
        <h3 className="text-lg font-semibold mb-4">Cost vs Quality</h3>
        <div className="h-80 flex items-center justify-center">
          <div className="text-muted-foreground">No data available</div>
        </div>
      </div>
    );
  }

  // Group data by model and length_bin for different series
  const groupedData: Record<string, any[]> = {};
  data.data.forEach((point) => {
    const seriesKey = `${point.model} • ${point.length_bin}`;
    if (!groupedData[seriesKey]) {
      groupedData[seriesKey] = [];
    }
    groupedData[seriesKey].push(point);
  });

  // Color palette for different series
  const colors = [
    '#3B82F6', '#EF4444', '#10B981', '#F59E0B', 
    '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'
  ];

  return (
    <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Cost vs Quality</h3>
        <div className="text-sm text-muted-foreground">
          {data.data.length} data points
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <XAxis 
            type="number" 
            dataKey="x" 
            name="AUD / 1K tokens"
            domain={['dataMin - 0.0001', 'dataMax + 0.0001']}
            tickFormatter={(value) => value.toFixed(4)}
          />
          <YAxis 
            type="number" 
            dataKey="y" 
            name="Composite Score"
            domain={[0, 5]}
          />
          <Tooltip 
            formatter={(value, name) => [
              typeof value === 'number' ? value.toFixed(4) : value, 
              name
            ]}
            labelFormatter={() => ''}
            content={({ active, payload }) => {
              if (active && payload && payload.length > 0) {
                const data = payload[0].payload;
                return (
                  <div className="bg-popover p-3 rounded-lg shadow-lg border">
                    <p className="font-medium">{data.model}</p>
                    <p className="text-sm text-muted-foreground">{data.length_bin} • {data.scenario}</p>
                    <p className="text-sm">Cost: ${data.x.toFixed(4)} AUD/1K</p>
                    <p className="text-sm">Quality: {data.y.toFixed(2)}/5.0</p>
                    <p className="text-sm">Runs: {data.count}</p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend />
          
          {Object.entries(groupedData).map(([seriesName, points], index) => (
            <Scatter 
              key={seriesName}
              data={points} 
              name={seriesName}
              fill={colors[index % colors.length]}
            />
          ))}
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
