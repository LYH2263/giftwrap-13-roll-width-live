<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const boxes = ref([])
const papers = ref([])
const bid = ref(1)
const pid = ref(null)
const out = ref(null)
const err = ref('')
const busy = ref(false)

const currentPaper = () => papers.value.find((p) => p.id === pid.value) || null

onMounted(async () => {
  try {
    const [b, p] = await Promise.all([getJSON('/api/boxes'), getJSON('/api/papers')])
    boxes.value = b.items.filter((x) => x.data_quality === 'clean')
    papers.value = p.items
    if (boxes.value.length) bid.value = boxes.value[0].id
    if (papers.value.length) pid.value = papers.value[0].id
  } catch (e) {
    err.value = String(e.message || e)
  }
})

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
    <p class="lede">先试算看面积、卷宽折张与展开，确认后再写入用纸档。改卷宽请去纸张页，保存后此处立即按新卷宽算。</p>
    <div class="row">
      <select v-model.number="bid">
        <option v-for="b in boxes" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <select v-model.number="pid">
        <option v-for="p in papers" :key="p.id" :value="p.id">{{ p.name }}（卷宽 {{ p.roll_width }} m）</option>
      </select>
      <button :disabled="busy" @click="go(false)">试算</button>
      <button class="ribbon" :disabled="busy" @click="go(true)">写入用纸档</button>
    </div>
    <p v-if="currentPaper()" class="meta">当前选用 {{ currentPaper()?.name }}，卷宽 {{ currentPaper()?.roll_width }} m</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-if="out" class="result-board">
      <div class="figure">{{ out.paper_m2 }}<span>m²</span></div>
      <p class="stat-line">
        卷宽 {{ out.roll_width }} m 折张：每张约 {{ out.sheet_len }} m，共 <strong>{{ out.sheets }}</strong> 张
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
