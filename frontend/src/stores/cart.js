// frontend/src/stores/cart.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { cartAPI } from '@/services/api'

export const useCartStore = defineStore('cart', () => {
    // State
    const cartDetails = ref(null)  // CartResponse от бэкенда
    const loading = ref(false)
    const error = ref(null)

    // Getters
    const items = computed(() => cartDetails.value?.items ?? [])

    const itemsCount = computed(() => cartDetails.value?.total_items ?? 0)

    const totalPrice = computed(() => Number(cartDetails.value?.total_price ?? 0))

    const hasItems = computed(() => itemsCount.value > 0)

    // Actions

    /**
     * Загрузить корзину с бэкенда (состояние хранится в Redis по cookie)
     */
    async function fetchCart() {
        loading.value = true
        error.value = null
        try {
            const response = await cartAPI.getCart()
            cartDetails.value = response.data
        } catch (err) {
            console.error('Error fetching cart:', err)
            error.value = 'Failed to load cart'
        } finally {
            loading.value = false
        }
    }

    /**
     * Добавить товар в корзину
     */
    async function addToCart(productId, quantity = 1) {
        loading.value = true
        error.value = null
        try {
            const response = await cartAPI.addItem(productId, quantity)
            cartDetails.value = response.data
            return true
        } catch (err) {
            console.error('Error adding to cart:', err)
            error.value = err.response?.data?.detail ?? 'Failed to add item'
            return false
        } finally {
            loading.value = false
        }
    }

    /**
     * Обновить количество товара в корзине
     */
    async function updateQuantity(productId, quantity) {
        if (quantity <= 0) {
            return removeFromCart(productId)
        }

        loading.value = true
        error.value = null
        try {
            const response = await cartAPI.updateItem(productId, quantity)
            cartDetails.value = response.data
            return true
        } catch (err) {
            console.error('Error updating cart:', err)
            error.value = err.response?.data?.detail ?? 'Failed to update item'
            return false
        } finally {
            loading.value = false
        }
    }

    /**
     * Удалить товар из корзины
     */
    async function removeFromCart(productId) {
        loading.value = true
        error.value = null
        try {
            const response = await cartAPI.removeItem(productId)
            cartDetails.value = response.data
            return true
        } catch (err) {
            console.error('Error removing from cart:', err)
            error.value = err.response?.data?.detail ?? 'Failed to remove item'
            return false
        } finally {
            loading.value = false
        }
    }

    /**
     * Очистить корзину
     */
    async function clearCart() {
        loading.value = true
        error.value = null
        try {
            await cartAPI.clearCart()
            cartDetails.value = null
            return true
        } catch (err) {
            console.error('Error clearing cart:', err)
            error.value = 'Failed to clear cart'
            return false
        } finally {
            loading.value = false
        }
    }

    return {
        // State
        cartDetails,
        loading,
        error,
        // Getters
        items,
        itemsCount,
        totalPrice,
        hasItems,
        // Actions
        fetchCart,
        addToCart,
        updateQuantity,
        removeFromCart,
        clearCart,
    }
})