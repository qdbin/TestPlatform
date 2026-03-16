export const parseSsePayload = (buffer) => {
  let rest = String(buffer || "");
  const events = [];
  let eventEnd = rest.indexOf("\n\n");
  while (eventEnd !== -1) {
    const rawEvent = rest.slice(0, eventEnd);
    rest = rest.slice(eventEnd + 2);
    const dataLines = rawEvent
      .split("\n")
      .filter((line) => !line.startsWith(":"))
      .filter((line) => line.startsWith("data:"))
      .map((line) => line.replace(/^data:\s?/, ""));
    const payload = dataLines.join("\n").trim();
    if (payload && payload !== "[DONE]") {
      try {
        const parsed = JSON.parse(payload);
        if (parsed && typeof parsed === "object") {
          events.push(parsed);
        }
      } catch (e) {
        events.push({ type: "error", message: "SSE事件解析失败" });
      }
    }
    eventEnd = rest.indexOf("\n\n");
  }
  return { events, rest };
};
