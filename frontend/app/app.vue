<template>
  <div>
    <h1>Список пользователей</h1>
    <ul>
      <li v-for="user in users" :key="user.id">
        {{ user.username }} ({{ user.role }})
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const users = ref([])

onMounted(async () => {
  const res = await fetch('http://127.0.0.1:8000/users')
  const data = await res.json()
  users.value = data.users
})
</script>
