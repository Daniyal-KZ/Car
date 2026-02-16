import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as any,
    isAuth: false,
    token: null as string | null
  }),

  actions: {
    async init() {
      if (process.client) {
        const token = localStorage.getItem('access_token')
        const savedUser = localStorage.getItem('user')
        if (token && savedUser) {
          this.token = token
          this.user = JSON.parse(savedUser)
          this.isAuth = true
          try {
            await this.fetchMe()
          } catch {
            this.logout()
          }
        }
      }
    },

    async fetchMe() {
      const config = useRuntimeConfig()
      this.user = await $fetch(`${config.public.apiBase}/users/me`, {
        headers: { Authorization: `Bearer ${this.token}` }
      })
      this.isAuth = true
      localStorage.setItem('user', JSON.stringify(this.user))
    },

    async login(username: string, password: string) {
      const config = useRuntimeConfig()
      const form = new URLSearchParams({ username, password })
      const data = await $fetch<{ access_token: string }>(`${config.public.apiBase}/auth/login`, {
        method: 'POST',
        body: form
      })
      this.token = data.access_token
      localStorage.setItem('access_token', data.access_token)
      await this.fetchMe()
    },

    logout() {
      this.user = null
      this.isAuth = false
      this.token = null
      if (process.client) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
      }
    }
  }
})