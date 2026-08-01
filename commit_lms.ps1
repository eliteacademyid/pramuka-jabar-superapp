cd frontend
git add src/services/lms.js
git commit -m "fitur(lms-ui): add API service wrapper for LMS endpoints" -m "Commit 21: Membuat service API di sisi Frontend untuk mempermudah pemanggilan endpoint backend LMS."

git add src/router/index.js
git commit -m "fitur(lms-ui): update router with LMS views" -m "Commit 22: Mendaftarkan rute (routes) baru di Vue Router untuk halaman-halaman LMS (Trainings, Detail, Quiz, Enrollments)."

git add src/components/AdminLayout.vue
git commit -m "fitur(lms-ui): add LMS menu to sidebar navigation" -m "Commit 23: Mengaktifkan menu 'Daftar Pelatihan' dan 'Pelatihanku' di sidebar AdminLayout agar user bisa mengakses LMS."

git add src/views/lms/TrainingsList.vue
git commit -m "fitur(lms-ui): implement Trainings List view" -m "Commit 24: Membuat halaman utama LMS untuk menampilkan daftar pelatihan yang bisa diikuti oleh staf."

git add src/views/lms/TrainingDetail.vue
git commit -m "fitur(lms-ui): implement Training Detail & Material views" -m "Commit 25: Membuat halaman detail yang memuat tombol Enroll dan menampilkan daftar modul materi bagi user yang sudah terdaftar."

git add src/views/lms/TrainingQuiz.vue
git commit -m "fitur(lms-ui): implement Training Quiz & Evaluation view" -m "Commit 26: Membuat UI untuk mengerjakan kuis pilihan ganda yang otomatis dinilai (auto-grading) ketika disubmit."

git add src/views/lms/MyEnrollments.vue
git commit -m "fitur(lms-ui): implement My Enrollments and E-Certificate view" -m "Commit 27: Membuat halaman riwayat pelatihan beserta fitur untuk melihat nomor seri dan keterangan e-certificate."
