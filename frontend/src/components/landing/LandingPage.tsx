import React from 'react';
import { Globe, MessageSquare, Zap, CheckCircle, ArrowRight } from 'lucide-react';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#0f1115] text-gray-900 dark:text-gray-100 font-sans transition-colors duration-300">
      {/* Background gradients */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl opacity-50 dark:opacity-20 animate-pulse"></div>
        <div className="absolute top-1/3 -left-20 w-72 h-72 bg-purple-500/20 rounded-full blur-3xl opacity-50 dark:opacity-20"></div>
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-12 md:py-20 flex flex-col gap-24">
        
        {/* Header / Nav */}
        <nav className="flex items-center justify-between w-full">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-purple-600 flex items-center justify-center text-white font-bold shadow-lg">
              P
            </div>
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">
              PolyChat
            </span>
          </div>
          <div className="hidden md:flex gap-8 text-sm font-medium text-gray-600 dark:text-gray-300">
            <a href="#features" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">How it works</a>
            <a href="#pricing" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Pricing</a>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="flex flex-col md:flex-row items-center justify-between gap-12 pt-10">
          <div className="flex flex-col gap-6 max-w-xl">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs font-semibold w-max border border-blue-200 dark:border-blue-800/50">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
              </span>
              v1.0 MVP is now live
            </div>
            
            <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight leading-[1.15]">
              Break Language Barriers with <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">PolyChat</span>
            </h1>
            
            <p className="text-lg text-gray-600 dark:text-gray-400 leading-relaxed">
              An AI-powered multilingual assistant that speaks your customers' language seamlessly. Enhance engagement and support in English, Hindi, Marathi, Tamil, and Punjabi with zero friction.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 mt-4">
              <button className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-medium shadow-lg shadow-blue-500/30 transition-all flex items-center justify-center gap-2">
                Get Started Free <ArrowRight size={18} />
              </button>
              <button className="px-6 py-3 rounded-xl bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-white font-medium shadow-sm border border-gray-200 dark:border-gray-700 transition-all">
                View Documentation
              </button>
            </div>
            
            <div className="flex items-center gap-4 mt-6 text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center gap-1.5">
                <CheckCircle size={16} className="text-green-500" /> No credit card required
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle size={16} className="text-green-500" /> 14-day free trial
              </div>
            </div>
          </div>
          
          <div className="flex-1 w-full max-w-md lg:max-w-none relative hidden md:block">
            <div className="absolute inset-0 bg-gradient-to-tr from-blue-500 to-purple-600 rounded-3xl transform rotate-2 scale-105 opacity-10 dark:opacity-20 blur-xl"></div>
            <div className="relative w-full border border-gray-200 dark:border-gray-800/80 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-3xl shadow-2xl p-8 flex flex-col gap-6">
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></span>
                  Quick Start & Demo Guide
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Follow these simple steps to test PolyChat's multilingual capabilities.
                </p>
              </div>

              <div className="flex flex-col gap-4">
                {/* Step 1 */}
                <div className="flex gap-4 p-4 rounded-2xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700/50 hover:border-blue-500/30 transition-all duration-300">
                  <div className="w-8 h-8 rounded-xl bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold text-sm shrink-0">
                    1
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-gray-800 dark:text-gray-200">Select Your Language</h4>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Click the chat widget button in the bottom-right corner, and select a language from the dropdown menu (e.g., <strong>Hindi (हिंदी)</strong> or <strong>Punjabi (ਪੰਜਾਬੀ)</strong>).
                    </p>
                  </div>
                </div>

                {/* Step 2 */}
                <div className="flex gap-4 p-4 rounded-2xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700/50 hover:border-blue-500/30 transition-all duration-300">
                  <div className="w-8 h-8 rounded-xl bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-400 flex items-center justify-center font-bold text-sm shrink-0">
                    2
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-gray-800 dark:text-gray-200">Ask a Question</h4>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Choose one of the quick suggestions like <em>"What are your pricing plans?"</em> or type any question in your chosen language.
                    </p>
                  </div>
                </div>

                {/* Step 3 */}
                <div className="flex gap-4 p-4 rounded-2xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700/50 hover:border-blue-500/30 transition-all duration-300">
                  <div className="w-8 h-8 rounded-xl bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold text-sm shrink-0">
                    3
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-gray-800 dark:text-gray-200">Instant NLP Response</h4>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Our semantic search pipeline translates, detects intent with confidence mapping, and outputs replies accurately under 500ms.
                    </p>
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-gray-100 dark:border-gray-800 text-center">
                <span className="text-xs text-gray-400 dark:text-gray-500 flex items-center justify-center gap-1.5">
                  <MessageSquare size={14} className="animate-bounce" /> Click the blue bubble in the bottom right corner to start!
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* How it Works / Tutorial */}
        <section id="how-it-works" className="flex flex-col gap-12 pt-10">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold mb-4">How PolyChat Works</h2>
            <p className="text-gray-600 dark:text-gray-400">Deploy an intelligent multilingual support system in three simple steps. We handle the complex NLP magic behind the scenes.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white dark:bg-gray-800/80 backdrop-blur-sm border border-gray-100 dark:border-gray-800 p-8 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 rounded-xl flex items-center justify-center mb-6">
                <Zap size={24} />
              </div>
              <h3 className="text-xl font-bold mb-3">1. One-Click Integration</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                Embed PolyChat into your website with a single line of code. Customize the branding and theme to match your application perfectly.
              </p>
            </div>
            
            <div className="bg-white dark:bg-gray-800/80 backdrop-blur-sm border border-gray-100 dark:border-gray-800 p-8 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-400 rounded-xl flex items-center justify-center mb-6">
                <Globe size={24} />
              </div>
              <h3 className="text-xl font-bold mb-3">2. NLP Language Magic</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                PolyChat automatically detects the language of the user's query and responds intelligently in English, Hindi, Marathi, Tamil, or Punjabi.
              </p>
            </div>
            
            <div className="bg-white dark:bg-gray-800/80 backdrop-blur-sm border border-gray-100 dark:border-gray-800 p-8 rounded-2xl shadow-sm hover:shadow-md transition-shadow relative">
              <div className="absolute top-0 right-0 -mt-2 -mr-2 flex h-4 w-4">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-4 w-4 bg-green-500"></span>
              </div>
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/40 text-green-600 dark:text-green-400 rounded-xl flex items-center justify-center mb-6">
                <MessageSquare size={24} />
              </div>
              <h3 className="text-xl font-bold mb-3">3. Context Aware</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                Our chatbot remembers conversation history to intelligently answer follow-up questions, creating a natural and seamless experience.
              </p>
            </div>
          </div>
        </section>
        
        {/* Footer */}
        <footer className="border-t border-gray-200 dark:border-gray-800 pt-8 pb-12 text-center text-sm text-gray-500">
          <p>© 2026 PolyChat MVP. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default LandingPage;
