<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Cari produk…' }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const router = useRouter()
const suggestions = ref([])
const show = ref(false)
const active = ref(-1)
const keyword = ref(props.modelValue)
let timer = null

watch(
  () => props.modelValue,
  (v) => {
    keyword.value = v
  }
)

watch(keyword, (v) => {
  emit('update:modelValue', v)
  clearTimeout(timer)
  const q = v.trim()
  if (!q) {
    suggestions.value = []
    show.value = false
    return
  }
  timer = setTimeout(async () => {
    try {
      const { data } = await api.get('/products/suggest', { params: { q, limit: 6 } })
      suggestions.value = data
      show.value = true
      active.value = -1
    } catch {
      suggestions.value = []
    }
  }, 250)
})

onBeforeUnmount(() => clearTimeout(timer))

function onEnter() {
  if (active.value >= 0 && suggestions.value[active.value]) {
    goTo(suggestions.value[active.value])
    return
  }
  emit('submit')
}

function onKeydown(e) {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    active.value = Math.min(active.value + 1, suggestions.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    active.value = Math.max(active.value - 1, -1)
  } else if (e.key === 'Escape') {
    show.value = false
  }
}

function goTo(s) {
  show.value = false
  keyword.value = ''
  router.push({ name: 'product-detail', params: { slug: s.slug } })
}

function hide() {
  setTimeout(() => {
    show.value = false
  }, 120)
}

function fmt(v) {
  return Number(v).toLocaleString('id-ID')
}
</script>

<template>
  <div class="suggest-wrap">
    <input
      v-model="keyword"
      type="text"
      :placeholder="placeholder"
      autocomplete="off"
      role="combobox"
      aria-expanded="show"
      @keydown="onKeydown"
      @keyup.enter="onEnter"
      @focus="show = suggestions.length > 0"
      @blur="hide"
    />
    <ul v-if="show && suggestions.length" class="suggest-list">
      <li
        v-for="(s, i) in suggestions"
        :key="s.id"
        :class="{ active: i === active }"
        @mousedown.prevent="goTo(s)"
        @mouseenter="active = i"
      >
        <img v-if="s.image" :src="s.image" :alt="s.name" class="suggest-thumb" />
        <div class="suggest-info">
          <span class="suggest-name">{{ s.name }}</span>
          <span class="suggest-meta">{{ s.store_name }} · {{ s.sold }} terjual</span>
        </div>
        <span class="suggest-price">Rp {{ fmt(s.price) }}</span>
      </li>
    </ul>
    <p v-else-if="show && keyword.trim() && !suggestions.length" class="suggest-empty">
      Tidak ada saran produk serupa
    </p>
  </div>
</template>

<style scoped>
.suggest-wrap {
  position: relative;
  flex: 1;
  min-width: 0;
}

.suggest-wrap input {
  width: 100%;
}

.suggest-list {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  z-index: 60;
  list-style: none;
  margin: 0;
  padding: 6px;
  background: #fffdf9;
  border: 1px solid #e8ddcd;
  border-radius: 14px;
  box-shadow: 0 12px 34px rgba(60, 30, 10, 0.22);
  max-height: 320px;
  overflow: auto;
}

html.dark .suggest-list {
  background: #241f1b;
  border-color: #3a2f26;
}

.suggest-list li {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.5rem 0.6rem;
  border-radius: 10px;
  cursor: pointer;
}

.suggest-list li.active,
.suggest-list li:hover {
  background: var(--cream);
}

.suggest-thumb {
  width: 44px;
  height: 44px;
  object-fit: cover;
  border-radius: 8px;
  flex: none;
  background: #f0e8dc;
}

html.dark .suggest-thumb {
  background: #3a2f26;
}

.suggest-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.suggest-name {
  color: var(--brown);
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.suggest-meta {
  font-size: 0.78rem;
  color: #9a9188;
}

.suggest-price {
  color: var(--maroon);
  font-weight: 700;
  font-size: 0.9rem;
  white-space: nowrap;
}

.suggest-empty {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  z-index: 60;
  margin: 0;
  padding: 0.6rem 0.9rem;
  background: #fffdf9;
  border: 1px solid #e8ddcd;
  border-radius: 12px;
  font-size: 0.85rem;
  color: #9a9188;
  box-shadow: 0 12px 34px rgba(60, 30, 10, 0.22);
}

html.dark .suggest-empty {
  background: #241f1b;
  border-color: #3a2f26;
  color: #b6aca0;
}
</style>
