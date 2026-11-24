export const MAX_STUDENT_CODE_LENGTH = 10_000;

export class PythonLabApiError extends Error {
  constructor(code, status = null) {
    super(code);
    this.name = 'PythonLabApiError';
    this.code = code;
    this.status = status;
  }
}

async function readJson(response) {
  try {
    return await response.json();
  } catch {
    throw new PythonLabApiError('invalid_response', response.status);
  }
}

export async function fetchExercises(
  apiUrl,
  { signal, fetchImpl = fetch } = {}
) {
  let response;

  try {
    response = await fetchImpl(`${apiUrl}/exercises`, { signal });
  } catch (error) {
    if (error?.name === 'AbortError') throw error;
    throw new PythonLabApiError('unavailable');
  }

  if (!response.ok) {
    throw new PythonLabApiError('request_failed', response.status);
  }

  const data = await readJson(response);
  const exercises = Array.isArray(data)
    ? data
    : Array.isArray(data?.value)
      ? data.value
      : null;

  if (!exercises || exercises.length === 0) {
    throw new PythonLabApiError('invalid_catalog', response.status);
  }

  return exercises;
}

export async function executeExercise(
  apiUrl,
  payload,
  { signal, fetchImpl = fetch } = {}
) {
  if (
    typeof payload?.student_code !== 'string' ||
    payload.student_code.length > MAX_STUDENT_CODE_LENGTH
  ) {
    throw new PythonLabApiError('code_too_long');
  }

  let response;

  try {
    response = await fetchImpl(`${apiUrl}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal
    });
  } catch (error) {
    if (error?.name === 'AbortError') throw error;
    throw new PythonLabApiError('unavailable');
  }

  if (!response.ok) {
    throw new PythonLabApiError('request_failed', response.status);
  }

  const data = await readJson(response);

  if (!data || typeof data !== 'object' || typeof data.status !== 'string') {
    throw new PythonLabApiError('invalid_response', response.status);
  }

  return data;
}
