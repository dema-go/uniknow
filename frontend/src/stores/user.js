import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref({
    id: '',
    name: '',
    avatar: ''
  })

  function setToken(t) {
    token.value = t
    localStorage.setItem('token', t)
  }

  function logout() {
    token.value = ''
    userInfo.value = { id: '', name: '', avatar: '' }
    localStorage.removeItem('token')
  }

  return {
    token,
    userInfo,
    setToken,
    logout
  }
})
