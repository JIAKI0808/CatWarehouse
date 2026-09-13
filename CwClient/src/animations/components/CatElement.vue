<script setup lang="ts">
</script>

<template>
  <div class="cat-wrapper">
    <!-- 耳朵 -->
    <div class="ear left">
      <div class="ear-inner"></div>
    </div>
    <div class="ear right">
      <div class="ear-inner"></div>
    </div>

    <!-- 头部 -->
    <div class="head">
      <div class="face">
        <!-- 眼睛 -->
        <div class="eye left">
          <div class="pupil"></div>
          <div class="shine"></div>
        </div>
        <div class="eye right">
          <div class="pupil"></div>
          <div class="shine"></div>
        </div>

        <!-- 鼻子 -->
        <div class="nose"></div>

        <!-- 嘴巴 -->
        <div class="mouth">
          <div class="mouth-line left"></div>
          <div class="mouth-line right"></div>
        </div>

        <!-- 胡须 -->
        <div class="whisker left top"></div>
        <div class="whisker left bottom"></div>
        <div class="whisker right top"></div>
        <div class="whisker right bottom"></div>

        <!-- 腮红 -->
        <div class="blush left"></div>
        <div class="blush right"></div>
      </div>

      <!-- 斑点 -->
      <div class="head-spot spot1"></div>
      <div class="head-spot spot2"></div>
    </div>

    <!-- 身体 -->
    <div class="body">
      <div class="body-pattern"></div>
      <div class="chest"></div>

      <!-- 前爪 -->
      <div class="paw front left"></div>
      <div class="paw front right"></div>

      <!-- 后爪 -->
      <div class="paw back left"></div>
      <div class="paw back right"></div>
    </div>

    <!-- 尾巴 -->
    <div class="tail">
      <div class="tail-tip"></div>
    </div>
  </div>
</template>

<style scoped>
.cat-wrapper {
  position: relative;
  width: 100px;
  height: 110px;
}

/* 耳朵 */
.ear {
  position: absolute;
  top: 0;
  width: 28px;
  height: 30px;
  background: #F5DEB3;
  border-radius: 50% 50% 0 0;
  z-index: 1;
  overflow: hidden;
}

.ear.left {
  left: 15px;
  transform: rotate(-15deg);
}

.ear.right {
  right: 15px;
  transform: rotate(15deg);
}

.ear-inner {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 16px;
  height: 18px;
  background: #FFB6C1;
  border-radius: 50% 50% 0 0;
}

/* 头部 */
.head {
  position: absolute;
  top: 15px;
  left: 50%;
  transform: translateX(-50%);
  width: 70px;
  height: 60px;
  background: linear-gradient(180deg, #F5DEB3 0%, #EED9B7 100%);
  border-radius: 50%;
  z-index: 2;
  overflow: hidden;
}

.head-spot {
  position: absolute;
  border-radius: 50%;
}

.head-spot.spot1 {
  top: 5px;
  right: 5px;
  width: 20px;
  height: 18px;
  background: #D2691E;
}

.head-spot.spot2 {
  top: 25px;
  left: 0;
  width: 15px;
  height: 14px;
  background: #CD853F;
}

.face {
  position: relative;
  width: 100%;
  height: 100%;
}

/* 眼睛 */
.eye {
  position: absolute;
  top: 22px;
  width: 16px;
  height: 18px;
  background: linear-gradient(180deg, #90EE90 0%, #228B22 100%);
  border-radius: 50%;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
}

.eye.left { left: 12px; }
.eye.right { right: 12px; }

.pupil {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 10px;
  background: #000;
  border-radius: 50%;
}

.shine {
  position: absolute;
  top: 4px;
  left: 4px;
  width: 4px;
  height: 4px;
  background: #FFF;
  border-radius: 50%;
}

/* 鼻子 */
.nose {
  position: absolute;
  top: 38px;
  left: 50%;
  transform: translateX(-50%);
  width: 10px;
  height: 7px;
  background: #FFB6C1;
  border-radius: 50% 50% 40% 40%;
}

/* 嘴巴 */
.mouth {
  position: absolute;
  top: 45px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 10px;
}

.mouth-line {
  position: absolute;
  top: 0;
  width: 10px;
  height: 8px;
  border-bottom: 2px solid #8B4513;
  border-radius: 0 0 50% 50%;
}

.mouth-line.left { left: 0; }
.mouth-line.right { right: 0; }

/* 胡须 */
.whisker {
  position: absolute;
  width: 25px;
  height: 2px;
  background: linear-gradient(90deg, #8B4513 0%, transparent 100%);
}

.whisker.left {
  left: -20px;
  background: linear-gradient(90deg, transparent 0%, #8B4513 100%);
}

.whisker.right {
  right: -20px;
}

.whisker.top { top: 36px; }
.whisker.bottom { top: 42px; }

.whisker.left.top { transform: rotate(-8deg); }
.whisker.left.bottom { transform: rotate(8deg); }
.whisker.right.top { transform: rotate(8deg); }
.whisker.right.bottom { transform: rotate(-8deg); }

/* 腮红 */
.blush {
  position: absolute;
  top: 38px;
  width: 12px;
  height: 8px;
  background: rgba(255, 182, 193, 0.6);
  border-radius: 50%;
}

.blush.left { left: 5px; }
.blush.right { right: 5px; }

/* 身体 */
.body {
  position: absolute;
  top: 65px;
  left: 50%;
  transform: translateX(-50%);
  width: 55px;
  height: 45px;
  background: linear-gradient(180deg, #F5DEB3 0%, #EED9B7 100%);
  border-radius: 50% 50% 40% 40%;
  z-index: 1;
}

.body-pattern {
  position: absolute;
  top: 10px;
  left: 5px;
  width: 25px;
  height: 20px;
  background: #D2691E;
  border-radius: 50%;
}

.chest {
  position: absolute;
  bottom: 5px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 20px;
  background: #FFFAF0;
  border-radius: 50%;
}

/* 爪子 */
.paw {
  position: absolute;
  bottom: -8px;
  width: 14px;
  height: 12px;
  background: #F5DEB3;
  border-radius: 50%;
}

.paw.front { bottom: 0; }
.paw.back { bottom: -5px; }

.paw.front.left { left: 5px; }
.paw.front.right { right: 5px; }
.paw.back.left { left: 0; }
.paw.back.right { right: 0; }

/* 尾巴 */
.tail {
  position: absolute;
  top: 80px;
  right: -25px;
  width: 40px;
  height: 12px;
  background: linear-gradient(90deg, #F5DEB3 0%, #D2691E 100%);
  border-radius: 6px;
  transform-origin: left center;
  z-index: 0;
}

.tail-tip {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 14px;
  height: 14px;
  background: #8B4513;
  border-radius: 50%;
}
</style>
