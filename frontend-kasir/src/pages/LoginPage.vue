<script setup lang="ts">
import { CircleAlertIcon } from '@lucide/vue'
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BrandMark from '@/components/common/BrandMark.vue'
import ThemeToggle from '@/components/common/ThemeToggle.vue'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Field, FieldGroup, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'
import { errorMessage } from '@/services/api'
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
    router.push((route.query.redirect as string) || { name: 'pos' })
  } catch (e) {
    error.value = errorMessage(e, 'Login gagal')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="relative flex min-h-screen items-center justify-center p-4">
    <div class="absolute top-4 right-4"><ThemeToggle /></div>

    <div class="w-full max-w-sm">
      <div class="mb-6 flex justify-center"><BrandMark size="lg" /></div>
      <Card>
        <CardHeader class="text-center">
          <CardTitle class="text-2xl font-bold">Masuk Kasir</CardTitle>
          <CardDescription>{{ BRAND.name }} · masuk dengan akun kasir</CardDescription>
        </CardHeader>
        <CardContent>
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
                <Input id="password" v-model="password" class="h-10" type="password" autocomplete="current-password" />
              </Field>
              <Button type="submit" size="lg" class="w-full" :disabled="loading">
                <Spinner v-if="loading" />
                {{ loading ? 'Memproses…' : 'Masuk' }}
              </Button>
            </FieldGroup>
          </form>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
