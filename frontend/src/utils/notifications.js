export function showLevelUpBanner(rankName) {
  const banner = document.createElement('div')
  banner.className = 'level-up-banner'
  banner.innerHTML = `
    <div class="level-up-content">
      <h2>Level Up!</h2>
      <p>You've reached ${rankName}!</p>
    </div>
  `
  document.body.appendChild(banner)

  // Remove banner after animation
  setTimeout(() => {
    banner.classList.add('fade-out')
    setTimeout(() => {
      banner.remove()
    }, 1000)
  }, 4000)
} 