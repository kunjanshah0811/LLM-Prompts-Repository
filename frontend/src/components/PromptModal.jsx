import { useState, useEffect } from 'react';

const PromptModal = ({ prompt, onClose }) => {
  const [copied, setCopied] = useState(false);

  // Prevent body scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  // Separate prompt from example/sample output
  const separatePromptAndExample = (text) => {
    if (!text) return { prompt: '', example: null };
    
    // First check for explicit ---EXAMPLE--- marker
    if (text.includes('---EXAMPLE---')) {
      const parts = text.split('---EXAMPLE---');
      return {
        prompt: parts[0].trim(),
        example: parts.length > 1 ? parts[1].trim() : null
      };
    }

    // Fallback: look for common example markers
    const markers = [
      'Example:',
      'Example Output:',
      'Sample Output:',
      'Sample Expected Output:',
      'Example Input:',
      'Sample Answer:',
      'Example Analysis:',
      'Example Classification:',
      'Sample Example:'
    ];

    // Find the first occurrence of any marker
    let splitIndex = -1;
    let foundMarker = '';
    
    for (const marker of markers) {
      const regex = new RegExp(`\\n${marker}`, 'i');
      const match = text.match(regex);
      if (match && (splitIndex === -1 || match.index < splitIndex)) {
        splitIndex = match.index;
        foundMarker = match[0];
      }
    }

    if (splitIndex !== -1) {
      return {
        prompt: text.substring(0, splitIndex).trim(),
        example: text.substring(splitIndex).trim()
      };
    }

    // No example found, return all as prompt
    return {
      prompt: text.trim(),
      example: null
    };
  };

  const handleCopy = async () => {
    try {
      // Only copy the prompt part, not the example
      await navigator.clipboard.writeText(promptText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // // Separate prompt from example using ---EXAMPLE--- marker
  // const separatePromptAndExample = (text) => {
  //   if (!text) return { prompt: '', example: '' };
    
  //   const parts = text.split('---EXAMPLE---');
  //   return {
  //     prompt: parts[0].trim(),
  //     example: parts.length > 1 ? parts[1].trim() : ''
  //   };
  // };

  // Parse hierarchical category
  const parseCategory = (category) => {
    if (category && category.includes(' > ')) {
      const [mainCat, subCat] = category.split(' > ');
      return { main: mainCat, sub: subCat };
    }
    return { main: null, sub: category };
  };

  const { main: mainCategory, sub: subCategory } = parseCategory(prompt.category);
  const { prompt: promptText, example: exampleText } = separatePromptAndExample(prompt.prompt_text);

  if (!prompt) return null;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {prompt.title}
            </h2>
            <div className="flex flex-wrap gap-2 items-center">
              {mainCategory && (
                <span className="inline-block px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm font-medium">
                  {mainCategory}
                </span>
              )}
              <span className="inline-block px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                {subCategory}
              </span>
              {prompt.source && (
                <span className="text-sm text-gray-600">
                  📚 Source: {prompt.source}
                </span>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="ml-4 text-gray-400 hover:text-gray-600 transition-colors"
            title="Close"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Prompt Text */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-gray-900">Prompt</h3>
              <button
                onClick={handleCopy}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  copied 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-primary-100 text-primary-700 hover:bg-primary-200'
                }`}
              >
                {copied ? '✓ Copied Prompt!' : '📋 Copy Prompt'}
              </button>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <pre className="whitespace-pre-wrap font-mono text-sm text-gray-800 leading-relaxed">
                {promptText}
              </pre>
            </div>
          </div>

          {/* Example/Sample Output (if exists) */}
          {exampleText && (
            <div className="mb-6">
              <div className="flex items-center mb-3">
                <h3 className="text-lg font-semibold text-gray-900">Example / Sample Output</h3>
              </div>
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <pre className="whitespace-pre-wrap font-mono text-sm text-blue-900 leading-relaxed">
                  {exampleText}
                </pre>
              </div>
              <p className="mt-2 text-xs text-gray-500 italic">
                💡 The copy button above copies only the prompt, not this example section
              </p>
            </div>
          )}

          {/* Tags */}
          {prompt.tags && prompt.tags.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {prompt.tags.map((tag, index) => (
                  <span 
                    key={index}
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
            <div>
              <span className="text-sm text-gray-600">Views</span>
              <p className="text-lg font-semibold text-gray-900">
                👁️ {prompt.views}
              </p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Added</span>
              <p className="text-lg font-semibold text-gray-900">
                {new Date(prompt.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              💡 Tip: Use variables like {'{variable_name}'} in your prompts for reusability
            </p>
            <button
              onClick={onClose}
              className="btn-secondary"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PromptModal;