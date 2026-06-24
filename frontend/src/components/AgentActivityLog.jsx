import React, { useEffect, useRef } from 'react';

export default function AgentActivityLog({ events }) {
  const listRef = useRef(null);

  // Auto-scroll to bottom when new events arrive
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [events]);

  return (
    <div className="activity-log">
      <div className="activity-header">
        Live Agent Activity
      </div>
      <div className="activity-list" ref={listRef}>
        {events.length === 0 ? (
          <div style={{ color: 'var(--text-secondary)', textAlign: 'center', marginTop: '2rem' }}>
            Awaiting topic submission...
          </div>
        ) : (
          events.map((evt, idx) => (
            <div key={idx} className={`activity-item ${evt.agent.toLowerCase()}`}>
              <div className="agent-name">
                {evt.agent === 'system' ? 'System' : evt.agent + ' Agent'} 
                {evt.status === 'completed' && ' ✓'}
              </div>
              
              {/* Data payload display based on agent type */}
              {evt.agent === 'researcher' && evt.data?.new_findings !== undefined && (
                <div style={{ fontSize: '0.85rem', marginBottom: '0.5rem' }}>
                  Found {evt.data.new_findings} new sources.
                </div>
              )}
              {evt.agent === 'writer' && evt.data?.draft_length !== undefined && (
                <div style={{ fontSize: '0.85rem', marginBottom: '0.5rem' }}>
                  Drafted {evt.data.draft_length} characters.
                </div>
              )}
              {evt.agent === 'critic' && evt.data?.critique && (
                <div style={{ fontSize: '0.85rem', marginBottom: '0.5rem' }}>
                  <strong>Critique:</strong> {evt.data.critique.substring(0, 100)}...
                </div>
              )}

              {/* Reasoning from the supervisor or LLM node */}
              {evt.reasoning && (
                <div className="reasoning">
                  <strong>Reasoning:</strong> {evt.reasoning}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
