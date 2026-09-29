import type { ClassValue } from 'clsx'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/** Gabung class Tailwind tanpa bentrok (dipakai semua komponen shadcn di components/ui). */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
