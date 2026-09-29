<script setup lang="ts">
import { EllipsisIcon, KeyRoundIcon, PlusIcon, PowerIcon, SquarePenIcon } from '@lucide/vue'
import { reactive, ref } from 'vue'
import ActiveBadge from '@/components/common/ActiveBadge.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import FilterToggle from '@/components/common/FilterToggle.vue'
import Modal from '@/components/common/Modal.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import SearchInput from '@/components/common/SearchInput.vue'
import FormField from '@/components/form/FormField.vue'
import DataTable from '@/components/table/DataTable.vue'
import TablePagination from '@/components/table/TablePagination.vue'
import type { Column } from '@/components/table/types'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { DialogFooter } from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { Spinner } from '@/components/ui/spinner'
import { usePagination } from '@/composables/usePagination'
import { userApi } from '@/services/api'
import { ApiException, errorMessage } from '@/services/apiClient'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import type { Role, User } from '@/types/api'
import { formatDate } from '@/utils/format'

const auth = useAuthStore()
const toast = useToast()
const roles: { value: Role; label: string }[] = [
  { value: 'KASIR', label: 'Kasir' },
  { value: 'LOGISTIK', label: 'Logistik' },
  { value: 'OWNER', label: 'Owner' },
  { value: 'ADMIN', label: 'Admin' },
]
const roleLabel = (r: Role) => roles.find((x) => x.value === r)?.label ?? r

const list = usePagination<User, { search: string; role: Role | ''; isActive: boolean | '' }>((q) => userApi.list(q), {
  search: '',
  role: '',
  isActive: '',
})
list.load()

const activeOptions: { value: boolean | ''; label: string }[] = [
  { value: '', label: 'Semua' },
  { value: true, label: 'Aktif' },
  { value: false, label: 'Nonaktif' },
]

const columns: Column[] = [
  { key: 'name', label: 'Pengguna' },
  { key: 'role', label: 'Peran' },
  { key: 'isActive', label: 'Status' },
  { key: 'createdAt', label: 'Dibuat' },
  { key: 'actions', label: '', align: 'right' },
]
const isSelf = (u: User) => u.id === auth.user?.id

// ---- buat / ubah ----
const formOpen = ref(false)
const editing = ref<User | null>(null)
const form = reactive({ name: '', username: '', password: '', role: 'KASIR' as Role })
const errors = reactive<Record<string, string>>({})
const saving = ref(false)

function openForm(u: User | null) {
  editing.value = u
  Object.assign(form, { name: u?.name ?? '', username: u?.username ?? '', password: '', role: u?.role ?? 'KASIR' })
  for (const k of Object.keys(errors)) delete errors[k]
  formOpen.value = true
}

async function save() {
  for (const k of Object.keys(errors)) delete errors[k]
  if (!form.name.trim()) errors.name = 'Nama wajib diisi'
  if (!editing.value) {
    if (!/^[a-z0-9._]{3,32}$/.test(form.username.trim().toLowerCase()))
      errors.username = '3–32 karakter: huruf kecil, angka, titik, underscore'
    if (form.password.length < 8) errors.password = 'Minimal 8 karakter'
  }
  if (Object.keys(errors).length) return
  saving.value = true
  try {
    if (editing.value) await userApi.update(editing.value.id, { name: form.name.trim(), role: form.role })
    else
      await userApi.create({ name: form.name.trim(), username: form.username.trim(), password: form.password, role: form.role })
    toast.success(editing.value ? 'Pengguna diperbarui' : `Pengguna ${form.username.trim().toLowerCase()} dibuat`)
    formOpen.value = false
    list.reload()
  } catch (e) {
    if (e instanceof ApiException) Object.assign(errors, e.fieldErrors())
    if (!Object.keys(errors).length) errors.name = errorMessage(e)
  } finally {
    saving.value = false
  }
}

// ---- reset password ----
const resetting = ref<User | null>(null)
const newPassword = ref('')
const resetError = ref('')
const resetSaving = ref(false)
function openReset(u: User) {
  resetting.value = u
  newPassword.value = ''
  resetError.value = ''
}
async function doReset() {
  if (!resetting.value) return
  if (newPassword.value.length < 8) return (resetError.value = 'Minimal 8 karakter')
  resetSaving.value = true
  try {
    await userApi.resetPassword(resetting.value.id, newPassword.value)
    toast.success(`Password ${resetting.value.username} direset`)
    resetting.value = null
  } catch (e) {
    resetError.value = errorMessage(e)
  } finally {
    resetSaving.value = false
  }
}

// ---- aktif / nonaktif ----
const target = ref<User | null>(null)
const toggling = ref(false)
async function toggle() {
  if (!target.value) return
  toggling.value = true
  try {
    const u = await userApi.setStatus(target.value.id, !target.value.isActive)
    toast.success(`${u.name} ${u.isActive ? 'diaktifkan' : 'dinonaktifkan'}`)
    target.value = null
    list.reload()
  } catch (e) {
    toast.error(errorMessage(e))
  } finally {
    toggling.value = false
  }
}
</script>

<template>
  <PageHeader title="Pengguna" subtitle="Pengguna tidak dihapus — nonaktifkan supaya jejak audit tetap utuh.">
    <Button @click="openForm(null)"><PlusIcon /> Pengguna baru</Button>
  </PageHeader>

  <Card class="gap-0 overflow-hidden py-0">
    <div class="flex flex-wrap items-center gap-2 border-b p-4">
      <SearchInput v-model="list.filters.search" placeholder="Cari nama atau username" />
      <NativeSelect v-model="list.filters.role" aria-label="Peran">
        <NativeSelectOption value="">Semua peran</NativeSelectOption>
        <NativeSelectOption v-for="r in roles" :key="r.value" :value="r.value">{{ r.label }}</NativeSelectOption>
      </NativeSelect>
      <FilterToggle v-model="list.filters.isActive" :options="activeOptions" label="Status" />
    </div>
    <ErrorAlert v-if="list.error.value" :message="list.error.value" class="m-4 w-auto" />
    <DataTable :columns="columns" :rows="list.rows.value" :loading="list.loading.value" row-key="id" empty="Tidak ada pengguna">
      <template #cell-name="{ row }">
        <p class="flex items-center gap-1.5 font-semibold">
          {{ row.name }} <Badge v-if="isSelf(row)" variant="outline">Anda</Badge>
        </p>
        <p class="font-mono text-xs text-muted-foreground">{{ row.username }}</p>
      </template>
      <template #cell-role="{ row }"><Badge variant="soft">{{ roleLabel(row.role) }}</Badge></template>
      <template #cell-isActive="{ row }"><ActiveBadge :active="row.isActive" /></template>
      <template #cell-createdAt="{ row }"><span class="text-muted-foreground">{{ formatDate(row.createdAt) }}</span></template>
      <template #cell-actions="{ row }">
        <DropdownMenu :modal="false">
          <DropdownMenuTrigger as-child>
            <Button variant="ghost" size="icon-sm" :aria-label="`Aksi untuk ${row.username}`"><EllipsisIcon /></Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" class="w-44">
            <DropdownMenuItem @select="openForm(row)"><SquarePenIcon /> Ubah</DropdownMenuItem>
            <DropdownMenuItem @select="openReset(row)"><KeyRoundIcon /> Reset password</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem :variant="row.isActive ? 'destructive' : 'default'" :disabled="isSelf(row)" @select="target = row">
              <PowerIcon /> {{ row.isActive ? 'Nonaktifkan' : 'Aktifkan' }}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </template>
    </DataTable>
    <TablePagination v-model="list.page.value" :meta="list.meta.value" :loading="list.loading.value" />
  </Card>

  <Modal :open="formOpen" :title="editing ? 'Ubah pengguna' : 'Pengguna baru'" @close="formOpen = false">
    <form class="space-y-4" @submit.prevent="save">
      <FormField label="Nama lengkap" for="u-name" required :error="errors.name">
        <Input id="u-name" v-model="form.name" :aria-invalid="!!errors.name || undefined" maxlength="60" />
      </FormField>
      <FormField
        label="Username"
        for="u-username"
        :required="!editing"
        :error="errors.username"
        :hint="editing ? 'Username tidak bisa diubah' : undefined"
      >
        <Input
          id="u-username"
          v-model="form.username"
          class="font-mono lowercase"
          :aria-invalid="!!errors.username || undefined"
          :disabled="!!editing"
          autocomplete="off"
        />
      </FormField>
      <FormField v-if="!editing" label="Password awal" for="u-pass" required :error="errors.password" hint="Minimal 8 karakter">
        <Input id="u-pass" v-model="form.password" type="password" :aria-invalid="!!errors.password || undefined" autocomplete="new-password" />
      </FormField>
      <FormField
        label="Peran"
        for="u-role"
        required
        :error="errors.role"
        :hint="editing && isSelf(editing) ? 'Anda tidak bisa mengubah peran sendiri' : undefined"
      >
        <NativeSelect id="u-role" v-model="form.role" class="w-full" :disabled="!!editing && isSelf(editing)">
          <NativeSelectOption v-for="r in roles" :key="r.value" :value="r.value">{{ r.label }}</NativeSelectOption>
        </NativeSelect>
      </FormField>
      <DialogFooter class="pt-2">
        <Button type="button" variant="outline" @click="formOpen = false">Batal</Button>
        <Button type="submit" :disabled="saving"><Spinner v-if="saving" /> Simpan</Button>
      </DialogFooter>
    </form>
  </Modal>

  <Modal :open="!!resetting" :title="`Reset password ${resetting?.username ?? ''}`" size="sm" @close="resetting = null">
    <form class="space-y-4" @submit.prevent="doReset">
      <FormField label="Password baru" for="new-pass" required :error="resetError" hint="Minimal 8 karakter">
        <Input id="new-pass" v-model="newPassword" type="password" :aria-invalid="!!resetError || undefined" autocomplete="new-password" />
      </FormField>
      <DialogFooter>
        <Button type="button" variant="outline" @click="resetting = null">Batal</Button>
        <Button type="submit" :disabled="resetSaving"><Spinner v-if="resetSaving" /> Reset</Button>
      </DialogFooter>
    </form>
  </Modal>

  <ConfirmModal
    :open="!!target"
    :title="target?.isActive ? 'Nonaktifkan pengguna?' : 'Aktifkan pengguna?'"
    :message="target?.isActive ? `${target?.name} langsung tidak bisa masuk, termasuk sesi yang sedang berjalan.` : `${target?.name} bisa masuk kembali.`"
    :confirm-text="target?.isActive ? 'Nonaktifkan' : 'Aktifkan'"
    :danger="target?.isActive"
    :loading="toggling"
    @confirm="toggle"
    @cancel="target = null"
  />
</template>
