import { useNotifications } from '../context/NotificationContext'

export default function ToastStack() {
  const { toasts } = useNotifications()

  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm">
      {toasts.map((t) => (
        <div
          key={t.id}
          className="bg-ink text-paper rounded shadow-lg px-4 py-3 text-sm animate-[fadeIn_0.2s_ease-out]"
          role="status"
        >
          {t.message}
        </div>
      ))}
    </div>
  )
}
