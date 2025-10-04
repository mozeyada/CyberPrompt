import { useFilters } from '../../state/useFilters'

const LENGTH_BINS = [
  { value: 'S', label: 'S (250-350) - Tactical' },
  { value: 'M', label: 'M (350-500) - Analytical' },
  { value: 'L', label: 'L (600-750) - Strategic' }
]

export function LengthBinMulti() {
  const { selectedLengthBins, setSelectedLengthBins } = useFilters()

  const handleLengthBinToggle = (bin: string) => {
    if (selectedLengthBins.includes(bin)) {
      setSelectedLengthBins(selectedLengthBins.filter(b => b !== bin))
    } else {
      setSelectedLengthBins([...selectedLengthBins, bin])
    }
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">Length Bins</label>
      <div className="space-y-1">
        {LENGTH_BINS.map(bin => (
          <label key={bin.value} className="flex items-center">
            <input
              type="checkbox"
              checked={selectedLengthBins.includes(bin.value)}
              onChange={() => handleLengthBinToggle(bin.value)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">{bin.label}</span>
          </label>
        ))}
      </div>
    </div>
  )
}