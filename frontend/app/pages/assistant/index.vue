<script setup lang="ts">

definePageMeta({
  layout:"assistant"
})

const router = useRouter()
const { createChat } = useAssistant()

onMounted(()=>{

const chat = createChat()

router.replace(`/assistant/${chat.id}`)

})

</script>

<template>
<div />
</template>
