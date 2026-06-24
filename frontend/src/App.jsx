import React, { useState } from 'react';
import TopicInput from './components/TopicInput';
import AgentActivityLog from './components/AgentActivityLog';
import ReportView from './components/ReportView';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [events, setEvents] = useState([]);
  const [finalReport, setFinalReport] = useState(null);

  const startResearch = async (topic) => {
    setIsLoading(true);
    setEvents([]);
    setFinalReport(null);

    try {
      // Start the research task on the backend
      const response = await fetch('http://localhost:8000/api/research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic }),
      });

      if (!response.ok) {
        throw new Error('Failed to start research');
      }

      // Instead of relying on EventSource which doesn't easily support POST bodies,
      // we can read the streamed response directly. The backend uses sse_starlette
      // which sets text/event-stream. We can parse it.
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      let done = false;

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          // Parse SSE format
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.replace('data: ', '').trim();
              if (dataStr) {
                try {
                  const eventData = JSON.parse(dataStr);
                  
                  if (eventData.status === 'final') {
                    setFinalReport(eventData.data);
                    setIsLoading(false);
                  } else {
                    setEvents(prev => [...prev, eventData]);
                  }
                } catch (err) {
                  console.error('Error parsing event data:', err);
                }
              }
            }
          }
        }
      }
    } catch (error) {
      console.error(error);
      setIsLoading(false);
      // Let the user know it failed
      setEvents(prev => [...prev, {
        agent: 'system',
        status: 'error',
        reasoning: `Error: ${error.message}`
      }]);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>TheResearcher</h1>
        <p>A multi-agent AI research assistant</p>
      </header>
      
      <main className="main-content">
        <aside style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <TopicInput onSubmit={startResearch} isLoading={isLoading} />
          <AgentActivityLog events={events} />
        </aside>
        <section>
          <ReportView report={finalReport} />
        </section>
      </main>
    </div>
  );
}

export default App;
