<script setup>
const props = defineProps({
  modelValue: { type: Number, default: 0 },
  readonly: { type: Boolean, default: false },
  max: { type: Number, default: 5 }
})

const emit = defineEmits(['update:modelValue'])

function pick(star) {
  if (props.readonly) return
  emit('update:modelValue', star)
}
</script>

<template>
  <span class="star-rating" :class="{ readonly }">
    <button
      v-for="star in max"
      :key="star"
      type="button"
      class="star"
      :class="{ on: star <= modelValue }"
      :disabled="readonly"
      :aria-label="`${star} dari ${max} bintang`"
      @click="pick(star)"
    >
      <i :class="star <= modelValue ? 'fas fa-star' : 'far fa-star'"></i>
    </button>
  </span>
</template>

<style scoped>
.star-rating {
  display: inline-flex;
  gap: 2px;
  line-height: 1;
}

.star {
  border: none;
  background: transparent;
  padding: 0 1px;
  cursor: pointer;
  font-size: 1.15rem;
  color: #cfc4b4;
  transition: transform 0.1s, color 0.15s;
}

.star.on {
  color: var(--gold, #d4ac0d);
}

.star:not(:disabled):hover {
  transform: scale(1.2);
}

.star-rating.readonly .star {
  cursor: default;
}

.star-rating.readonly .star:hover {
  transform: none;
}

.star-rating.readonly .star {
  font-size: 1rem;
}
</style>
