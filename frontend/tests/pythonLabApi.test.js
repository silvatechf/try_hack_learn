import test from 'node:test';
import assert from 'node:assert/strict';

import {
  executeExercise,
  fetchExercises,
  MAX_STUDENT_CODE_LENGTH,
  PythonLabApiError
} from '../src/services/pythonLabApi.js';

function jsonResponse(body, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    async json() {
      return body;
    }
  };
}

test('fetchExercises accepts the current catalog array contract', async () => {
  const exercises = [{ exercise_id: 'PY-001' }];
  const result = await fetchExercises('http://localhost/api', {
    fetchImpl: async () => jsonResponse(exercises)
  });

  assert.deepEqual(result, exercises);
});

test('fetchExercises rejects unsuccessful HTTP responses', async () => {
  await assert.rejects(
    fetchExercises('http://localhost/api', {
      fetchImpl: async () => jsonResponse({ detail: 'unavailable' }, 503)
    }),
    error => error instanceof PythonLabApiError &&
      error.code === 'request_failed' &&
      error.status === 503
  );
});

test('executeExercise rejects oversized code before making a request', async () => {
  let requestMade = false;

  await assert.rejects(
    executeExercise('http://localhost/api', {
      exercise_id: 'PY-001',
      student_code: 'x'.repeat(MAX_STUDENT_CODE_LENGTH + 1)
    }, {
      fetchImpl: async () => {
        requestMade = true;
        return jsonResponse({ status: 'EXECUTED' });
      }
    }),
    error => error instanceof PythonLabApiError && error.code === 'code_too_long'
  );

  assert.equal(requestMade, false);
});

test('executeExercise preserves technical overflow responses returned with HTTP 200', async () => {
  const result = await executeExercise('http://localhost/api', {
    exercise_id: 'PY-001',
    student_code: "print('X' * 70000)"
  }, {
    fetchImpl: async () => jsonResponse({
      status: 'OUTPUT_LIMIT_EXCEEDED',
      max_output_bytes: 65_536
    })
  });

  assert.equal(result.status, 'OUTPUT_LIMIT_EXCEEDED');
  assert.equal(result.max_output_bytes, 65_536);
});

test('executeExercise rejects malformed success payloads', async () => {
  await assert.rejects(
    executeExercise('http://localhost/api', {
      exercise_id: 'PY-001',
      student_code: 'pass'
    }, {
      fetchImpl: async () => jsonResponse({ unexpected: true })
    }),
    error => error instanceof PythonLabApiError && error.code === 'invalid_response'
  );
});
