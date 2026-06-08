<template>
  <div :class="['message-wrapper', type]">
    <div class="msg-avatar">{{ avatarEmoji }}</div>
    
    <div class="msg-content">
      <div class="msg-bubble" v-html="formattedText"></div>
      
      <div class="msg-meta">
        <span>{{ formattedTime }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  type: {
    type: String,
    required: true,
    validator: (value) => ['user', 'ai'].includes(value)
  },
  text: {
    type: String,
    required: true
  },
  meta: {
    type: Object,
    default: () => ({})
  },
  timestamp: {
    type: Date,
    default: () => new Date()
  }
});

const avatarEmoji = computed(() => props.type === 'user' ? '👤' : '✨');

const formattedTime = computed(() => {
  return props.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
});

const formattedText = computed(() => {
  if (!props.text) return "";
  
  let formatted = props.text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

  // Bold
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // Italic
  formatted = formatted.replace(/\*(.*?)\*/g, "<em>$1</em>");

  // Code
  formatted = formatted.replace(/`(.*?)`/g, "<code>$1</code>");

  // Line breaks
  formatted = formatted.replace(/\n/g, "<br>");

  // Bullet points
  formatted = formatted.replace(/^[-•]\s(.+)/gm, "<li>$1</li>");
  formatted = formatted.replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>");

  return formatted;
});
</script>
