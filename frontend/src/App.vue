<template>
  <!-- Animated Gradient Orbs Background -->
  <div class="animated-bg"></div>

  <div class="app-container">
    <div class="glass-app">
      <!-- Header -->
      <header class="header">
          <div class="logo-section">
              <div class="avatar-ring">
                  <div class="pulse-ring"></div>
                  <div class="avatar">A</div>
              </div>
              <div>
                  <h1 class="app-title">Akram<span class="title-highlight">AI</span></h1>
                  <p class="app-subtitle">
                      <span class="status-dot"></span>
                      Premium Knowledge Assistant
                  </p>
              </div>
          </div>
      </header>

      <!-- Chat Area -->
      <main class="chat-area" ref="chatArea">
          <!-- Welcome Section -->
          <div class="welcome-section" v-if="messages.length === 0">
              <div class="welcome-icon">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.5">
                      <path d="M12 2a10 10 0 0 1 10 10c0 5.52-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2z"/>
                      <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
                      <line x1="9" y1="9" x2="9.01" y2="9"/>
                      <line x1="15" y1="9" x2="15.01" y2="9"/>
                  </svg>
              </div>
              <h2 class="welcome-title">How can I help you?</h2>
              <p class="welcome-desc">I am trained on Akram Ali Faridi's complete background. Feel free to ask about his education, experience, or specialized skills.</p>
              
              <div class="suggestions-grid">
                  <button class="suggestion-btn" @click="askSuggestion('What is Akram\'s educational background?')">
                      <span class="suggestion-icon">🎓</span>
                      What is Akram's educational background?
                  </button>
                  <button class="suggestion-btn" @click="askSuggestion('What programming skills does Akram have?')">
                      <span class="suggestion-icon">💻</span>
                      What programming skills does Akram have?
                  </button>
                  <button class="suggestion-btn" @click="askSuggestion('Tell me about Akram\'s projects')">
                      <span class="suggestion-icon">🚀</span>
                      Tell me about Akram's projects
                  </button>
                  <button class="suggestion-btn" @click="askSuggestion('Who is Akram Ali Faridi?')">
                      <span class="suggestion-icon">👤</span>
                      Who is Akram Ali Faridi?
                  </button>
              </div>
          </div>

          <!-- Messages Container -->
          <div class="messages-container">
              <ChatMessage 
                  v-for="(msg, index) in messages" 
                  :key="index"
                  :type="msg.type"
                  :text="msg.text"
                  :meta="msg.meta"
                  :timestamp="msg.timestamp"
              />
              
              <!-- Elegant Typing Indicator -->
              <div class="message-wrapper ai" v-if="isLoading">
                  <div class="msg-avatar">✨</div>
                  <div class="msg-content">
                      <div class="msg-bubble">
                          <div class="typing-dots">
                              <div class="dot"></div>
                              <div class="dot"></div>
                              <div class="dot"></div>
                          </div>
                      </div>
                  </div>
              </div>
          </div>
      </main>

      <!-- Input Area -->
      <footer class="input-area">
          <div class="input-wrapper">
              <textarea 
                  v-model="questionInput"
                  placeholder="Ask me anything..." 
                  rows="1"
                  maxlength="1000"
                  @input="autoResize"
                  @keydown.enter.exact.prevent="sendMessage"
                  ref="textarea"
              ></textarea>
              <button class="send-btn" :disabled="isLoading" @click="sendMessage">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <line x1="22" y1="2" x2="11" y2="13"/>
                      <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                  </svg>
              </button>
          </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import ChatMessage from './components/ChatMessage.vue';

// State
const messages = ref([]);
const questionInput = ref('');
const isLoading = ref(false);
const gpuText = ref('Checking...');

// Template refs
const chatArea = ref(null);
const textarea = ref(null);

const API_BASE = '/api';

const checkHealth = async () => {
    try {
        const res = await fetch(`${API_BASE}/health`);
        const data = await res.json();
        gpuText.value = data.gpu === "cuda" ? "RTX 5060" : "CPU Compute";
    } catch (err) {
        gpuText.value = "Offline";
    }
};

const autoResize = () => {
    if (!textarea.value) return;
    textarea.value.style.height = "auto";
    textarea.value.style.height = Math.min(textarea.value.scrollHeight, 150) + "px";
};

const scrollToBottom = () => {
    nextTick(() => {
        if (chatArea.value) {
            chatArea.value.scrollTop = chatArea.value.scrollHeight;
        }
    });
};

const askSuggestion = (question) => {
    questionInput.value = question;
    sendMessage();
};

const sendMessage = async () => {
    const question = questionInput.value.trim();
    if (!question || isLoading.value) return;

    isLoading.value = true;

    // Add user message
    messages.value.push({
        type: 'user',
        text: question,
        timestamp: new Date()
    });
    
    questionInput.value = "";
    autoResize();
    scrollToBottom();

    try {
        const res = await fetch(`${API_BASE}/ask`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        });

        const data = await res.json();

        if (data.error) {
            messages.value.push({
                type: 'ai',
                text: "An error occurred: " + data.error,
                timestamp: new Date(),
                meta: { isError: true }
            });
        } else {
            messages.value.push({
                type: 'ai',
                text: data.answer,
                timestamp: new Date(),
                meta: {
                    confidence: data.confidence,
                    responseTime: data.response_time,
                    model: data.model
                }
            });
        }
    } catch (err) {
        messages.value.push({
            type: 'ai',
            text: "Unable to connect to the server. Please check your connection.",
            timestamp: new Date(),
            meta: { isError: true }
        });
    } finally {
        isLoading.value = false;
        scrollToBottom();
        nextTick(() => {
            textarea.value?.focus();
        });
    }
};

onMounted(() => {
    checkHealth();
    textarea.value?.focus();
});
</script>
