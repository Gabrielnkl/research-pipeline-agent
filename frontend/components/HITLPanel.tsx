"use client";

import { useState } from "react";
import { submitReview } from "@/lib/api";
import { useRouter } from "next/navigation";

export function HITLPanel({ jobId }: { jobId: string }) {
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handle(action: "approve" | "reject") {
    setLoading(true);

    try {
      await submitReview(jobId, {
        action,
        feedback,
      });

      router.push(`/research/${jobId}`);
    } catch (err) {
      console.error(err);
      alert("Failed to submit review");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Review Required</h2>

      <textarea
        className="w-full p-3 rounded-md border 
                   bg-gray-900 text-white 
                   placeholder-gray-400"
        placeholder="Optional feedback..."
        value={feedback}
        onChange={(e) => setFeedback(e.target.value)}
      />

      <div className="flex gap-2">
        <button
          disabled={loading}
          onClick={() => handle("approve")}
          className="bg-green-600 text-white px-4 py-2 rounded"
        >
          {loading ? "Submitting..." : "Approve & Continue"}
        </button>

        <button
          disabled={loading}
          onClick={() => handle("reject")}
          className="bg-red-600 text-white px-4 py-2 rounded"
        >
          Reject & Refine
        </button>
      </div>
    </div>
  );
}