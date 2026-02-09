------------------------------------------------------------------------

## Particle Simulation

본 Repository에서는 Isaac Sim에서 **대량 Particle(입자) 환경을 구성하기
위한 최적화된 생성 스크립트**를 제공합니다.

Isaac Sim에는 기본적으로 **PBD Particle 시스템**이 존재하지만,\
해당 방식은 구조적으로 다음과 같은 한계가 있습니다.

-   입자에 작용하는 힘(force) 및 토크(torque) 측정이 불가능
-   Force Sensor, Joint Torque 기반 분석이 적용되지 않음
-   실제 물리 기반 상호작용 분석에는 부적합

따라서 본 프로젝트에서는 PBD 대신\
**Point Instancer 기반 Particle 생성 방식**을 사용합니다.

Point Instancer 방식은 Prototype Particle을 복제(instancing)하여
배치하기 때문에\
수십만 개 이상의 Particle을 생성할 수 있으며, 대규모 환경에서도 성능이
유지됩니다.

------------------------------------------------------------------------

### 제공 스크립트

-   `particle_simulation/point_instancer_fill.py`

Cube 영역 내부를 자동으로 Particle로 채우는 기능을 수행합니다.

------------------------------------------------------------------------

## 사용 방법 (How to Use)

### 1. Cube 배치

Particle을 생성하고 싶은 위치에 Cube를 하나 배치합니다.

-   Prim Path는 반드시 아래와 같아야 합니다.

```{=html}
<!-- -->
```
    /World/Cube

-   Cube의 위치(translate)와 크기(scale)가 Particle 생성 영역이 됩니다.

> ⚠️ 현재 스크립트는 Cube만 지원합니다.

------------------------------------------------------------------------

### 2. Script 실행

1.  Isaac Sim 상단 메뉴에서 Script Editor를 엽니다.

```{=html}
<!-- -->
```
    Window → Script Editor

2.  `point_instancer_fill.py` 파일 내용을 그대로 복사하여 붙여넣습니다.

3.  Run 버튼을 누르면 Particle이 생성됩니다.

------------------------------------------------------------------------

### 3. 실행 결과

-   Cube는 Bounding Box 추출 후 자동 삭제됩니다.
-   Particle은 아래 경로에 생성됩니다.

```{=html}
<!-- -->
```
    /World/Particles

-   실행 후 콘솔에 생성된 Particle 개수가 출력됩니다.

------------------------------------------------------------------------

## 파라미터 설정

스크립트 상단에서 Particle 크기를 조절할 수 있습니다.

``` python
particle_sizes = {
    "large":  0.02,
    "medium": 0.017,
    "small":  0.015
}
```

### Particle 종류

-   `large` : Dodecahedron 형태
-   `medium` : Icosahedron 형태
-   `small` : Sphere 형태

### 생성 개수 결정 방식

Particle 개수는 Cube 크기와 Particle 최대 크기를 기준으로 자동
계산됩니다.

``` python
max_size = max(particle_sizes.values())
num_x = floor(scale[0] / (2 * max_size))
```

즉,

-   Particle 크기를 키우면 → 생성 개수 감소
-   Particle 크기를 줄이면 → 생성 개수 증가

------------------------------------------------------------------------

## 특징 요약

-   Cube 영역 내부를 자동으로 Particle로 채움
-   Point Instancer 기반으로 매우 많은 Particle 생성 가능
-   RTX 5090 기준 300,000개 이상 생성 가능
-   Prototype 기반 3종 입자가 번갈아 배치됨

------------------------------------------------------------------------

## Limitations

-   Cube Prim(`/World/Cube`)만 지원
-   Fabric/Rope 물성 적용은 별도 Rope Simulation 파트에서 다룸
