<script setup lang="ts">
import { ChevronDownIcon, LogOutIcon } from '@lucide/vue'
import { computed } from 'vue'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

/** Menu akun di pojok kanan atas — ISI FILE INI IDENTIK di kedua app. */
const props = defineProps<{ name?: string; subtitle?: string }>()
const emit = defineEmits<{ logout: [] }>()

const initials = computed(() =>
  (props.name ?? '?')
    .split(' ')
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase(),
)
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="ghost" class="h-10 gap-2.5 px-2">
        <Avatar class="size-8">
          <AvatarFallback class="bg-primary text-xs font-bold text-primary-foreground">{{ initials }}</AvatarFallback>
        </Avatar>
        <span class="hidden text-left leading-tight md:block">
          <span class="block text-sm font-semibold">{{ name }}</span>
          <span class="block text-xs font-normal text-muted-foreground">{{ subtitle }}</span>
        </span>
        <ChevronDownIcon class="hidden size-4 text-muted-foreground md:block" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="w-56">
      <DropdownMenuLabel>
        <p class="truncate font-semibold">{{ name }}</p>
        <p class="text-xs font-normal text-muted-foreground">{{ subtitle }}</p>
      </DropdownMenuLabel>
      <DropdownMenuSeparator />
      <DropdownMenuItem variant="destructive" @select="emit('logout')">
        <LogOutIcon /> Keluar
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
