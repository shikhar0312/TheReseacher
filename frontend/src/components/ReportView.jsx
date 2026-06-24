import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

export default function ReportView({ report }) {
  const [highlightedCitation, setHighlightedCitation] = useState(null);

  if (!report) {
    return (
      <div className="report-view">
        <div className="report-placeholder">
          The final research report will appear here once the team is finished.
        </div>
      </div>
    );
  }

  const { draft, citations } = report;

  const handleCitationClick = (citationId) => {
    setHighlightedCitation(citationId);
    
    // Smooth scroll to the citations section if needed
    const el = document.getElementById(`citation-${citationId}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    // Remove highlight after a few seconds
    setTimeout(() => {
      setHighlightedCitation(null);
    }, 2000);
  };

  // Custom renderer for markdown links or inline markers.
  // We'll use a simple regex to replace [1], [2] in text before passing to markdown,
  // or we can use custom components in ReactMarkdown.
  // Actually, easiest is to let ReactMarkdown parse it, but standard markdown doesn't have a special token for [1].
  // We can just use a simple regex to replace `[1]` with a custom HTML span or link, but ReactMarkdown might escape it.
  // Let's preprocess the draft to replace `[1]` with `[1](#citation-1)` which parses as a link,
  // then we intercept links.

  const processedDraft = draft.replace(/\[(\d+)\]/g, (match, p1) => {
    // If it's a known citation
    if (citations[p1]) {
      return `[${match}](#citation-${p1})`;
    }
    return match;
  });

  return (
    <div className="report-view">
      <div className="report-content">
        <ReactMarkdown
          components={{
            a: ({ node, ...props }) => {
              if (props.href?.startsWith('#citation-')) {
                const id = props.href.replace('#citation-', '');
                return (
                  <a
                    className="citation-link"
                    onClick={(e) => {
                      e.preventDefault();
                      handleCitationClick(id);
                    }}
                    href={props.href}
                  >
                    [{id}]
                  </a>
                );
              }
              // External links open in new tab
              return <a {...props} target="_blank" rel="noopener noreferrer" />;
            }
          }}
        >
          {processedDraft}
        </ReactMarkdown>

        {Object.keys(citations).length > 0 && (
          <div className="sources-section">
            <h3>Sources</h3>
            <ol>
              {Object.entries(citations)
                // sort numerically by key
                .sort(([a], [b]) => parseInt(a) - parseInt(b))
                .map(([id, source]) => (
                <li
                  key={id}
                  id={`citation-${id}`}
                  className={`source-item ${highlightedCitation === id ? 'highlighted-source' : ''}`}
                >
                  <a href={source.url} target="_blank" rel="noopener noreferrer">
                    {source.title || source.url}
                  </a>
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </div>
  );
}
