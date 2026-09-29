import { defineStore } from 'pinia';
import type { CartItem, Product } from '../types';

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: JSON.parse(localStorage.getItem('cart_items') || '[]') as CartItem[],
  }),
  getters: {
    totalQty: (state) => state.items.reduce((acc, item) => acc + item.quantity, 0),
    totalAmount: (state) => state.items.reduce((acc, item) => acc + item.price * item.quantity, 0),
  },
  actions: {
    saveToLocalStorage() {
      localStorage.setItem('cart_items', JSON.stringify(this.items));
    },
    addItem(product: Product) {
      if (product.stock <= 0) return;

      const existing = this.items.find((i) => i.productId === product.id);
      if (existing) {
        if (existing.quantity < product.stock) {
          existing.quantity++;
        }
      } else {
        this.items.push({
          productId: product.id,
          sku: product.sku,
          name: product.name,
          price: product.sellingPrice,
          quantity: 1,
          stock: product.stock,
        });
      }
      this.saveToLocalStorage();
    },
    updateQty(productId: string, qty: number) {
      const item = this.items.find((i) => i.productId === productId);
      if (item) {
        if (qty <= 0) {
          this.removeItem(productId);
        } else if (qty <= item.stock) {
          item.quantity = qty;
          this.saveToLocalStorage();
        }
      }
    },
    removeItem(productId: string) {
      this.items = this.items.filter((i) => i.productId !== productId);
      this.saveToLocalStorage();
    },
    clearCart() {
      this.items = [];
      localStorage.removeItem('cart_items');
    },
  },
});