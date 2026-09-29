import { defineStore } from 'pinia'
import type { CartItem, Product } from '@/types'

const STORAGE_KEY = 'kasir_cart'

function load(): CartItem[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]') as CartItem[]
  } catch {
    return []
  }
}

export const useCartStore = defineStore('cart', {
  state: () => ({ items: load() }),
  getters: {
    totalQty: (s) => s.items.reduce((n, i) => n + i.quantity, 0),
    /** Perkiraan untuk tampilan. Total yang SAH dihitung backend dari harga di database. */
    totalAmount: (s) => s.items.reduce((n, i) => n + i.price * i.quantity, 0),
    isEmpty: (s) => s.items.length === 0,
  },
  actions: {
    persist() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.items))
    },
    add(product: Product) {
      if (product.stock <= 0) return
      const existing = this.items.find((i) => i.productId === product.id)
      if (existing) {
        existing.stock = product.stock
        if (existing.quantity < product.stock) existing.quantity++
      } else {
        this.items.push({
          productId: product.id,
          sku: product.sku,
          name: product.name,
          unit: product.unit,
          price: product.sellingPrice,
          quantity: 1,
          stock: product.stock,
        })
      }
      this.persist()
    },
    setQty(productId: string, qty: number) {
      const item = this.items.find((i) => i.productId === productId)
      if (!item) return
      if (qty <= 0) return this.remove(productId)
      item.quantity = Math.min(qty, item.stock, 999)
      this.persist()
    },
    remove(productId: string) {
      this.items = this.items.filter((i) => i.productId !== productId)
      this.persist()
    },
    /** Samakan harga & batas stok keranjang dengan data katalog terbaru. */
    sync(products: Product[]) {
      const byId = new Map(products.map((p) => [p.id, p]))
      for (const item of this.items) {
        const p = byId.get(item.productId)
        if (!p) continue
        item.price = p.sellingPrice
        item.stock = p.stock
        if (item.quantity > p.stock) item.quantity = Math.max(p.stock, 0)
      }
      this.items = this.items.filter((i) => i.quantity > 0)
      this.persist()
    },
    clear() {
      this.items = []
      localStorage.removeItem(STORAGE_KEY)
    },
  },
})
