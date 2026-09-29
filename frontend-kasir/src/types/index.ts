export interface Product {
  id: string;
  sku: string;
  barcode: string | null;
  name: string;
  categoryId: string;
  categoryName: string;
  unit: string;
  sellingPrice: number;
  stock: number;
  minimumStock: number;
  stockStatus: 'OK' | 'LOW' | 'OUT';
  imageUrl: string | null;
  isActive: boolean;
}

export interface Category {
  id: string;
  name: string;
  description: string;
  isActive: boolean;
}

export interface CartItem {
  productId: string;
  sku: string;
  name: string;
  price: number;
  quantity: number;
  stock: number;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface Paginated<T> extends ApiResponse<T[]> {
  meta: { page: number; limit: number; total: number; totalPages: number };
}