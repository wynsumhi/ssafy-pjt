import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'intro',
      component: () => import('@/views/IntroView.vue'),
      meta: { title: '지구깡 - 지역 구석구석을 깡하세요' },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { title: '로그인 - 지구깡', requiresGuest: true },
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('@/views/auth/SignupView.vue'),
      meta: { title: '회원가입 - 지구깡', requiresGuest: true },
    },
    {
      path: '/random',
      name: 'random',
      component: () => import('@/views/RandomView.vue'),
      meta: { title: '랜덤 - 지구깡' },
    },
    {
      path: '/articles/list',
      name: 'articles-list',
      component: () => import('@/views/articles/ArticleListView.vue'),
      meta: { title: '피드 목록 - 지구깡' },
    },
    {
      path: '/articles/:id',
      name: 'article-detail',
      component: () => import('@/views/articles/ArticleDetailView.vue'),
      meta: { title: '게시글 상세 - 지구깡' },
    },
    {
      path: '/articles/create',
      name: 'articles-create',
      component: () => import('@/views/articles/ArticleCreateView.vue'),
      meta: { title: '게시글 작성 - 지구깡', requiresAuth: false },
    },
    {
      path: '/articles/edit/:id',
      name: 'articles-edit',
      component: () => import('@/views/articles/ArticleEditView.vue'),
      meta: { title: '게시글 수정 - 지구깡', requiresAuth: false },
    },
    {
      path: '/places/:place_cid',
      name: 'place-detail',
      component: () => import('@/views/places/PlaceDetailView.vue'),
      meta: { title: '장소 상세 - 지구깡' },
    },
    {
      path: '/profile/:username',
      name: 'profile',
      component: () => import('@/views/profile/ProfileView.vue'),
      meta: { title: '프로필 - 지구깡' },
    },
    // 프로필에서 본인이 작성한 게시글 목록
    {
      path: '/profile/articles',
      name: 'profile-articles',
      component: () => import('@/views/profile/ArticleView.vue'),
      meta: { title: '내 게시글 - 지구깡' },
    },
    // 저장한 장소 목록
    {
      path: '/profile/favorites',
      name: 'profile-saved-places',
      component: () => import('@/views/profile/SavedPlacesView.vue'),
      meta: { title: '저장한 장소 목록 - 지구깡' },
    },
    // 좋아요한 게시글 목록
    {
      path: '/profile/liked-articles',
      name: 'profile-liked-articles',
      component: () => import('@/views/profile/LikedArticlesView.vue'),
      meta: { title: '좋아요한 게시글 목록 - 지구깡' },
    },
    // 프로필 수정
    {
      path: '/profile/edit',
      name: 'profile-edit',
      component: () => import('@/views/profile/ProfileEditView.vue'),
      meta: { title: '저장한 장소/좋아요 목록 - 지구깡' },
    },
    // 비밀번호 변경
    {
      path: '/profile/password',
      name: 'profile-password',
      component: () => import('@/views/profile/PasswordChangeView.vue'),
      meta: { title: '저장한 장소/좋아요 목록 - 지구깡' },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      redirect: '/',
    },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

export default router
