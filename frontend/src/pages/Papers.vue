<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'

const items = ref([])
const err = ref('')
const drafts = ref({})
const saving = ref({})
const rowErr = ref({})

onMounted(load)

async function load() {
  err.value = ''
  try {
    items.value = (await getJSON('/api/papers')).items
    drafts.value = Object.fromEntries(items.value.map((p) => [p.id, String(p.roll_width)]))
  } catch (e) {
    err.value = String(e.message || e)
  }
}

async function save(p) {
  rowErr.value[p.id] = ''
  const v = Number(drafts.value[p.id])
  if (!Number.isFinite(v) || v <= 0) {
    rowErr.value[p.id] = '卷宽须为正数，已拒绝保存'
    drafts.value[p.id] = String(p.roll_width)
    return
  }
  saving.value[p.id] = true
  try {
    const updated = await putJSON(`/api/papers/${p.id}`, { roll_width: v })
    const i = items.value.findIndex((x) => x.id === p.id)
    if (i >= 0) items.value[i] = updated
    drafts.value[p.id] = String(updated.roll_width)
  } catch (e) {
    rowErr.value[p.id] = String(e.message || e)
  } finally {
    saving.value[p.id] = false
  }
}
</script>

<template>
  <div class="page">
    <h1>包装纸</h1>
    <p class="lede">卷宽当场生效：保存后算纸台选用该纸即按新卷宽折张；已写入用纸档的旧单仍钉住写入时卷宽。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-else class="paper-grid">
      <div v-for="p in items" :key="p.id" class="paper-tile">
        <strong>{{ p.name }}</strong>
        <div class="row" style="margin-bottom: 0.4rem">
          <label class="meta" :for="'rw-' + p.id">卷宽</label>
          <input
            :id="'rw-' + p.id"
            v-model="drafts[p.id]"
            type="number"
            min="0"
            step="0.01"
            style="width: 6.5rem; padding: 0.35rem 0.5rem; border: 1px solid var(--line); border-radius: var(--radius)"
          />
          <span class="meta">m</span>
          <button :disabled="saving[p.id]" @click="save(p)">保存</button>
        </div>
        <p v-if="rowErr[p.id]" class="bad" style="margin: 0.2rem 0 0; font-size: 0.85rem">{{ rowErr[p.id] }}</p>
      </div>
    </div>
  </div>
</template>
