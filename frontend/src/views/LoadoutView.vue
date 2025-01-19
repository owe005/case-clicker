<template>
  <div class="min-h-screen bg-gray-darker">
    <!-- Loadout Header -->
    <div class="relative py-12 mb-8">
      <div class="absolute inset-0 bg-gradient-to-b from-yellow/5 to-transparent"></div>
      <div class="relative max-w-7xl mx-auto px-4">
        <h1 class="text-4xl font-display font-bold text-white mb-2">Loadout</h1>
        <p class="text-white/70">Customize your weapon skins for each team</p>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <!-- Team Tabs -->
      <div class="flex gap-2 mb-8">
        <button 
          v-for="team in ['CT', 'T']" 
          :key="team"
          class="px-6 py-2 rounded-lg font-medium transition-all duration-200"
          :class="[
            currentTeam === team 
              ? 'bg-yellow text-gray-darker' 
              : 'bg-gray-dark/50 text-white/70 hover:bg-gray-dark hover:text-white'
          ]"
          @click="currentTeam = team"
        >
          {{ team }} Side
        </button>
      </div>

      <!-- Category Tabs -->
      <div class="flex flex-wrap gap-2 mb-8">
        <button 
          v-for="(icon, category) in categoryIcons" 
          :key="category"
          class="px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2"
          :class="[
            currentCategory === category 
              ? 'bg-yellow text-gray-darker' 
              : 'bg-gray-dark/50 text-white/70 hover:bg-gray-dark hover:text-white'
          ]"
          @click="currentCategory = category"
        >
          <span class="text-inherit">{{ icon }}</span>
          {{ getCategoryName(category) }}
        </button>
      </div>

      <!-- Weapon Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Special handling for Knife & Gloves -->
        <template v-if="currentCategory === 'special'">
          <div 
            v-for="type in ['knife', 'glove']"
            :key="type"
            class="flex items-center gap-4 p-3 bg-gray-dark/50 rounded-lg cursor-pointer hover:bg-gray-dark transition-all duration-200 relative"
            @click="openSelector(type)"
          >
            <div v-if="getEquippedItem(type)" class="absolute inset-x-0 top-0 h-1 rounded-t-xl z-10" :class="getRarityColor(getEquippedItem(type).rarity)"></div>
            <img 
              :src="getEquippedItem(type) ? getSkinImagePath(getEquippedItem(type)) : `/vanilla/${type}.png`"
              :alt="getWeaponName(type)"
              class="w-24 h-24 object-contain"
            />
            <div>
              <div class="text-white font-medium">
                {{ getEquippedItem(type) ? getEquippedItem(type).name : 'Default ' + getWeaponName(type) }}
              </div>
              <div v-if="getEquippedItem(type)" class="text-white/50 text-sm">
                {{ getEquippedItem(type).wear }}
                <span v-if="getEquippedItem(type).float_value !== undefined">({{ getEquippedItem(type).float_value.toFixed(8) }})</span>
                <span v-if="getEquippedItem(type).stattrak" class="text-yellow">• StatTrak™</span>
              </div>
            </div>
          </div>
        </template>

        <!-- Regular weapons -->
        <template v-else>
          <div 
            v-for="weapon in getWeaponsForCategory(currentCategory)"
            :key="weapon"
            class="flex items-center gap-4 p-3 bg-gray-dark/50 rounded-lg cursor-pointer hover:bg-gray-dark transition-all duration-200 relative"
            @click="openSelector(weapon)"
          >
            <div v-if="getEquippedItem(weapon)" class="absolute inset-x-0 top-0 h-1 rounded-t-xl z-10" :class="getRarityColor(getEquippedItem(weapon).rarity)"></div>
            <img 
              :src="getEquippedItem(weapon) ? getSkinImagePath(getEquippedItem(weapon)) : `/vanilla/${weapon}.png`"
              :alt="getWeaponName(weapon)"
              class="w-24 h-24 object-contain"
            />
            <div>
              <div class="text-white font-medium">
                {{ getEquippedItem(weapon) ? getEquippedItem(weapon).name : 'Default ' + getWeaponName(weapon) }}
              </div>
              <div v-if="getEquippedItem(weapon)" class="text-white/50 text-sm">
                {{ getEquippedItem(weapon).wear }}
                <span v-if="getEquippedItem(weapon).float_value !== undefined">({{ getEquippedItem(weapon).float_value.toFixed(8) }})</span>
                <span v-if="getEquippedItem(weapon).stattrak" class="text-yellow">• StatTrak™</span>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Skin Selector Modal -->
    <div 
      v-if="showSelector"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      @click.self="closeSelector"
    >
      <div class="bg-gray-dark rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-display text-white">Select Skin for {{ getWeaponName(currentSlot) }}</h3>
          <button 
            @click="closeSelector"
            class="text-white/50 hover:text-white transition-colors"
          >
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Available Skins -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- Default/Remove Option -->
          <button
            class="bg-gray-darker p-4 rounded-lg hover:bg-gray-dark/70 transition-all duration-200"
            @click="equipSkin(null)"
          >
            <img 
              :src="`/vanilla/${currentSlot}.png`"
              :alt="getWeaponName(currentSlot)"
              class="w-full h-32 object-contain mb-2"
            >
            <div class="text-white font-medium">Default {{ getWeaponName(currentSlot) }}</div>
          </button>

          <!-- Available Skins -->
          <template v-for="skin in getAvailableSkins()" :key="skin.id">
            <button
              class="bg-gray-darker p-4 rounded-lg hover:bg-gray-dark/70 transition-all duration-200 relative"
              @click="equipSkin(skin)"
            >
              <div class="absolute inset-x-0 top-0 h-1 rounded-t-lg z-10" :class="getRarityColor(skin.rarity)"></div>
              <img 
                :src="getSkinImagePath(skin)"
                :alt="skin.name"
                class="w-full h-32 object-contain mb-2"
              >
              <div class="text-white font-medium">{{ skin.name }}</div>
              <div class="text-white/50 text-sm">
                {{ skin.wear }}
                <span v-if="skin?.float_value">({{ skin.float_value.toFixed(4) }})</span>
                <span v-if="skin.stattrak" class="text-yellow">• StatTrak™</span>
              </div>
            </button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useStore, CASE_MAPPING } from '../store'

export default {
  name: 'LoadoutView',
  setup() {
    const store = useStore()
    const currentTeam = ref('CT')
    const showSelector = ref(false)
    const currentSlot = ref(null)
    const loadout = ref({
      CT: {},
      T: {}
    })
    const currentCategory = ref('special')
    
    const categoryIcons = {
      special: '★',
      pistols: '🔫',
      smgs: '🔫',
      rifles: '🎯',
      snipers: '🎯',
      shotguns: '💥',
      heavy: '💪'
    }

    const getCategoryName = (category) => {
      const names = {
        special: 'Knife & Gloves',
        pistols: 'Pistols',
        smgs: 'SMGs',
        rifles: 'Rifles',
        snipers: 'Snipers',
        shotguns: 'Shotguns',
        heavy: 'Heavy'
      }
      return names[category]
    }

    const getWeaponsForCategory = (category) => {
      switch (category) {
        case 'pistols':
          return getPistols()
        case 'smgs':
          return getSMGs()
        case 'rifles':
          return getRifles()
        case 'snipers':
          return getSnipers()
        case 'shotguns':
          return getShotguns()
        case 'heavy':
          return getHeavy()
        default:
          return []
      }
    }

    // Weapon name mappings
    const weaponNames = {
      'knife': 'Knife',
      'glove': 'Gloves',
      'ak47': 'AK-47',
      'm4a4': 'M4A4',
      'm4a1s': 'M4A1-S',
      'awp': 'AWP',
      'deserteagle': 'Desert Eagle',
      'usps': 'USP-S',
      'glock18': 'Glock-18',
      'p2000': 'P2000',
      'fiveseven': 'Five-SeveN',
      'p250': 'P250',
      'cz75auto': 'CZ75-Auto',
      'dualberettas': 'Dual Berettas',
      'r8revolver': 'R8 Revolver',
      'tec9': 'Tec-9',
      'mp9': 'MP9',
      'mp7': 'MP7',
      'mp5': 'MP5-SD',
      'p90': 'P90',
      'ump45': 'UMP-45',
      'ppbizon': 'PP-Bizon',
      'mac10': 'MAC-10',
      'famas': 'FAMAS',
      'aug': 'AUG',
      'ssg08': 'SSG 08',
      'scar20': 'SCAR-20',
      'galil': 'Galil AR',
      'sg553': 'SG 553',
      'g3sg1': 'G3SG1',
      'mag7': 'MAG-7',
      'nova': 'Nova',
      'xm1014': 'XM1014',
      'm249': 'M249',
      'negev': 'Negev',
      'sawedoff': 'Sawed-Off'
    }

    // Get proper weapon name
    const getWeaponName = (type) => {
      return weaponNames[type] || type.toUpperCase()
    }

    // Weapon categorization
    const weaponCategories = {
      pistols: {
        CT: ['usps', 'p2000', 'fiveseven', 'deserteagle', 'p250', 'cz75auto', 'dualberettas', 'r8revolver'],
        T: ['glock18', 'tec9', 'deserteagle', 'p250', 'cz75auto', 'dualberettas', 'r8revolver']
      },
      smgs: {
        CT: ['mp9', 'mp7', 'mp5', 'p90', 'ump45', 'ppbizon'],
        T: ['mac10', 'mp7', 'mp5', 'p90', 'ump45', 'ppbizon']
      },
      shotguns: {
        CT: ['mag7', 'nova', 'xm1014'],
        T: ['sawedoff', 'nova', 'xm1014']
      },
      rifles: {
        CT: ['m4a4', 'm4a1s', 'famas', 'aug'],
        T: ['ak47', 'galil', 'sg553']
      },
      snipers: {
        CT: ['ssg08', 'awp', 'scar20'],
        T: ['ssg08', 'awp', 'g3sg1']
      },
      heavy: {
        CT: ['m249', 'negev'],
        T: ['m249', 'negev']
      }
    }

    // Helper functions for weapon categories
    const getPistols = () => weaponCategories.pistols[currentTeam.value]
    const getSMGs = () => weaponCategories.smgs[currentTeam.value]
    const getShotguns = () => weaponCategories.shotguns[currentTeam.value]
    const getRifles = () => weaponCategories.rifles[currentTeam.value]
    const getSnipers = () => weaponCategories.snipers[currentTeam.value]
    const getHeavy = () => weaponCategories.heavy[currentTeam.value]

    // Load saved loadout from backend
    const loadSavedLoadout = async () => {
      try {
        const response = await fetch('/api/loadout/load')
        const data = await response.json()
        
        if (data.error) {
          console.error('Error loading loadout:', data.error)
          return
        }

        console.log('Loaded loadout:', data.loadout)
        loadout.value = data.loadout
        validateLoadout() // Validate after loading
      } catch (error) {
        console.error('Error loading loadout:', error)
      }
    }

    // Save loadout to backend
    const saveLoadout = async () => {
      try {
        const response = await fetch('/api/loadout/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(loadout.value)
        })
        
        const data = await response.json()
        
        if (data.error) {
          console.error('Error saving loadout:', data.error)
          return
        }

        // Update local state with validated loadout from server
        loadout.value = data.loadout
      } catch (error) {
        console.error('Error saving loadout:', error)
      }
    }

    // Validate loadout against inventory (client-side)
    const validateLoadout = () => {
      const inventory = store.state.inventory
      let hasChanges = false

      for (const team of ['CT', 'T']) {
        for (const [slot, item] of Object.entries(loadout.value[team])) {
          if (item) {
            // Check if item still exists in inventory
            const exists = inventory.some(invItem => {
              const match = invItem.name === item.name && 
                invItem.wear === item.wear && 
                invItem.stattrak === item.stattrak &&
                invItem.weapon === item.weapon
              
              if (match) {
                console.log('Found matching item:', invItem)
              }
              return match
            })
            
            console.log('Validating item:', item, 'Exists:', exists)
            
            if (!exists) {
              console.log('Removing non-existent item:', item)
              delete loadout.value[team][slot]
              hasChanges = true
            }
          }
        }
      }

      // Only save if changes were made
      if (hasChanges) {
        saveLoadout()
      }
    }

    // Watch for inventory changes to validate loadout
    watch(() => store.state.inventory, () => {
      validateLoadout()
    }, { deep: true })

    // Get equipped item for a slot
    const getEquippedItem = (slot) => {
      return loadout.value[currentTeam.value][slot]
    }

    // Open skin selector
    const openSelector = (slot) => {
      currentSlot.value = slot
      showSelector.value = true
    }

    // Close skin selector
    const closeSelector = () => {
      showSelector.value = false
      currentSlot.value = null
    }

    // Check if an item is already equipped on the other team
    const isItemEquippedOnOtherTeam = (skin) => {
      const otherTeam = currentTeam.value === 'CT' ? 'T' : 'CT'
      return Object.values(loadout.value[otherTeam]).some(item => 
        item && 
        item.weapon === skin.weapon && 
        item.name === skin.name && 
        item.wear === skin.wear && 
        item.stattrak === skin.stattrak &&
        item.float_value === skin.float_value
      )
    }

    // Equip a skin
    const equipSkin = async (skin) => {
      const team = currentTeam.value
      const slot = currentSlot.value
      
      if (skin) {
        console.log('Equipping skin:', skin)
        // Check if already equipped on other team
        if (isItemEquippedOnOtherTeam(skin)) {
          alert('This item is already equipped on the other team!')
          closeSelector()
          return
        }
        // Create a deep copy of the skin to prevent reference issues
        loadout.value[team][slot] = JSON.parse(JSON.stringify(skin))
      } else {
        delete loadout.value[team][slot]
      }
      
      try {
        const response = await fetch('/api/loadout/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(loadout.value)
        })
        
        const data = await response.json()
        
        if (data.error) {
          console.error('Error saving loadout:', data.error)
          return
        }

        // Update local state with validated loadout from server
        loadout.value = data.loadout
      } catch (error) {
        console.error('Error saving loadout:', error)
      } finally {
        closeSelector()
      }
    }

    // Get skin image path
    const getSkinImagePath = (item) => {
      if (item.is_sticker) {
        // For stickers, use the case_type to determine the folder
        const capsuleType = item.case_type || item.capsule_type
        return `/sticker_skins/${capsuleType}/${item.image}`
      }
      const casePath = CASE_MAPPING[item.case_type] || 'weapon_case_1'
      if (!item.image) {
        // Construct image filename from weapon and name
        const weaponName = item.weapon.toLowerCase()
          .replace('-', '')
          .replace(' ', '')
          .replace('553', '553')
          .replace('galil ar', 'galil')
          .replace('galilar', 'galil')
        const skinName = item.name.toLowerCase().replace(/ /g, '_')
        return `/skins/${casePath}/${weaponName}_${skinName}.png`
      }
      return `/skins/${casePath}/${item.image}`
    }

    // Load saved loadout on mount
    onMounted(() => {
      loadSavedLoadout()
    })

    // Add getRarityColor function
    function getRarityColor(rarity) {
      const colors = {
        'CONTRABAND': 'bg-gradient-to-r from-amber-500 to-amber-600',
        'GOLD': 'bg-gradient-to-r from-[#FFD700] to-[#FFA500]',
        'RED': 'bg-gradient-to-r from-red-500 to-red-600',
        'PINK': 'bg-gradient-to-r from-pink-500 to-pink-600',
        'PURPLE': 'bg-gradient-to-r from-purple-500 to-purple-600',
        'BLUE': 'bg-gradient-to-r from-blue-500 to-blue-600'
      }
      return colors[rarity] || 'bg-gradient-to-r from-gray-500 to-gray-600'
    }

    // Get available skins for current slot
    const getAvailableSkins = () => {
      return store.state.inventory.filter(item => {
        // Skip cases and stickers
        if (item.is_case || item.is_sticker) {
          return false
        }

        // For knives
        if (currentSlot.value === 'knife') {
          const knives = ['knife', 'karambit', 'bayonet', 'butterfly', 'm9 bayonet', 'flip', 'gut', 'huntsman', 'falchion', 'bowie', 'shadow daggers', 'ursus', 'navaja', 'stiletto', 'talon', 'classic', 'paracord', 'survival', 'skeleton', 'nomad']
          return knives.some(knifeType => item.weapon?.toLowerCase().includes(knifeType))
        }
        // For gloves
        if (currentSlot.value === 'glove') {
          return item.weapon?.toLowerCase().includes('glove')
        }
        // For other weapons, normalize the names for comparison
        const itemWeapon = item.weapon?.toLowerCase()
          .replace('-', '')
          .replace(' ', '')
          .replace('553', '553')
          .replace('galil ar', 'galil')
          .replace('galilar', 'galil')
        const slotWeapon = currentSlot.value.toLowerCase()
        return itemWeapon === slotWeapon
      }).filter(item => !isItemEquippedOnOtherTeam(item)) // Filter out items equipped on other team
    }

    return {
      currentTeam,
      currentCategory,
      categoryIcons,
      getCategoryName,
      getWeaponsForCategory,
      showSelector,
      currentSlot,
      getEquippedItem,
      openSelector,
      closeSelector,
      getAvailableSkins,
      equipSkin,
      getSkinImagePath,
      getWeaponName,
      getRarityColor,
    }
  }
}
</script> 