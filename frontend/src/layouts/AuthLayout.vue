<template>
  <div class="min-h-screen bg-slate-50">
    <div class="mx-auto flex min-h-screen max-w-6xl items-center justify-center px-4 py-8">
      <div class="w-full overflow-hidden rounded-[32px] border border-slate-200 bg-white shadow-2xl">
        <div class="grid lg:grid-cols-[1.1fr_0.9fr]">
          <div class="hidden bg-gradient-to-br from-pramuka-700 via-pramuka-600 to-amber-500 p-10 text-white lg:flex lg:flex-col lg:justify-between">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.3em] text-pramuka-100">Pramuka Kwarda Jabar</p>
              <h1 class="mt-4 text-3xl font-semibold leading-tight">SuperApp untuk operasional dan pelaporan program.</h1>
              <p class="mt-4 max-w-md text-sm text-pramuka-100/90">Pantau progres, akses dashboard, dan kelola informasi program secara terpadu.</p>
            </div>
            <div class="rounded-2xl border border-white/20 bg-white/10 p-4 text-sm backdrop-blur">
              Akses aman, pengalaman yang konsisten, dan navigasi cepat untuk tim administrasi.
            </div>
          </div>
          <div class="flex items-center justify-center bg-white p-6 sm:p-10">
            <router-view />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
