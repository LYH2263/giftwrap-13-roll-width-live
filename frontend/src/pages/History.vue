<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const items = ref([])
const err = ref('')

onMounted(async () => {
  try {
    items.value = (await getJSON('/api/runs')).items
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <h1>用纸档</h1>
    <p class="lede">算纸页「写入用纸档」后的落库结果。卷宽与折张按写入时快照钉住，之后改卷宽不动旧单；点单可复算互证。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-else-if="!items.length" class="empty">还没有写入过。先去算纸试一单。</p>
    <ul v-else class="item-list">
      <li v-for="r in items" :key="r.id">
        <router-link :to="`/runs/${r.id}`">{{ r.box_name }}</router-link>
        <span class="meta">
          {{ r.result?.paper_m2 ?? '—' }} m² ·
          卷宽 {{ r.roll_width ?? '—' }} m ·
          {{ r.sheets ?? '—' }} 张
        </span>
      </li>
    </ul>
  </div>
</template>
