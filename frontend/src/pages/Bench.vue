<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, putJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const boxes = ref([])
const papers = ref([])
const bid = ref(1)
const pid = ref(null)
const out = ref(null)
const err = ref('')
const busy = ref(false)

onMounted(async () => {
  try {
    const [b, p, s] = await Promise.all([
      getJSON('/api/boxes'),
      getJSON('/api/papers'),
      getJSON('/api/settings'),
    ])
    boxes.value = b.items.filter((x) => x.data_quality === 'clean')
    papers.value = p.items
    pid.value = Number(s.selected_paper_id) || p.items[0]?.id || null
    if (boxes.value.length) bid.value = boxes.value[0].id
  } catch (e) {
    err.value = String(e.message || e)
  }
})

async function selectPaper() {
  err.value = ''
  try {
    await putJSON('/api/settings', { selected_paper_id: pid.value })
  } catch (e) {
    err.value = String(e.message || e)
  }
}

async function go(save) {
  err.value = ''
  busy.value = true
  try {
    out.value = save
      ? await postJSON('/api/estimate', { box_id: bid.value, paper_id: pid.value, save: true })
      : await getJSON(`/api/estimate?box_id=${bid.value}&paper_id=${pid.value}`)
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>算纸</h1>
    <p class="lede">先试算看面积与折张，确认后再写入用纸档。卷宽改动当场生效。</p>
    <div class="row">
      <select v-model.number="bid">
        <option v-for="b in boxes" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <select v-model.number="pid" @change="selectPaper">
        <option v-for="p in papers" :key="p.id" :value="p.id">{{ p.name }}（卷宽 {{ p.roll_width }} m）</option>
      </select>
      <button :disabled="busy" @click="go(false)">试算</button>
      <button class="ribbon" :disabled="busy" @click="go(true)">写入用纸档</button>
    </div>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-if="out" class="result-board">
      <div class="figure">{{ out.paper_m2 }}<span>m²</span></div>
      <p class="stat-line">
        {{ out.paper_name }} · 卷宽 {{ out.roll_width }} m · 每张长 {{ out.sheet_len }} m · <strong>{{ out.sheets }} 张</strong>
      </p>
      <p class="stat-line" v-if="out.ribbon">
        十字丝带约 {{ out.ribbon.ribbon_m ?? out.ribbon }} m
      </p>
      <BoxUnfold
        :l="out.box.length"
        :w="out.box.width"
        :h="out.box.height"
        :paper-m2="out.paper_m2"
      />
    </div>
  </div>
</template>
