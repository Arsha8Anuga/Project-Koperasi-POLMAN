import { api } from './apiClient';
import type { Paginated, Product, Category, ApiResponse } from '../types';

export const productApi = {
  getProducts: (params?: { search?: string; categoryId?: string; page?: number; limit?: number }) =>
    api.get<Paginated<Product>>('/products', { params }).then((res) => res.data),

  getCategories: () =>
    api.get<ApiResponse<Category[]>>('/categories', { params: { isActive: true } }).then((res) => res.data),
};