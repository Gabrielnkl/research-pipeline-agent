"use client";

import { useState } from "react";
import { startResearch } from "@/lib/api";
import { useRouter } from "next/navigation";

const EXAMPLES = [
  "What are the main causes of inflation in 2024?",
  "How is AI impacting the job market in 2025?",
  "What are the economic effects of high interest rates?",
  "How do supply chain disruptions affect global trade?"
];

export function ResearchForm() {
  const [question, setQuestion] = useState("");
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault(); // ✅ VERY IMPORTANT

    if (!question.trim()) return;

    try {
      const res = await startResearch(question);
      router.push(`/research/${res.id}`);
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a research question..."
        className="w-full p-3 rounded-md border 
                   bg-gray-900 text-white 
                   placeholder-gray-400"
      />

      {/* Examples */}
      <div className="space-y-2">
        <p className="text-sm text-gray-400">Try an example:</p>

        <div className="flex flex-wrap gap-2">
          {EXAMPLES.map((example, idx) => (
            <button
              key={idx}
              type="button" // ✅ IMPORTANT (prevents form submit)
              onClick={() => setQuestion(example)}
              className="px-3 py-1 rounded-full text-sm
                         bg-gray-800 text-white
                         hover:bg-gray-700"
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit" // ✅ MUST be submit
        className="px-4 py-2 bg-blue-600 rounded-md text-white"
      >
        Start Research
      </button>
    </form>
  );
}