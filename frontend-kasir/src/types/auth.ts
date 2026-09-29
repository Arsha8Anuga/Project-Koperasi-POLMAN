export interface User {
  id: string;
  username: string;
  name: string;
  role: 'KASIR' | 'LOGISTIK' | 'OWNER' | 'ADMIN';
}

export interface LoginPayload {
  username: string;
  password: string;
  app: 'KASIR'; // Sesuai spesifikasi BE-1
}

export interface LoginResponse {
  token: string;
  user: User;
}