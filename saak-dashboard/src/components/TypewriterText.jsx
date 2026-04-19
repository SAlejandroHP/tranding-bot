import React, { useState, useEffect } from 'react';

export const TypewriterText = ({ text }) => {
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    setDisplayedText('');
    if (!text) return;
    
    const chars = Array.from(text);
    let i = 0;
    
    const intervalId = setInterval(() => {
      i++;
      setDisplayedText(chars.slice(0, i).join(''));
      if (i >= chars.length) {
        clearInterval(intervalId);
      }
    }, 15);
    
    return () => clearInterval(intervalId);
  }, [text]);

  return <>{displayedText}<span className="cursor-blink">_</span></>;
};

export default TypewriterText;
