// ✅ Утилита для извлечения текста ошибки из любого формата
export function extractErrorMessage(err: any, fallback = 'Ошибка'): string {
  if (!err?.response?.data) return fallback;

  const data = err.response.data;

  // Формат Pydantic 422: { detail: [{ msg: "..." }, ...] }
  if (Array.isArray(data.detail)) {
    return data.detail.map((item: any) => item.msg || JSON.stringify(item)).join('; ');
  }

  // Формат Pydantic 422 одиночная: { detail: "..." }
  if (typeof data.detail === 'string') {
    return data.detail;
  }

  // Другие ошибки
  if (typeof data === 'string') return data;

  return fallback;
}