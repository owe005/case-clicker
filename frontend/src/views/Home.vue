<template>
  <div class="max-w-7xl mx-auto px-4 py-12">
    <!-- Hero Section -->
    <div class="text-center mb-20 relative">
      <!-- Background Effects -->
      <div class="absolute inset-0 bg-gradient-radial from-yellow/5 via-transparent to-transparent -top-24"></div>
      <div class="absolute inset-0 bg-gradient-mesh opacity-20" style="background-size: 30px 30px;"></div>

      <!-- Content -->
      <div class="relative">
        <img src="@/assets/logo.png" alt="Case Clicker Logo" class="w-32 h-32 mx-auto mb-8 animate-float">
        <h1 class="display-heading text-4xl md:text-6xl mb-5">
          Welcome to <span class="text-yellow">Case Clicker</span>
        </h1>
        <div class="w-24 h-px mx-auto bg-gradient-to-r from-transparent via-yellow/30 to-transparent mb-6"></div>
        <p class="text-base md:text-lg text-white/70 max-w-2xl mx-auto">
          Experience the thrill of CS:GO case opening in an elegant idle game environment.
        </p>
      </div>
    </div>

    <!-- Features Section -->
    <div class="glass-panel p-8 md:p-10">
      <h2 class="display-heading text-2xl md:text-3xl mb-3 text-yellow">Game Features</h2>
      <p class="text-base text-white/70 mb-10 max-w-3xl">
        Start with $1000 and build your inventory through various engaging game modes:
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="feature-card group">
          <div class="feature-icon group-hover:text-yellow group-hover:scale-110">🖱️</div>
          <h3 class="display-heading text-lg mb-2">Clicker</h3>
          <p class="text-sm text-white/60">
            Click to earn money and upgrade your clicking power. Enable auto-clicker and other upgrades for passive income.
          </p>
        </div>

        <div class="feature-card group">
          <div class="feature-icon group-hover:text-yellow group-hover:scale-110">📦</div>
          <h3 class="display-heading text-lg mb-2">Cases</h3>
          <p class="text-sm text-white/60">
            Open CS:GO-style cases for a chance to get rare skins. From common blues to rare knives, build your dream inventory.
          </p>
        </div>

        <div class="feature-card group">
          <div class="feature-icon group-hover:text-yellow group-hover:scale-110">🎰</div>
          <h3 class="display-heading text-lg mb-2">Casino</h3>
          <p class="text-sm text-white/60">
            Try your luck with various casino games including Coinflip, Crash, Roulette, Blackjack, and Jackpot.
          </p>
        </div>

        <div class="feature-card group">
          <div class="feature-icon group-hover:text-yellow group-hover:scale-110">📈</div>
          <h3 class="display-heading text-lg mb-2">Progress</h3>
          <p class="text-sm text-white/60">
            Level up from Silver I to Global Elite as you play. Each rank brings new achievements and bragging rights.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script> 