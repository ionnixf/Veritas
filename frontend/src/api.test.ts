import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, request } from "./api";

afterEach(() => vi.unstubAllGlobals());

function interruptedResponse(error: Error, status = 200) {
  return new Response(
    new ReadableStream({
      start(controller) {
        controller.error(error);
      },
    }),
    { status },
  );
}

describe("API response failures", () => {
  it.each(["/demo/analyze", "/templates/transactions.csv"])(
    "reports an interrupted %s response as a connection failure",
    async (path) => {
      vi.stubGlobal(
        "fetch",
        vi
          .fn()
          .mockResolvedValue(interruptedResponse(new TypeError("terminated"))),
      );
      await expect(request(path)).rejects.toMatchObject({
        code: "connection_error",
        status: 0,
        message: expect.stringContaining("Cannot reach"),
      });
    },
  );

  it("keeps the timeout explanation when the response body times out", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          interruptedResponse(new DOMException("Timed out", "TimeoutError")),
        ),
    );
    await expect(request("/demo/analyze")).rejects.toMatchObject({
      code: "connection_error",
      status: 0,
      message: expect.stringContaining("The request timed out"),
    });
  });

  it("distinguishes malformed JSON from an interrupted response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("<html>")));
    await expect(request("/model")).rejects.toMatchObject({
      code: "invalid_response",
      status: 200,
    });
  });

  it("preserves structured API errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        Response.json(
          {
            error: {
              code: "model_unavailable",
              message: "Model unavailable",
            },
          },
          { status: 503 },
        ),
      ),
    );
    await expect(request("/demo/analyze")).rejects.toEqual(
      new ApiError("Model unavailable", "model_unavailable", 503),
    );
  });

  it("reports an interrupted error body as a connection failure", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          interruptedResponse(new TypeError("terminated"), 503),
        ),
    );
    await expect(request("/demo/analyze")).rejects.toMatchObject({
      code: "connection_error",
      status: 0,
    });
  });

  it("falls back to the HTTP status when an error body is not JSON", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response("Bad Gateway", { status: 502 })),
    );
    await expect(request("/model")).rejects.toMatchObject({
      code: "server_error",
      status: 502,
      message: expect.stringContaining("HTTP 502"),
    });
  });
});
