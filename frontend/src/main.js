import { createApp } from 'vue'
<<<<<<< HEAD
import App from './App.vue'
import router from './router'
import './style.css'

createApp(App).use(router).mount('#app')
=======
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'
import './style.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Toast, {
  transition: 'Vue-Toastification__bounce',
  maxToasts: 5,
  newestOnTop: true
})

app.mount('#app')
>>>>>>> b0b9cda (feat: initialize Vue 3 project with Vite)
