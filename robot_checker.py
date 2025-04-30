import cv2
import pyautogui
import time
import mss
import numpy as np
import asyncio

confirm_image_path = r"C:\Users\np3nm\Documents\PY\robot_checker\box.png"
sign_image_path = r"C:\Users\np3nm\Documents\PY\test\sign_click\sign.png"
rabby_image_path = r"C:\Users\np3nm\Documents\PY\test\sign_click\rabby.png"

# 다중 모니터 지원을 활성화
pyautogui.FAILSAFE = False  # 마우스가 화면 끝으로 이동했을 때 종료 방지
pyautogui.PAUSE = 0.1  # 동작 사이의 대기 시간 설정

async def find_and_click(image_path, confidence=0.8, monitor_index=1):
    try:
        with mss.mss() as sct:
            monitors = sct.monitors  # 모든 모니터 정보 가져오기
            if monitor_index < 1 or monitor_index > len(monitors) - 1:
                print(f"Invalid monitor index: {monitor_index}")
                return False

            monitor = monitors[monitor_index]  # 특정 모니터 선택
            screenshot = sct.grab(monitor)  # 모니터 캡처
            screenshot = np.array(screenshot)  # numpy 배열로 변환

            # 이미지 매칭
            template = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            print(f"Match confidence for {image_path} on monitor {monitor_index}: {max_val}")
            if max_val >= confidence:
                h, w, _ = template.shape
                center_x = max_loc[0] + w // 2 + monitor["left"]
                center_y = max_loc[1] + h // 2 + monitor["top"]

                # 클릭
                pyautogui.click(center_x, center_y)
                print(f"Clicked {image_path} on monitor {monitor_index} at ({center_x}, {center_y})!")
                return True
            else:
                print(f"{image_path} not found on monitor {monitor_index}.")
                return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

async def main():
    monitor_to_search = [1, 2, 3]  # 탐색할 모니터 인덱스 리스트
    tasks = []

    while True:
        for monitor_index in monitor_to_search:
            # sign.png 비동기 탐지 및 클릭
            tasks.append(find_and_click(sign_image_path, confidence=0.8, monitor_index=monitor_index))

        # 비동기 작업 실행
        await asyncio.gather(*tasks)
        tasks.clear()  # 작업 리스트 초기화
        await asyncio.sleep(15)  # 반복 주기 조정

if __name__ == "__main__":
    print("Starting in 3 seconds...")
    time.sleep(1)

    asyncio.run(main())