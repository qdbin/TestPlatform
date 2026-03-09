import { describe, it, expect } from "vitest";
import { parseSsePayload } from "../../src/views/aiAssistant/utils/sse";

describe("aiAssistant sse parser", () => {
  it("should parse multiple complete events", () => {
    const source =
      'data: {"type":"content","delta":"A"}\n\n' +
      'data: {"type":"content","delta":"B"}\n\n' +
      'data: {"type":"end"}\n\n';
    const parsed = parseSsePayload(source);
    expect(parsed.events.length).toBe(3);
    expect(parsed.events[0].delta).toBe("A");
    expect(parsed.events[1].delta).toBe("B");
    expect(parsed.events[2].type).toBe("end");
    expect(parsed.rest).toBe("");
  });

  it("should keep incomplete frame in rest buffer", () => {
    const source =
      'data: {"type":"content","delta":"A"}\n\n' +
      'data: {"type":"content","delta":"INCOMPLETE"}';
    const parsed = parseSsePayload(source);
    expect(parsed.events.length).toBe(1);
    expect(parsed.events[0].delta).toBe("A");
    expect(parsed.rest).toContain("INCOMPLETE");
  });
});
