import api from './api'

export default {
  getTrainings({ search = '', page = 1, limit = 6 } = {}) {
    const params = { page, limit }
    if (search) params.search = search
    return api.get('/lms/trainings', { params })
  },
  getTrainingMaterials(trainingId) {
    return api.get(`/lms/trainings/${trainingId}/materials`)
  },
  getQuiz(trainingId) {
    return api.get(`/lms/trainings/${trainingId}/quiz`)
  },
  getQuizQuestions(quizId) {
    return api.get(`/lms/quizzes/${quizId}/questions`)
  },
  submitQuiz(quizId, payload) {
    return api.post(`/lms/quizzes/${quizId}/submit`, payload)
  },
  enrollTraining(trainingId) {
    return api.post(`/lms/trainings/${trainingId}/enroll`)
  },
  getMyEnrollments() {
    return api.get('/lms/enrollments/me')
  },
  getCertificate(enrollmentId) {
    return api.get(`/lms/enrollments/${enrollmentId}/certificate`)
  }
}
