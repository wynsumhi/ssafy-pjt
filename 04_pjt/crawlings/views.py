from django.shortcuts import render, redirect
from .models import Comment
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from collections import defaultdict
import os
from openai import OpenAI

# OpenAI API 클라이언트 초기화 (환경변수에서 API 키 사용)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_sentiment_analysis(comments):
    company_comments = defaultdict(list)
    for comment in comments:
        company_comments[comment.company_name].append(comment.content)

    result = {}
    for company, comment_list in company_comments.items():
        if not comment_list:
            continue

        all_comments = "\n".join(comment_list[:20]) # 댓글 20개까지 분석
        try:
            response = client.chat.completions.create(
                model="gpt-5-nano",   # 더 빠르고 저렴한 최신 모델 권장
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 주식 투자 관련 댓글들을 분석하여 전체적인 여론을 파악하는 전문가입니다."
                    },
                    {
                        "role": "user",
                        "content": f"""다음은 '{company}' 종목에 대한 투자자들의 댓글들입니다:

                        {all_comments}

                    위 댓글들을 종합적으로 분석하여 다음 형식으로 답변해주세요:
                    1. 첫 번째 줄: '긍정', '중립', '부정' 중 하나만 작성
                    2. 두 번째 줄부터: 전체적인 여론 분석을 자연스러운 문체로 2-3문장으로 요약 (반드시 '~입니다' 말투 사용)"""
                    }
                ],
                max_completion_tokens=5000,
                temperature=1
            )
            
            analysis_result = response.choices[0].message.content.strip()
            lines = analysis_result.split('\n', 1)

            if len(lines) >= 2 and lines[0] in ['긍정', '중립', '부정']:
                result[company] = {
                    'sentiment': lines[0],
                    'summary': lines[1].strip(),
                    'total_count': len(comment_list)
                }
            else:
                result[company] = {
                    'sentiment': '중립',
                    'summary': '댓글 분석 중 오류가 발생했습니다.',
                    'total_count': len(comment_list)
                }

        except Exception as e:
            result[company] = {
                'sentiment': '중립',
                'summary': 'API 오류로 인해 분석할 수 없습니다.',
                'total_count': len(comment_list)
            }
    return result


def index(request):
    comments = []
    if request.method == 'POST':
        company_name = request.POST.get('company_name')

        # Selenium 크롤링 (참고 파일 방식)
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        try:
            driver.get('https://www.tossinvest.com/')
            time.sleep(1)
            body = driver.find_element(By.TAG_NAME, 'body')
            body.send_keys('/')
            time.sleep(1)
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            search_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='검색어를 입력해주세요']"))
            )
            search_input.send_keys(company_name)
            search_input.send_keys(Keys.ENTER)
            time.sleep(1)
            WebDriverWait(driver, 15).until(EC.url_contains("/order"))
            current_url = driver.current_url
            try:
                stock_code = current_url.split("/")[current_url.split("/").index("stocks") + 1]
            except Exception:
                stock_code = None
            if stock_code:
                community_url = f"https://www.tossinvest.com/stocks/{stock_code}/community"
                driver.get(community_url)
                time.sleep(1)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "main article"))
                )
                # 댓글 수집 (최대 20개, 중복 제거)
                crawled_comments = set()
                last_height = driver.execute_script("return document.body.scrollHeight")
                for _ in range(10):
                    spans = driver.find_elements(By.CSS_SELECTOR, "article.comment span.tw-1r5dc8g0._60z0ev1")
                    for span in spans:
                        text = span.text.strip()
                        if text:
                            crawled_comments.add(text)
                    if len(crawled_comments) >= 20:
                        break
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                for c in list(crawled_comments)[:20]:
                    Comment.objects.create(company_name=company_name, content=c)
        finally:
            driver.quit()
        return redirect('crawlings:index')
    # GET 요청: DB에서 전체 댓글 조회 (최신순)
    comments = Comment.objects.all().order_by('-created_at')

    
    # 감정 분석 결과 생성
    sentiment_analysis = get_sentiment_analysis(comments)
    
    return render(request, 'crawlings/index.html', {
        'comments': comments,
        'sentiment_analysis': sentiment_analysis
    })

# 댓글 삭제 뷰
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from django.urls import reverse

@require_POST
def delete_comment(request, comment_id):
    comment = Comment.objects.filter(id=comment_id).first()
    if comment:
        comment.delete()
    return HttpResponseRedirect(reverse('crawlings:index'))