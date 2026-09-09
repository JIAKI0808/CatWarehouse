<script setup lang="ts">
defineProps<{
  type: 'box' | 'shelf' | 'pallet'
  size?: 'small' | 'medium' | 'large'
}>()
</script>

<template>
  <!-- 精美纸箱 -->
  <div v-if="type === 'box'" class="box-wrapper" :class="size || 'medium'">
    <div class="box-body">
      <div class="box-flap left"></div>
      <div class="box-flap right"></div>
      <div class="box-tape"></div>
      <div class="box-label"></div>
    </div>
    <div class="box-shadow"></div>
  </div>

  <!-- 精美货架 -->
  <div v-else-if="type === 'shelf'" class="shelf-wrapper">
    <div class="shelf-top"></div>
    <div class="shelf-leg left"></div>
    <div class="shelf-leg right"></div>
    <div class="shelf-bar top"></div>
    <div class="shelf-bar middle"></div>
    <div class="shelf-bar bottom"></div>
    <div class="shelf-item item1"></div>
    <div class="shelf-item item2"></div>
    <div class="shelf-item item3"></div>
  </div>

  <!-- 托盘 -->
  <div v-else-if="type === 'pallet'" class="pallet-wrapper">
    <div class="pallet-board"></div>
    <div class="pallet-leg left"></div>
    <div class="pallet-leg right"></div>
  </div>
</template>

<style scoped>
/* 纸箱样式 */
.box-wrapper {
  position: relative;
}

.box-wrapper.small { width: 55px; height: 45px; }
.box-wrapper.medium { width: 70px; height: 55px; }
.box-wrapper.large { width: 85px; height: 65px; }

.box-body {
  width: 100%;
  height: 100%;
  background: linear-gradient(145deg, #E8C99B 0%, #D4A574 50%, #C4956A 100%);
  border-radius: 4px;
  position: relative;
  box-shadow:
    inset 0 2px 4px rgba(255,255,255,0.3),
    0 4px 8px rgba(0,0,0,0.15);
}

.box-flap {
  position: absolute;
  top: -8px;
  width: 50%;
  height: 12px;
  background: linear-gradient(145deg, #F0D9B5 0%, #E8C99B 100%);
  border-radius: 2px 2px 0 0;
}

.box-flap.left {
  left: 0;
  transform: rotate(-5deg);
}

.box-flap.right {
  right: 0;
  transform: rotate(5deg);
}

.box-tape {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60%;
  height: 10px;
  background: linear-gradient(90deg, #F5E6D3 0%, #EDE0D4 50%, #F5E6D3 100%);
  border-radius: 2px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.box-label {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 20px;
  background: #FFF9F0;
  border: 1px solid #D4A574;
  border-radius: 2px;
}

.box-shadow {
  position: absolute;
  bottom: -6px;
  left: 10%;
  width: 80%;
  height: 6px;
  background: radial-gradient(ellipse, rgba(0,0,0,0.2) 0%, transparent 70%);
  border-radius: 50%;
}

/* 货架样式 */
.shelf-wrapper {
  position: relative;
  width: 90px;
  height: 110px;
}

.shelf-top {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 8px;
  background: linear-gradient(180deg, #8B6914 0%, #6B4F12 100%);
  border-radius: 2px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.shelf-leg {
  position: absolute;
  top: 8px;
  width: 8px;
  height: 102px;
  background: linear-gradient(90deg, #6B4F12 0%, #8B6914 50%, #6B4F12 100%);
  border-radius: 2px;
}

.shelf-leg.left { left: 5px; }
.shelf-leg.right { right: 5px; }

.shelf-bar {
  position: absolute;
  left: 5px;
  right: 5px;
  height: 6px;
  background: linear-gradient(180deg, #8B6914 0%, #6B4F12 100%);
  border-radius: 2px;
  box-shadow: 0 2px 3px rgba(0,0,0,0.15);
}

.shelf-bar.top { top: 30px; }
.shelf-bar.middle { top: 58px; }
.shelf-bar.bottom { top: 86px; }

.shelf-item {
  position: absolute;
  border-radius: 3px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.shelf-item.item1 {
  top: 12px;
  left: 18px;
  width: 25px;
  height: 16px;
  background: linear-gradient(135deg, #FFB6C1 0%, #FF69B4 100%);
}

.shelf-item.item2 {
  top: 40px;
  right: 15px;
  width: 30px;
  height: 14px;
  background: linear-gradient(135deg, #87CEEB 0%, #4169E1 100%);
}

.shelf-item.item3 {
  top: 68px;
  left: 20px;
  width: 22px;
  height: 14px;
  background: linear-gradient(135deg, #98FB98 0%, #32CD32 100%);
}

/* 托盘样式 */
.pallet-wrapper {
  position: relative;
  width: 80px;
  height: 20px;
}

.pallet-board {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 10px;
  background: linear-gradient(180deg, #D2691E 0%, #8B4513 100%);
  border-radius: 2px;
}

.pallet-leg {
  position: absolute;
  bottom: 0;
  width: 12px;
  height: 12px;
  background: linear-gradient(180deg, #8B4513 0%, #654321 100%);
  border-radius: 2px;
}

.pallet-leg.left { left: 8px; }
.pallet-leg.right { right: 8px; }
</style>
