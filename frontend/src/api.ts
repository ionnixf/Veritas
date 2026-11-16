export const API_BASE = (
  import.meta.env.VITE_API_BASE_URL || "/api/v1"
).replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    public code: string,
    public status: number,
  ) {
    super(message);
  }
}

function connectionError(error: unknown) {
  return new ApiError(
    error instanceof Error && error.name === "TimeoutError"
      ? "The request timed out. The server may still be working. Wait a moment before retrying."
      : "Cannot reach the analysis server. Check that the backend is running, then retry.",
    "connection_error",
    0,
  );
}

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: AbortSignal.timeout(120_000),
    });
  } catch (error) {
    throw connectionError(error);
  }
  if (!response.ok) {
    const body = await response.json().catch((error: unknown) => {
      if (!(error instanceof SyntaxError)) throw connectionError(error);
      return null;
    });
    throw new ApiError(
      body?.error?.message ||
        `The server could not complete this request (HTTP ${response.status}).`,
      body?.error?.code || "server_error",
      response.status,
    );
  }
  try {
    if (path.startsWith("/templates/")) return (await response.blob()) as T;
    return (await response.json()) as T;
  } catch (error) {
    if (!(error instanceof SyntaxError)) throw connectionError(error);
    throw new ApiError(
      "The server returned an unreadable response. Check the API URL.",
      "invalid_response",
      response.status,
    );
  }
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
