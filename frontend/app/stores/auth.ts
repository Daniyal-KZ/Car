import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: process.client ? localStorage.getItem('token') : null,
    user: null as any
  }),

  getters: {
    isLoggedIn: (state) => !!state.token
  },

  actions: {
    async login(username: string, password: string) {
      const config = useRuntimeConfig()

      const form = new URLSearchParams()
      form.append('username', username)
      form.append('password', password)

      const res: any = await $fetch(`${config.public.apiBase}/auth/login`, {
        method: 'POST',
        body: form,
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })

      this.token = res.access_token
      if (process.client) {
        try {
          localStorage.setItem('token', res.access_token)
        } catch {}
      }

      await this.fetchMe()
    },

    async fetchMe() {
      if (!this.token) return

      const config = useRuntimeConfig()

      this.user = await $fetch(`${config.public.apiBase}/users/me`, {
        headers: {
          Authorization: `Bearer ${this.token}`
        }
      })
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    }
  }
})
