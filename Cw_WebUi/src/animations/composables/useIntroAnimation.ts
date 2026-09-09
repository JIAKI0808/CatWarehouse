import { gsap } from 'gsap'
import { onMounted, onUnmounted } from 'vue'

export function useIntroAnimation(onComplete: () => void) {
  let timeline: gsap.core.Timeline | null = null

  const animateWarehouseElements = (tl: gsap.core.Timeline) => {
    tl.from('.warehouse-box', {
      y: 80,
      opacity: 0,
      scale: 0.7,
      duration: 0.6,
      stagger: 0.12,
      ease: 'back.out(1.4)',
    }, 0.3)

    tl.from('.warehouse-shelf', {
      x: -100,
      opacity: 0,
      duration: 0.7,
      ease: 'power3.out',
    }, 0.4)
  }

  const animateLetters = (tl: gsap.core.Timeline) => {
    const letters = document.querySelectorAll('.intro-letter')
    letters.forEach((letter, i) => {
      tl.from(letter, {
        y: -60,
        opacity: 0,
        scale: 0.3,
        rotationZ: gsap.utils.random(-15, 15),
        duration: 0.5,
        ease: 'back.out(2)',
      }, 0.8 + i * 0.07)
    })
  }

  const animateCat = (tl: gsap.core.Timeline) => {
    const cat = document.querySelector('.intro-cat')
    const tail = document.querySelector('.cat-tail')
    if (!cat) return

    tl.from(cat, {
      x: 150,
      opacity: 0,
      duration: 0.5,
      ease: 'power2.out',
    }, 1.5)

    tl.to(cat, {
      y: -30,
      scaleY: 1.1,
      duration: 0.18,
      ease: 'power2.in',
    }, 2.0)

    tl.to(cat, {
      y: 0,
      scaleY: 1,
      duration: 0.22,
      ease: 'bounce.out',
    }, 2.18)

    if (tail) {
      gsap.to(tail, {
        rotation: 20,
        duration: 0.35,
        yoyo: true,
        repeat: -1,
        ease: 'sine.inOut',
      })
    }
  }

  const createTimeline = () => {
    timeline = gsap.timeline({
      onComplete: () => {
        setTimeout(onComplete, 300)
      },
    })

    timeline.from('.intro-background', {
      opacity: 0,
      duration: 0.5,
      ease: 'power2.out',
    })

    animateWarehouseElements(timeline)
    animateLetters(timeline)
    animateCat(timeline)

    timeline.to('.intro-container', {
      opacity: 0,
      y: -30,
      duration: 0.5,
      ease: 'power2.in',
    }, '+=0.5')

    return timeline
  }

  onMounted(() => {
    createTimeline()
  })

  onUnmounted(() => {
    if (timeline) {
      timeline.kill()
    }
  })

  const skip = () => {
    if (timeline) {
      timeline.progress(1)
    }
  }

  return { skip }
}
