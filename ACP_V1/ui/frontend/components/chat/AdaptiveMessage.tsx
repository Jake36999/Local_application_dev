import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import DialecticalView from '../DialecticalView';

interface AdaptiveMessageProps {
  content: string;
}

const AdaptiveMessage: React.FC<AdaptiveMessageProps> = ({ content }) => {
  // Try to detect Dialectical JSON
  const dialecticalData = useMemo(() => {
    try {
      // Accepts either pure JSON or JSON embedded in text
      const jsonMatch = content.match(/\{[\s\S]*"thesis"[\s\S]*"antithesis"[\s\S]*"synthesis"[\s\S]*\}/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        if (parsed.thesis && parsed.antithesis && parsed.synthesis) return parsed;
      }
      return null;
    } catch {
      return null;
    }
  }, [content]);

  if (dialecticalData) {
    return <DialecticalView data={dialecticalData} />;
  }

  return (
    <div className="prose prose-invert max-w-none text-sm">
      <ReactMarkdown
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <SyntaxHighlighter
                style={vscDarkPlus}
                language={match[1]}
                PreTag="div"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default AdaptiveMessage;
