<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const props = defineProps({ id: String })
const run = ref(null)
const err = ref('')

onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
})

const REASON_TEXT = {
  box_missing: '盒型已不存在，无法互证',
  legacy_run_without_snapshot: '历史单据无卷宽快照，无法互证',
}
</script>

<template>
  <div class="page">
    <h1>用纸档 #{{ id }}</h1>
    <p v-if="err" class="bad">{{ err }} <router-link to="/history">返回用纸档</router-link></p>
    <template v-else-if="run">
      <p class="lede">{{ run.box_name }} · {{ run.created_at }}<template v-if="run.note"> · {{ run.note }}</template></p>

      <div class="unfold">
        <p class="unfold-title">写入时快照</p>
        <p>
          <span class="pill" v-if="run.snapshot_complete">完整快照</span>
          <span class="pill warn" v-else>历史无快照</span>
        </p>
        <ul class="detail-list">
          <li>用纸 <span class="meta">{{ run.result?.paper_name ?? '—' }}</span></li>
          <li>用纸面积 <span class="meta">{{ run.result?.paper_m2 ?? '—' }} m²</span></li>
          <li>卷宽 <span class="meta">{{ run.roll_width ?? '—' }} m</span></li>
          <li>每张长 <span class="meta">{{ run.sheet_len ?? '—' }} m</span></li>
          <li>张数 <span class="meta">{{ run.sheets ?? '—' }} 张</span></li>
        </ul>
      </div>

      <div class="unfold recheck">
        <p class="unfold-title">再干算互证（落库时卷宽/系数 + 当前盒型尺寸）</p>
        <template v-if="run.recheck?.sheets_match === true">
          <p><span class="pill">互证一致</span> 回看 {{ run.recheck.snapshot_sheets }} 张 = 再干算 {{ run.recheck.sheets }} 张</p>
        </template>
        <template v-else-if="run.recheck?.sheets_match === false">
          <p>
            <span class="pill warn">不一致</span>
            回看 {{ run.recheck.snapshot_sheets }} 张，再干算 {{ run.recheck.sheets }} 张
            <template v-if="run.recheck.paper_m2_match === false">
              （面积 {{ run.recheck.snapshot_paper_m2 }} → {{ run.recheck.paper_m2 }} m²，盒型可能已变更）
            </template>
          </p>
        </template>
        <template v-else>
          <p><span class="pill neutral">无法互证</span> {{ REASON_TEXT[run.recheck?.reason] ?? run.recheck?.reason }}</p>
        </template>
        <p class="meta" v-if="run.recheck?.box_dirty">注意：该盒型当前被标记为脏数据。</p>
      </div>

      <div class="row">
        <router-link class="btn ghost" to="/history">返回用纸档</router-link>
        <router-link class="btn" to="/bench">去算纸</router-link>
      </div>
    </template>
  </div>
</template>
