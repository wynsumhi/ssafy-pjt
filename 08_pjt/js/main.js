// 모듈 임포트
import config from './apikey.js';
import data from './data.js';

// 전역 변수
let map; // 카카오 지도 객체
let markers = []; // 마커 배열
let infowindows = []; // 인포윈도우 배열
let currentPolyline = null; // 현재 표시된 경로 폴리라인

// 멀티캠퍼스 역삼 좌표 (출발지)
const MULTICAMPUS_LOCATION = {
    lat: 37.5012743,
    lng: 127.039585
};

// 강남역 좌표 (초기 지도 중심)
const GANGNAM_STATION = {
    lat: 37.49818,
    lng: 127.027386
};

// DOM 요소
const regionSelect = document.getElementById('region-select');
const districtSelect = document.getElementById('district-select');
const bankSelect = document.getElementById('bank-select');
const searchBtn = document.getElementById('search-btn');
const resultMessage = document.getElementById('result-message');


// 페이지 로드 시 실행
function initApp() {
    initMap();
    initSelectBoxes();
    setupEventListeners();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    // 이미 DOMContentLoaded가 발생한 경우 즉시 초기화
    initApp();
}

/**
 * 지도 초기화 함수
 */
function initMap() {
    const container = document.getElementById('map');
    const options = {
        center: new kakao.maps.LatLng(GANGNAM_STATION.lat, GANGNAM_STATION.lng),
        level: 3
    };
    
    map = new kakao.maps.Map(container, options);
}

/**
 * 선택 박스 초기화
 */
function initSelectBoxes() {
    // 광역시/도 선택 박스 채우기
    data.mapInfo.forEach(region => {
        const option = document.createElement('option');
        option.value = region.name;
        option.textContent = region.name;
        regionSelect.appendChild(option);
    });
    
    // 은행 선택 박스 채우기 (초기에는 비활성화)
    data.bankInfo.forEach(bank => {
        const option = document.createElement('option');
        option.value = bank;
        option.textContent = bank;
        bankSelect.appendChild(option);
    });
}

/**
 * 이벤트 리스너 설정
 */
function setupEventListeners() {
    // 광역시/도 선택 시
    regionSelect.addEventListener('change', handleRegionChange);
    
    // 시/군/구 선택 시
    districtSelect.addEventListener('change', handleDistrictChange);
    
    // 찾기 버튼 클릭 시
    searchBtn.addEventListener('click', handleSearch);
}

/**
 * 광역시/도 선택 핸들러
 */
function handleRegionChange() {
    const selectedRegion = regionSelect.value;
    
    // 시/군/구 선택 박스 초기화
    districtSelect.innerHTML = '<option value="">시 / 군 / 구를 선택하세요</option>';
    districtSelect.disabled = !selectedRegion;
    
    // 은행 선택 박스 초기화 및 비활성화
    bankSelect.value = '';
    bankSelect.disabled = true;
    
    if (selectedRegion) {
        // 선택된 광역시/도의 시/군/구 데이터 찾기
        const regionData = data.mapInfo.find(region => region.name === selectedRegion);
        
        if (regionData) {
            regionData.countries.forEach(district => {
                const option = document.createElement('option');
                option.value = district;
                option.textContent = district;
                districtSelect.appendChild(option);
            });
        }
    }
    
    // 결과 메시지 초기화
    hideResultMessage();
}

/**
 * 시/군/구 선택 핸들러
 */
function handleDistrictChange() {
    const selectedDistrict = districtSelect.value;
    
    // 은행 선택 박스 활성화/비활성화
    bankSelect.disabled = !selectedDistrict;
    
    if (!selectedDistrict) {
        bankSelect.value = '';
    }
    
    // 결과 메시지 초기화
    hideResultMessage();
}

/**
 * 검색 버튼 핸들러
 */
function handleSearch() {
    const region = regionSelect.value;
    const district = districtSelect.value;
    const bank = bankSelect.value;
    
    // 유효성 검사
    if (!region || !district || !bank) {
        showResultMessage('모든 항목을 선택해주세요.', 'error');
        return;
    }
    
    // 검색 실행
    searchBanks(region, district, bank);
}

/**
 * 은행 검색 및 마커 표시
 */
function searchBanks(region, district, bank) {
    // 기존 마커 및 인포윈도우 제거
    clearMarkers();
    
    // 검색 쿼리 생성
    const query = `${region} ${district} ${bank}`;
    
    // 카카오 지도 API의 Places 서비스 사용
    const ps = new kakao.maps.services.Places();
    
    ps.keywordSearch(query, (data, status) => {
        if (status === kakao.maps.services.Status.OK) {
            if (data.length === 0) {
                showResultMessage('검색 결과가 없습니다.', 'error');
                return;
            }
            
            // 검색 결과 처리
            displaySearchResults(data);
            showResultMessage(`${data.length}개의 ${bank} 지점을 찾았습니다.`, 'success');
        } else if (status === kakao.maps.services.Status.ZERO_RESULT) {
            showResultMessage('검색 결과가 없습니다.', 'error');
        } else {
            showResultMessage('검색 중 오류가 발생했습니다.', 'error');
        }
    });
}

/**
 * 검색 결과를 지도에 표시
 */
function displaySearchResults(places) {
    const bounds = new kakao.maps.LatLngBounds();
    
    places.forEach((place, index) => {
        // 마커 생성
        const position = new kakao.maps.LatLng(place.y, place.x);
        const marker = new kakao.maps.Marker({
            map: map,
            position: position
        });
        
        // 인포윈도우 생성
        const infowindow = new kakao.maps.InfoWindow({
            content: createInfoWindowContent(place)
        });
        
        // 마커 클릭 이벤트
        kakao.maps.event.addListener(marker, 'click', () => {
            // 기존 인포윈도우 닫기
            closeAllInfoWindows();
            
            // 선택된 인포윈도우 열기
            infowindow.open(map, marker);
            
        });
        
        markers.push(marker);
        infowindows.push(infowindow);
        bounds.extend(position);
    });
    
    // 지도 범위 재설정
    map.setBounds(bounds);
}

/**
 * 인포윈도우 콘텐츠 생성
 */
function createInfoWindowContent(place) {
    return `
        <div class="custom-infowindow" style="padding:10px; min-width:200px;">
            <div class="title" style="font-weight:bold; margin-bottom:5px; font-size:14px;">
                ${place.place_name}
            </div>
            <div class="address" style="font-size:12px; color:#666;">
                ${place.address_name}
            </div>
        </div>
    `;
}

/**
 * 모든 마커 제거
 */
function clearMarkers() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];
    
    infowindows.forEach(infowindow => infowindow.close());
    infowindows = [];
    
    // 기존 경로 제거
    if (currentPolyline) {
        currentPolyline.setMap(null);
        currentPolyline = null;
    }
}

/**
 * 모든 인포윈도우 닫기
 */
function closeAllInfoWindows() {
    infowindows.forEach(infowindow => infowindow.close());
}

/**
 * 결과 메시지 표시
 */
function showResultMessage(message, type) {
    resultMessage.textContent = message;
    resultMessage.className = `result-message ${type}`;
    resultMessage.style.display = 'block';
}

/**
 * 결과 메시지 숨기기
 */
function hideResultMessage() {
    resultMessage.style.display = 'none';
    resultMessage.className = 'result-message';
}
