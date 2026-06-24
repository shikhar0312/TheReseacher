import React, { useState } from 'react';

export default function TopicInput({ onSubmit, isLoading }) {
  const [topic, setTopic] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (topic.trim() && !isLoading) {
      onSubmit(topic.trim());
    }
  };

  return (
    <div className="topic-input-card">
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <label htmlFor="topic-input">Research Topic</label>
        <input
          id="topic-input"
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g. Latest advancements in solid-state batteries"
          disabled={isLoading}
          required
        />
        <button type="submit" className="btn-primary" disabled={isLoading || !topic.trim()}>
          {isLoading ? 'Researching...' : 'Start Research'}
        </button>
      </form>
    </div>
  );
}
