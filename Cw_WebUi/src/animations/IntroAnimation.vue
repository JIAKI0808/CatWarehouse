<script setup lang="ts">
import { useIntroAnimation } from './composables/useIntroAnimation'
import LetterAnimation from './components/LetterAnimation.vue'
import WarehouseElement from './components/WarehouseElement.vue'
import CatElement from './components/CatElement.vue'

const emit = defineEmits<{
  (e: 'complete'): void
}>()

const title = 'CatWareHouse'

const { skip } = useIntroAnimation(() => {
  emit('complete')
})

function handleSkip() {
  skip()
}
</script>

<template>
  <div class="intro-background">
    <!-- 背景爪印装饰 -->
    <div class="paw-prints">
      <div class="paw-print print1"></div>
      <div class="paw-print print2"></div>
      <div class="paw-print print3"></div>
      <div class="paw-print print4"></div>
      <div class="paw-print print5"></div>
      <div class="paw-print print6"></div>
    </div>

    <button
      class="skip-btn"
      @click="handleSkip"
    >
      跳过动画
    </button>

    <div class="intro-container">
      <!-- 标题字母 -->
      <div class="title-area">
        <LetterAnimation
          v-for="(letter, index) in title"
          :key="index"
          :letter="letter"
          class="intro-letter"
        />
      </div>

      <!-- 仓库元素 -->
      <div class="warehouse-area">
        <WarehouseElement type="shelf" class="warehouse-shelf" />
        <WarehouseElement type="box" size="medium" class="warehouse-box box1" />
        <WarehouseElement type="box" size="large" class="warehouse-box box2" />
        <WarehouseElement type="pallet" class="warehouse-pallet" />
      </div>

      <!-- 猫猫 -->
      <div class="cat-area">
        <CatElement class="intro-cat" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.intro-background {
  background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 50%, #90CAF9 100%);
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  overflow: hidden;
}

/* 背景爪印 */
.paw-prints {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.paw-print {
  position: absolute;
  width: 40px;
  height: 45px;
  opacity: 0.15;
}

.paw-print::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 28px;
  height: 24px;
  background: #5D4037;
  border-radius: 50%;
}

.paw-print::after {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 32px;
  height: 14px;
  background:
    radial-gradient(circle at 20% 50%, #5D4037 6px, transparent 6px),
    radial-gradient(circle at 50% 30%, #5D4037 6px, transparent 6px),
    radial-gradient(circle at 80% 50%, #5D4037 6px, transparent 6px);
}

.print1 { top: 10%; left: 8%; transform: rotate(-20deg); }
.print2 { top: 25%; right: 12%; transform: rotate(15deg); }
.print3 { bottom: 30%; left: 15%; transform: rotate(-35deg); }
.print4 { bottom: 15%; right: 8%; transform: rotate(25deg); }
.print5 { top: 50%; left: 5%; transform: rotate(-10deg); opacity: 0.1; }
.print6 { top: 40%; right: 5%; transform: rotate(30deg); opacity: 0.1; }

.skip-btn {
  position: absolute;
  top: 24px;
  right: 24px;
  padding: 10px 20px;
  font-size: 14px;
  color: #1976D2;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid #1976D2;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10000;
  font-weight: 500;
  backdrop-filter: blur(4px);
}

.skip-btn:hover {
  background: #1976D2;
  color: white;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.4);
}

.intro-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.title-area {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  gap: 4px;
}

.warehouse-area {
  position: absolute;
  bottom: 12%;
  left: 8%;
  display: flex;
  align-items: flex-end;
  gap: 25px;
  transform: scale(1.4);
}

.warehouse-shelf {
  margin-right: 10px;
}

.warehouse-pallet {
  margin-left: 10px;
}

.cat-area {
  position: absolute;
  bottom: 15%;
  right: 12%;
  transform: scale(1.6);
}

.intro-cat {
  position: relative;
}
</style>
