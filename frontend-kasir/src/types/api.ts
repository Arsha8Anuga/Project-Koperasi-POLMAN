export interface ApiResponse<T> {
  success: true
  message: string
  data: T
}

export interface Paginated<T> extends ApiResponse<T[]> {
  meta: { page: number; limit: number; total: number; totalPages: number }
}