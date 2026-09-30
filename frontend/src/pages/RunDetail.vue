<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const props = defineProps({ id: String })
const run = ref(null)
const recheck = ref(null)
const err = ref('')

onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch (e) {
    err.value = String(e.message || e)
    return
  }
  try {
    recheck.value = await getJSON(`/api/runs/${props.id}/recheck`)
  } catch (e) {
    // 无卷宽快照的旧单无法按卷宽复算，详情仍可展示
  }
})
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="run">
      <h1>{{ run.box_name }} · 用纸档 #{{ run.id }}</h1>
      <p class="lede">
        {{ run.length }} × {{ run.width }} × {{ run.height }} m，折边系数 {{ run.overlap }}。
        卷宽与折张为写入时快照，纸张页后续改宽不影响本单。
      </p>
      <ul class="item-list">
        <li><span>用纸面积（几何口径）</span><span class="meta">{{ run.result?.paper_m2 ?? '—' }} m²</span></li>
        <li><span>写入时卷宽</span><span class="meta">{{ run.roll_width ?? '—' }} m</span></li>
        <li><span>每张长度</span><span class="meta">{{ run.sheet_len ?? '—' }} m</span></li>
        <li><span>折张数</span><span class="meta">{{ run.sheets ?? '—' }} 张</span></li>
      </ul>
      <div v-if="recheck" class="result-board">
        <p class="stat-line">
          用写入时卷宽 {{ recheck.recomputed.roll_width }} m 再干算：
          每张约 {{ recheck.recomputed.sheet_len }} m，共
          <strong>{{ recheck.recomputed.sheets }}</strong> 张
          <span class="pill" :class="{ warn: !recheck.sheets_match }">
            {{ recheck.sheets_match ? '与快照互证一致' : '与快照不一致' }}
          </span>
        </p>
      </div>
      <div class="row" style="margin-top: 1.25rem">
        <router-link class="btn ghost" to="/history">返回用纸档</router-link>
      </div>
    </template>
  </div>
</template>
