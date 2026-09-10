export const POST_TYPES = {
  lost_pet: { label: 'Lost pet', color: '#B5533C', bg: '#F6E7E2', icon: '\u{1F43E}' },
  lost_item: { label: 'Lost item', color: '#8A6D3B', bg: '#F3ECDD', icon: '\u{1F4E6}' },
  found_item: { label: 'Found item', color: '#1F5C52', bg: '#E4EEEC', icon: '\u{2728}' },
  alert: { label: 'Alert', color: '#A63B2E', bg: '#F7E3E0', icon: '\u{26A0}' },
}

export function typeMeta(type) {
  return POST_TYPES[type] || { label: type, color: '#5B6660', bg: '#EDEEEB', icon: '\u{1F4CD}' }
}

export function formatRelativeTime(dateStr) {
  const date = new Date(dateStr)
  const diffMs = Date.now() - date.getTime()
  const diffMin = Math.round(diffMs / 60000)
  if (diffMin < 1) return 'just now'
  if (diffMin < 60) return `${diffMin}m ago`
  const diffHr = Math.round(diffMin / 60)
  if (diffHr < 24) return `${diffHr}h ago`
  const diffDay = Math.round(diffHr / 24)
  if (diffDay < 7) return `${diffDay}d ago`
  return date.toLocaleDateString()
}
