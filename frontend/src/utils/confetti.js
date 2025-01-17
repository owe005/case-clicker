export function createConfetti() {
  const colors = ['#FFD700', '#FFA500', '#FF4500', '#FF6347', '#FF69B4']
  const confettiCount = 100

  for (let i = 0; i < confettiCount; i++) {
    const confetti = document.createElement('div')
    confetti.className = 'confetti'
    confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)]
    confetti.style.left = Math.random() * 100 + 'vw'
    confetti.style.animationDuration = (Math.random() * 3 + 2) + 's'
    confetti.style.opacity = Math.random()
    document.body.appendChild(confetti)

    // Remove confetti after animation
    setTimeout(() => {
      confetti.remove()
    }, 5000)
  }
} 