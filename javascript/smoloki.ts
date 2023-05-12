const axios = require("axios");

// constants
const SMOLOKI_BASE_ENDPOINT = process.env.SMOLOKI_BASE_ENDPOINT ?? "";

const SMOLOKI_BASE_LABELS_RAW = process.env.SMOLOKI_BASE_LABELS ?? "{}";
const SMOLOKI_BASE_LABELS = JSON.parse(SMOLOKI_BASE_LABELS_RAW);

const SMOLOKI_BASE_INFORMATION_RAW = process.env.SMOLOKI_BASE_INFORMATION ?? "{}";
const SMOLOKI_BASE_INFORMATION = JSON.parse(SMOLOKI_BASE_INFORMATION_RAW);

// polyfills and helpers
function containsAny(value: string, targets: string[]): boolean {
  for (const target of targets) {
    if (value.includes(target)) {
      return true;
    }
  }
  return false;
}

// utility functions
function _logfmtEscape(value: string): string {
  value = value.replace(/\\/g, "\\\\");
  value = value.replace(/"/g, '\\"');
  value = value.replace(/\n/g, "\\n");
  if (containsAny(value, [" ", "=", '"'])) {
    return `"${value}"`;
  }
  return value;
}

function _logfmtUnescape(value: string): string {
  if (value.match(/^"(.+)"$/) != null) {
    value = value.substring(1, value.length - 1);
  }
  value = value.replace(/\\n/g, "\n");
  value = value.replace(/\\"/g, '"');
  value = value.replace(/\\\\/g, "\\");
  return value;
}

const LOGFMT_PAIR_REGEX =
  /(?<key>\w+)=(?:(?<rvalue>[^"][^ \n]*)|"(?<qvalue>(?:\\.|[^"])*)")/g;

function logfmtLoad(data: string): any {
  const result = {};

  for (const match of data.matchAll(LOGFMT_PAIR_REGEX)) {
    const key = match[1];
    const value = match[2] ?? match[3];
    result[key] = _logfmtUnescape(value);
  }

  return result;
}

function logfmtDump(data: any): string {
  const items: string[] = [];

  for (const [key, value] of Object.entries(data)) {
    if (typeof key !== "string") {
      throw new Error("Make sure keys are strings");
    }

    if (key.match(/^[A-Z_][A-Za-z0-9_]*$/) != null) {
      throw new Error("Make sure keys are valid identifiers");
    }

    if (typeof value !== "string" && typeof value !== "number") {
      throw new Error("Make sure values are strings or numbers");
    }

    items.push(`${key}=${_logfmtEscape(value.toString())}`);
  }

  return items.join(" ");
}

// networking
async function push(
  labels: any,
  information: any,
  baseEndpoint: string | null = null
): Promise<void> {
  const targetBaseEndpoint = baseEndpoint ?? SMOLOKI_BASE_ENDPOINT;

  if (targetBaseEndpoint === "") {
    console.warn("No 'base_endpoint' configured for smoloki");
    return;
  }

  const targetEndpoint =
    targetBaseEndpoint.replace(/\/$/, "") + "/loki/api/v1/push";

  try {
    await axios.post(targetEndpoint, {
      streams: [
        {
          stream: { ...SMOLOKI_BASE_LABELS, ...labels },
          values: [
            [
              `${Date.now() * 1000000}`,
              logfmtDump({ ...SMOLOKI_BASE_INFORMATION, ...information }),
            ],
          ],
        },
      ],
    });
  } catch (error) {
    console.trace("Error while sending logs with smoloki:");
  }
}

// exports
module.exports = {
  logfmtDump,
  logfmtLoad,
  _logfmtEscape,
  _logfmtUnescape,
  push,
};
