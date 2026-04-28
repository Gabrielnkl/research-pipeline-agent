"use client";

import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";

export function ReportViewer({ report }: { report: string }) {
  async function copy() {
    await navigator.clipboard.writeText(report);
    alert("Copied!");
  }

  return (
    <div className="space-y-4">
      <button
        onClick={copy}
        className="bg-gray-800 text-white px-3 py-1 rounded"
      >
        Copy as Markdown
      </button>

      <div className="prose max-w-none">
        <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
          {report}
        </ReactMarkdown>
      </div>
    </div>
  );
}