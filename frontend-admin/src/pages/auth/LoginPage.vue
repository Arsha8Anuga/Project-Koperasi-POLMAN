<script setup lang="ts">
import { ChartColumnIcon, CircleAlertIcon, ShieldCheckIcon, TruckIcon } from '@lucide/vue'
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BrandMark from '@/components/common/BrandMark.vue'
import ThemeToggle from '@/components/common/ThemeToggle.vue'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Field, FieldGroup, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'
import { errorMessage } from '@/services/apiClient'
import { useAuthStore } from '@/stores/auth'
import { BRAND } from '@/utils/brand'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  if (!username.value.trim() || !password.value) {
    error.value = 'Username dan password wajib diisi'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await auth.login(username.value.trim(), password.value)
    router.push((route.query.redirect as string) || { name: 'dashboard' })
  } catch (e) {
    error.value = errorMessage(e, 'Login gagal')
  } finally {
    loading.value = false
  }
}

const roles = [
  { icon: ChartColumnIcon, title: 'Owner', text: 'Riwayat transaksi, arus kas, laba kotor, produk terlaris' },
  { icon: TruckIcon, title: 'Logistik', text: 'Produk, supplier, restock, dan pemantauan stok' },
  { icon: ShieldCheckIcon, title: 'Admin', text: 'Pengguna, anggota koperasi, dan audit trail' },
]
</script>

<template>
  <div class="grid min-h-screen lg:grid-cols-2">
    <aside class="relative hidden overflow-hidden bg-sidebar p-12 text-sidebar-foreground lg:flex lg:flex-col">
      <div class="pointer-events-none absolute -top-40 -right-40 size-[28rem] rounded-full bg-sidebar-primary/25 blur-3xl" />
      <div class="relative flex items-center gap-3">
        <BrandMark />
        <p class="text-lg font-bold text-sidebar-accent-foreground">{{ BRAND.name }}</p>
      </div>
      <div class="relative mt-auto max-w-md">
        <h2 class="text-3xl leading-tight font-bold text-sidebar-accent-foreground">Satu panel untuk seluruh pengelolaan toko.</h2>
        <ul class="mt-8 space-y-5">
          <li v-for="r in roles" :key="r.title" class="flex gap-4">
            <span class="flex size-10 shrink-0 items-center justify-center rounded-lg bg-sidebar-accent text-sidebar-accent-foreground">
              <component :is="r.icon" class="size-[19px]" />
            </span>
            <div>
              <p class="font-semibold text-sidebar-accent-foreground">{{ r.title }}</p>
              <p class="text-sm">{{ r.text }}</p>
            </div>
          </li>
        </ul>
      </div>
    </aside>

    <main class="relative flex items-center justify-center p-6">
      <div class="absolute top-4 right-4"><ThemeToggle /></div>
      <div class="w-full max-w-sm">
        <div class="mb-8">
          <div class="mb-6 lg:hidden"><BrandMark size="lg" /></div>
          <h1 class="text-2xl font-bold">Masuk ke Panel Admin</h1>
          <p class="mt-1 text-sm text-muted-foreground">Untuk akun Owner, Logistik, dan Admin.</p>
        </div>

        <form @submit.prevent="submit">
          <FieldGroup>
            <Alert v-if="error" variant="destructive">
              <CircleAlertIcon />
              <AlertDescription>{{ error }}</AlertDescription>
            </Alert>
            <Field>
              <FieldLabel for="username">Username</FieldLabel>
              <Input id="username" v-model="username" class="h-10" autocomplete="username" autofocus />
            </Field>
            <Field>
              <FieldLabel for="password">Password</FieldLabel>
              <Input id="password" v-model="password" type="password" class="h-10" autocomplete="current-password" />
            </Field>
            <Button type="submit" size="lg" class="w-full" :disabled="loading">
              <Spinner v-if="loading" />
              {{ loading ? 'Memproses…' : 'Masuk' }}
            </Button>
          </FieldGroup>
        </form>
      </div>
    </main>
  </div>
</template>
