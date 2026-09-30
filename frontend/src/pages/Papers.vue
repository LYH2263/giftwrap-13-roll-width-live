<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'

const items = ref([])
const selectedId = ref('')
const drafts = ref({})
const errs = ref({})
const savingId = ref(null)
const selectingId = ref(null)
const err = ref('')

onMounted(load)

async function load() {
  err.value = ''
  try {
    const [papers, settings] = await Promise.all([getJSON('/api/papers'), getJSON('/api/settings')])
    items.value = papers.items
    selectedId.value = String(settings.selected_paper_id ?? '')
    drafts.value = Object.fromEntries(papers.items.map((p) => [p.id, p.roll_width]))
  } catch (e) {
    err.value = String(e.message || e)
  }
}

async function saveWidth(p) {
  const width = Number(drafts.value[p.id])
  errs.value[p.id] = ''
  if (!(width > 0)) {
    errs.value[p.id] = '卷宽必须大于 0'
    return
  }
  savingId.value = p.id
  try {
    await putJSON(`/api/papers/${p.id}`, { roll_width: width })
    await load()
  } catch (e) {
    errs.value[p.id] = String(e.message || e)
  } finally {
    savingId.value = null
  }
}

async function selectPaper(p) {
  selectingId.value = p.id
  try {
    const settings = await putJSON('/api/settings', { selected_paper_id: p.id })
    selectedId.value = String(settings.selected_paper_id ?? p.id)
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    selectingId.value = null
  }
}
</script>

<template>
  <div class="page">
    <h1>包装纸</h1>
    <p class="lede">
      卷宽当场参与「算纸」按卷宽折张：每张长 = 卷宽，张数 = ceil(用纸面积 ÷ 卷宽²)。
      改卷宽不影响已落库用纸档（钉住写入时快照），只对新切张生效。
    </p>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-else class="paper-grid">
      <div v-for="p in items" :key="p.id" class="paper-tile">
        <strong>{{ p.name }}</strong>
        <span v-if="String(p.id) === selectedId" class="pill">当前选用</span>
        <div class="tile-actions">
          <label class="meta">卷宽 m
            <input v-model.number="drafts[p.id]" type="number" step="0.01" min="0" />
          </label>
          <button :disabled="savingId === p.id" @click="saveWidth(p)">保存</button>
        </div>
        <p v-if="errs[p.id]" class="bad tile-err">{{ errs[p.id] }}</p>
        <button
          v-if="String(p.id) !== selectedId"
          class="ghost tile-select"
          :disabled="selectingId === p.id"
          @click="selectPaper(p)"
        >设为当前选用</button>
      </div>
    </div>
  </div>
</template>
