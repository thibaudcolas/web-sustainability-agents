import { mkdir, writeFile } from "node:fs/promises";

if (!process.env.NEURALWATT_API_KEY)
  throw new Error("NEURALWATT_API_KEY is required");
const payload = {
  model: "deepseek-v4.1-flash",
  reasoning_effort: "low",
  max_tokens: 512,
  messages: [
    {
      role: "user",
      content:
        "Call record_status with status ready. This is an API tool compatibility preflight.",
    },
  ],
  tools: [
    {
      type: "function",
      function: {
        name: "record_status",
        description: "Record preflight status",
        parameters: {
          type: "object",
          properties: { status: { type: "string", enum: ["ready"] } },
          required: ["status"],
          additionalProperties: false,
        },
      },
    },
  ],
  tool_choice: { type: "function", function: { name: "record_status" } },
};
const response = await fetch("https://api.neuralwatt.com/v1/chat/completions", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${process.env.NEURALWATT_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify(payload),
  signal: AbortSignal.timeout(60000),
});
const body = await response.json();
const result = {
  date: new Date().toISOString(),
  status: response.status,
  requestedModel: payload.model,
  reasoningEffort: payload.reasoning_effort,
  response: body,
};
await mkdir(".audit-work", { recursive: true });
await writeFile(
  ".audit-work/neuralwatt-preflight.json",
  JSON.stringify(result, null, 2) + "\n",
  { mode: 0o600 },
);
const call = body.choices?.[0]?.message?.tool_calls?.[0];
if (
  !response.ok ||
  call?.function?.name !== "record_status" ||
  JSON.parse(call.function.arguments).status !== "ready"
)
  throw new Error(
    `Preflight failed (HTTP ${response.status}); inspect private result`,
  );
console.log(
  `Neuralwatt tool-call preflight passed; served model ${body.model}; usage recorded locally`,
);
