import { defineStore } from 'pinia'

type User = {
  id: number
  username: string
  email: string
  phone?: string | null
  role?: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    isAuth: false,
    token: null as string | null,
    inited: false
  }),

  actions: {
    async init() {
      // чтобы init не дергался по кругу
      if (this.inited) return
      this.inited = true

      if (!process.client) return

      const token = localStorage.getItem('access_token')
      const savedUser = localStorage.getItem('user')

      if (!token) {
        this.logout()
        return
      }

      this.token = token

      if (savedUser) {
        try {
          this.user = JSON.parse(savedUser)
          this.isAuth = true
        } catch {
          // если мусор в localStorage
          localStorage.removeItem('user')
        }
      }

      // пробуем обновить user с бэка
      try {
        await this.fetchMe()
      } catch (e: any) {
        // если сервер недоступен — не выходим, просто считаем что оффлайн
        if (e?.message?.includes('Сервер недоступен')) return

        // если токен умер/401 — выходим
        this.logout()
      }
    },

    async fetchMe() {
      const config = useRuntimeConfig()

      if (!this.token) {
        throw new Error('Нет токена. Войди снова.')
      }

      try {
        const me = await $fetch<User>(`${config.public.apiBase}/users/me`, {
          headers: { Authorization: `Bearer ${this.token}` }
        })

        this.user = me
        this.isAuth = true

        if (process.client) {
          localStorage.setItem('user', JSON.stringify(me))
        }

        return me
      } catch (e: any) {
        const status = e?.status || e?.response?.status

        // ❗ сервер офф / сеть / CORS
        if (!status) {
          throw new Error('Сервер недоступен. Проверь, запущен ли бекенд.')
        }

        // ❗ токен неверный/истек
        if (status === 401) {
          throw new Error('Сессия истекла или токен неверный. Войди снова.')
        }

        throw new Error(`Ошибка профиля (${status}).`)
      }
    },

    async login(username: string, password: string) {
      const config = useRuntimeConfig()
      const form = new URLSearchParams({ username, password })

      try {
        const data = await $fetch<{ access_token: string }>(
          `${config.public.apiBase}/auth/login`,
          { method: 'POST', body: form }
        )

        this.token = data.access_token
        this.isAuth = true

        if (process.client) {
          localStorage.setItem('access_token', data.access_token)
        }

        await this.fetchMe()
      } catch (e: any) {
        const status = e?.status || e?.response?.status

        if (!status) throw new Error('Сервер недоступен.')

        if (status === 401) throw new Error('Неверный логин или пароль')

        if (status === 422) throw new Error('Неверные данные формы (422). Проверь поля.')

        throw new Error(`Ошибка входа (${status}).`)
      }
    },

    logout() {
      this.user = null
      this.isAuth = false
      this.token = null
      this.inited = false

      if (process.client) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
      }
    }
  }
})