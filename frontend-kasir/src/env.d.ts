/// <reference types="vite/client" />

export {}

declare global {
  interface ImportMetaEnv {
    readonly VITE_API_URL?: string
  }
}

declare module 'vue-router' {
  interface RouteMeta {
    public?: boolean
  }
}
