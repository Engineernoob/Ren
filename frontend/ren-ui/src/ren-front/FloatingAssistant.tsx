'use client'

import React, { useState, useRef} from 'react'
import { Mic, MicOff, Volume2, MessageCircle, X, History} from 'lucide-react'

type AssistantState = 'idle' | 'listening' | 'speaking' | 'thinking'

interface FloatingAssistantProps {
  variant?: 'default' | 'minimal' | 'premium'
  state?: AssistantState
  isExpanded?: boolean
  onStateChange?: (state: AssistantState) => void
  onToggleExpanded?: () => void
}

export function FloatingAssistant({ 
  variant = 'default', 
  state = 'idle',
  isExpanded = false,
  onStateChange,
  onToggleExpanded 
}: FloatingAssistantProps) {
  const [inputValue, setInputValue] = useState('')
  const [isVoiceOnly, setIsVoiceOnly] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I\'m Ren, your AI assistant. How can I help you today?' },
    { role: 'user', content: 'What\'s the weather like?' },
    { role: 'assistant', content: 'I\'d be happy to help with the weather! However, I don\'t have access to real-time weather data. You can check your local weather app or ask me something else.' }
  ])
  const inputRef = useRef<HTMLInputElement>(null)

  const handleToggleListening = () => {
    const newState = state === 'listening' ? 'idle' : 'listening'
    onStateChange?.(newState)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim()) {
      setMessages(prev => [...prev, { role: 'user', content: inputValue }])
      setInputValue('')
      onStateChange?.('thinking')
      
      // Simulate AI response
      setTimeout(() => {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: 'I understand your request. Let me help you with that...' 
        }])
        onStateChange?.('idle')
      }, 2000)
    }
  }

  const getStateIndicator = () => {
    switch (state) {
      case 'listening':
        return { text: 'Listening...', color: 'text-blue-400', pulse: true }
      case 'speaking':
        return { text: 'Speaking...', color: 'text-green-400', pulse: true }
      case 'thinking':
        return { text: 'Thinking...', color: 'text-amber-400', pulse: true }
      default:
        return { text: 'Ready', color: 'text-slate-400', pulse: false }
    }
  }

  const stateIndicator = getStateIndicator()

  // Variant-specific styles
  const getVariantStyles = () => {
    switch (variant) {
      case 'minimal':
        return {
          container: 'bg-white/10 border-white/20',
          input: 'bg-white/5 border-white/10',
          button: 'bg-white/10 hover:bg-white/20'
        }
      case 'premium':
        return {
          container: 'bg-slate-900/40 border-slate-700/30',
          input: 'bg-slate-800/30 border-slate-600/20',
          button: 'bg-slate-700/30 hover:bg-slate-600/40'
        }
      default:
        return {
          container: 'bg-white/20 border-white/30',
          input: 'bg-white/10 border-white/20',
          button: 'bg-white/20 hover:bg-white/30'
        }
    }
  }

  const styles = getVariantStyles()

  return (
    <div className="fixed top-8 left-1/2 transform -translate-x-1/2 z-50">
      {/* Main floating bar */}
      <div 
        className={`
          relative backdrop-blur-xl ${styles.container}
          border rounded-3xl shadow-2xl transition-all duration-500 ease-out
          ${isExpanded ? 'w-96' : 'w-80'}
          ${variant === 'premium' ? 'shadow-slate-900/20' : 'shadow-black/10'}
        `}
      >
        {/* Main content */}
        <div className="p-4">
          {/* Header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${stateIndicator.pulse ? 'animate-pulse' : ''} ${stateIndicator.color === 'text-blue-400' ? 'bg-blue-400' : stateIndicator.color === 'text-green-400' ? 'bg-green-400' : stateIndicator.color === 'text-amber-400' ? 'bg-amber-400' : 'bg-slate-400'}`} />
              <span className={`text-sm ${stateIndicator.color}`}>
                {stateIndicator.text}
              </span>
            </div>
            <div className="flex items-center space-x-1">
              <button
                onClick={onToggleExpanded}
                className={`p-1.5 rounded-lg ${styles.button} transition-all duration-200 text-white/70 hover:text-white`}
              >
                {isExpanded ? <X className="w-4 h-4" /> : <History className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Input area */}
          {!isVoiceOnly && (
            <form onSubmit={handleSubmit} className="mb-3">
              <div className="relative">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Ask Ren anything..."
                  className={`
                    w-full px-4 py-2.5 ${styles.input}
                    border rounded-2xl transition-all duration-200
                    placeholder-white/50 text-white bg-transparent
                    focus:outline-none focus:ring-2 focus:ring-blue-400/50 focus:border-blue-400/50
                  `}
                  disabled={state === 'thinking'}
                />
                {state === 'thinking' && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <div className="w-4 h-4 border-2 border-white/20 border-t-white/60 rounded-full animate-spin" />
                  </div>
                )}
              </div>
            </form>
          )}

          {/* Controls */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <button
                onClick={handleToggleListening}
                className={`
                  p-2.5 rounded-xl transition-all duration-200
                  ${state === 'listening' 
                    ? 'bg-blue-500/80 text-white shadow-lg shadow-blue-500/25' 
                    : `${styles.button} text-white/70 hover:text-white`
                  }
                `}
              >
                {state === 'listening' ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
              </button>
              
              <button
                onClick={() => setIsVoiceOnly(!isVoiceOnly)}
                className={`p-2.5 rounded-xl ${styles.button} transition-all duration-200 text-white/70 hover:text-white`}
              >
                <MessageCircle className="w-4 h-4" />
              </button>
            </div>

            <button
              className={`p-2.5 rounded-xl ${styles.button} transition-all duration-200 text-white/70 hover:text-white`}
            >
              <Volume2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Expanded content */}
        {isExpanded && (
          <div className="border-t border-white/20 p-4 max-h-64 overflow-y-auto">
            <div className="space-y-3">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`text-sm ${
                    message.role === 'user' 
                      ? 'text-right text-white/90' 
                      : 'text-left text-white/70'
                  }`}
                >
                  <div
                    className={`inline-block px-3 py-2 rounded-xl max-w-[80%] ${
                      message.role === 'user'
                        ? 'bg-blue-500/20 border border-blue-400/30'
                        : 'bg-white/10 border border-white/20'
                    }`}
                  >
                    {message.content}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Voice-only mode overlay */}
      {isVoiceOnly && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className={`w-16 h-16 rounded-full ${styles.container} border flex items-center justify-center mb-2`}>
              <Mic className="w-8 h-8 text-white/80" />
            </div>
            <p className="text-white/60 text-sm">Voice mode active</p>
          </div>
        </div>
      )}
    </div>
  )
}