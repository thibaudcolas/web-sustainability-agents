import { co2 } from "@tgwf/co2";

const estimator = new co2({ model: "swd", version: 4, rating: true });

export function rateCapture(capture) {
  const bytes = capture.receivedBytes;
  const eligible =
    capture.complete &&
    capture.cache === "cold" &&
    Number.isFinite(bytes) &&
    bytes > 0;
  const profile = {
    library: "@tgwf/co2@0.19.0",
    model: "swd",
    version: 4,
    functionalUnit: "one sampled cold page load",
    hosting: "unknown; assume non-green for this scenario",
    firstVisitPercentage: 1,
    returnVisitPercentage: 0,
    dataReloadRatio: 0.02,
    comparisonStatus: "provisional; capture protocol not externally validated",
  };
  if (!eligible)
    return {
      status: "not_calculated",
      reason: "Requires a complete, positive-byte cold capture",
      profile,
    };
  return {
    status: "calculated",
    bytes,
    profile,
    trace: estimator.perVisitTrace(bytes, false, {
      firstVisitPercentage: 1,
      returnVisitPercentage: 0,
      dataReloadRatio: 0.02,
    }),
  };
}
