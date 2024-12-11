
# GestureIO

Demo Video

[![GestureIO Demo](https://img.youtube.com/vi/P7oylwh6kgQ/0.jpg)](https://youtu.be/P7oylwh6kgQ)

## Overview

GestureIO is an open-source project that enables computer control through hand gestures. It utilizes computer vision technology to allow users to interact with computers with natural hand gestures, making human-computer interaction more accessible and intuitive.

## Features

### Mouse Control

- Move cursor using index finger
- Left click with point gesture followed by standby gesture
- Right click with three fingers followed by fist gesture
- Select using right two/three fingers
- Scroll up/down using left two/three fingers

### Window Management

- Move windows by pinching gesture (okay sign)
- Automatic window focus management
- Multi-window support

### Gesture Recognition

- Real-time hand tracking
- Support for both left and right hands
- Rigth hand gesture patterns:
  - Fist
  - Open hand
  - One fingers(index finger) : move mouse
  - Two fingers : strart select
  - Three fingers : stop select
  - Four fingers
  - Okay sign : move window
  - One finger -> Stand by : click
- Left hand gesture patterns:
  - Fist
  - Open hand
  - One fingers(index finger) : move mouse
  - Two fingers : scroll up
  - Three fingers : scroll down
  - Four fingers
  - Okay sign : move window
  - One finger -> Stand by : click

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/KimDaegyu-Dev/GestureIO.git
   cd GestureIO
   ```

2. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```
   PxPA is a library that only works on Macs
    If your execution environment is Window, you can't move windows, just comment out the PxPA-related code and run it

3. Run the application:

   ```bash
   python main.py
   ```

## Technologies Used

### Core Technologies

- **MediaPipe**: Hand tracking and landmark detection
- **OpenCV**: Real-time video processing
- **PyQt5**: GUI framework for transparent overlay
- **PyAutoGUI**: System-level mouse and keyboard control

### System Integration

- **Quartz**: macOS window management
- **AppKit**: macOS application control
- **PyXA**: macOS application scripting

### Development Tools

- **Python 3.8+**: Main development language
- **Git**: Version control
- **pip**: Package management

## Contributing

We welcome contributions from the community! If you'd like to contribute to GestureIO, please follow these steps:

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Commit your changes and push the branch to your fork
4. Create a pull request with a detailed description of your changes

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/guide) for hand tracking technology
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro) for GUI components
- [PyAutoGUI](https://pypi.org/project/PyAutoGUI/) for mouse and keyboard control
- [PyXA](https://github.com/SKaplanOfficial/PyXA) for macOS application scripting

---

# GestureIO (한국어)

## 개요

GestureIO는 손동작을 통해 컴퓨터 제어를 가능하게 하는 오픈소스 프로젝트입니다. 컴퓨터 비전 기술을 활용하여 사용자가 자연스러운 손동작으로 컴퓨터와 상호작용할 수 있게 하여, 인간-컴퓨터 상호작용을 더욱 접근성 있고 직관적으로 만듭니다.

## 기능

### 마우스 제어

- 검지 손가락으로 커서 이동
- 포인트 제스처 후 대기 제스처로 왼쪽 클릭
- 세 손가락 후 주먹 제스처로 오른쪽 클릭
- 오른손 두/세 손가락으로 선택
- 왼손 두/세 손가락으로 위/아래 스크롤

### 창 관리

- 핀치 제스처(오케이 사인)로 창 이동
- 자동 창 포커스 관리
- 다중 창 지원

### 제스처 인식

- 실시간 손 추적
- 왼손과 오른손 모두 지원
- 오른손 제스처 패턴:
  - 주먹
  - 펼친 손
  - Right한 손가락: 마우스 이동
  - 두 손가락: 선택 시작
  - 세 손가락: 선택 종료
  - 네 손가락
  - 오케이 사인: 창 이동
  - 한 손가락 -> 스탠바이: 클릭
- 왼손 제스처 패턴:
  - 주먹
  - 펼친 손
  - 한 손가락(검지): 마우스 이동
  - 두 손가락: 위로 스크롤
  - 세 손가락: 아래로 스크롤
  - 네 손가락
  - 오케이 사인: 창 이동
  - 한 손가락 -> 스탠바이: 클릭

## 설치 방법

1. 레포지토리 클론:

   ```bash
   git clone https://github.com/KimDaegyu-Dev/GestureIO.git
   cd GestureIO
   ```

2. 필요한 패키지 설치:

   ```bash
   pip install -r requirements.txt
   ```
  PxPA는 Mac에서만 작동하는 라이브러리 입니다
  실행 환경이 Window일 경우 창 이동은 불가능하고 PxPA 관련 코드를 주석 처리하고 실행시키세요
3. 애플리케이션 실행:

   ```bash
   python main.py
   ```

## 사용된 기술

### 핵심 기술

- **MediaPipe**: 손 추적 및 랜드마크 감지
- **OpenCV**: 실시간 비디오 처리
- **PyQt5**: 투명 오버레이를 위한 GUI 프레임워크
- **PyAutoGUI**: 시스템 레벨 마우스 및 키보드 제어

### 시스템 통합

- **Quartz**: macOS 창 관리
- **AppKit**: macOS 애플리케이션 제어
- **PyXA**: macOS 애플리케이션 스크립팅

### 개발 도구

- **Python 3.8+**: 주 개발 언어
- **Git**: 버전 관리
- **pip**: 패키지 관리

## 기여 방법

GestureIO는 커뮤니티의 기여를 환영합니다! 기여하고 싶으신 경우, 다음 단계를 따라주세요:

1. 레포지토리를 포크합니다.
2. 새로운 기능 또는 버그 수정을 위한 브랜치를 생성합니다.
3. 변경 사항을 커밋하고 브랜치를 자신의 포크에 푸시합니다.
4. 변경 사항에 대한 자세한 설명과 함께 풀 리퀘스트를 생성합니다.

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 감사의 글

- [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/guide)를 통한 손 추적 기술
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro)를 통한 GUI 구성 요소
- [PyAutoGUI](https://pypi.org/project/PyAutoGUI/)를 통한 마우스 및 키보드 제어
- [PyXA](https://github.com/SKaplanOfficial/PyXA) for macOS application scripting
