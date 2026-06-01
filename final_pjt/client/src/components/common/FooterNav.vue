<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-section">
        <div class="logo">🌍 지구깡</div>
        <p class="tagline">지역 구석구석을 깡(언박싱)하세요!</p>
      </div>

      <div class="footer-section">
        <h4>서비스</h4>
        <router-link to="/map">지도</router-link>
        <router-link to="/my-page">마이페이지</router-link>
      </div>

      <div class="footer-section">
        <h4>소개</h4>
        <router-link to="/">홈</router-link>
        <a href="https://github.com/MRDD-jigu/jigukkang" target="_blank">GitHub</a>
      </div>
    </div>

    <div class="copyright">
      <p>
        © 2025 지구깡 (Jigukkang). All rights reserved. <br />
        해당 서비스는 비짓서울 API를 활용하여 제작되었습니다.
      </p>
    </div>
  </footer>
</template>

<style>
.footer {
  background: #2c3e50;
  color: white;
  padding: 3rem 2rem 1rem;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 3rem;
  margin-bottom: 2rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
}

.footer-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;

  .logo {
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
  }

  .tagline {
    color: #bdc3c7;
    font-size: 0.9rem;
  }

  h4 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
    color: #ecf0f1;
  }

  a {
    color: #bdc3c7;
    font-size: 0.9rem;
    transition: color 0.2s;

    &:hover {
      color: #ff6b6b;
    }
  }
}

.copyright {
  text-align: center;
  padding-top: 2rem;
  border-top: 1px solid #34495e;
  color: #95a5a6;
  font-size: 0.875rem;

  p {
    margin: 0.25rem 0;
  }
}
</style>
