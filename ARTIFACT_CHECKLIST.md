# 새 유물(오브젝트) 추가 체크리스트

이 세션에서 사용자가 지적한 모든 오류 유형과, 재발 방지를 위해 새 GLB를 넣을 때
반드시 통과시켜야 하는 검증 항목. **새 유물은 이 체크리스트를 전부 통과하고,
사용자에게 렌더 미리보기로 확인받은 뒤에만 목록(playable)에 넣는다.**

## 1. 임포트 / 디코드
- [ ] **Draco 압축 해제**: 업로드된 GLB는 KHR_draco_mesh_compression 인 경우가 많음.
      게임 GLTFLoader는 Draco 디코딩 불가 → `npx @gltf-transform/cli cp in.glb out.glb` 로 무손실 해제.
      (gltf-pipeline은 Draco 유지하므로 쓰지 말 것)
- [ ] **노멀 확인**: 재구성/병합 GLB는 NORMAL 누락 시 검게 렌더됨.
      export 시 include_normals=True, 게임은 로드 시 computeVertexNormals로 보정(이미 있음).

## 2. 지오메트리 (깨짐 검사) — "금관 실/바늘" 유형
- [ ] **스트레이/퇴화 지오메트리 제거**: 본체에서 떨어져 한 점으로 늘어진 스파이크,
      바운딩박스를 크게 벗어난 정점, 붕괴된 드리개 등. (금관: Y<-0.01 아래 면 제거로 해결한 사례)
- [ ] **밀려난/분해된 부품**: 원본이 부품별로 눕혀진(텍스처 베이킹용) 배치면,
      조립 위치 정보가 없으므로 함부로 병합하지 말 것. 부품 살릴 거면 멀티메시로.
- [ ] **다각도 렌더로 육안 확인** (front/side/back/top).

## 3. UV / 텍스처
- [ ] **UV 존재 확인**. 없으면:
      - 구면 UV는 **랩 이음새(U 1→0) 문제**로 오염 무늬가 늘어지고, 정점분리+RepeatWrapping은
        buildPosMap([0,1] 가정)을 깨서 **청소 번짐 버그** 유발 → 지양(개토우에서 되돌린 사례).
      - xatlas는 유기적 형상에서 수천 개 차트로 쪼개져 오염 무늬가 파편화됨 → 지양.
      - 가능하면 **원본에 있는 UV를 그대로** 쓰는 게 최선.
- [ ] **텍스처 세트**: c(색,sRGB)·m(metal)·n(normal)·r(rough)·ao. 전부 flipY=false 규약.
- [ ] **WebP 압축** (color q82, normal/ao q92 정도). .png→.webp.
- [ ] **AO/마스크 방향**: 게임에 넣고 오염 균일 여부로 검증(뒤집힘 시 상하 flip).

## 4. 오염 균일 (맨살 없음) — 자동 검증
- [ ] 게임 엔진 로드 후 **bareFrac(맨살 비율) ≈ 0** 확인 (seedAO 유물은 내부 제외분 제외).
      시딩은 이미 "실제 UV 커버리지(posMap)+3px 팽창" 기준이라 대부분 자동 해결됨.

## 5. 100% 도달 (내부 오염 막힘 방지) — "사자상 90% 막힘" 유형
- [ ] **반구 가시성 레이캐스트(embreex)로 내부(밀폐) 텍셀 비율 측정**.
- [ ] 내부 비율이 **4% 초과**면 → 도달 가능한 겉면만 오염시키는 마스크를 AO에 **512로 베이킹**
      (팽창은 배경으로만, 내부는 깨끗 유지) + 해당 유물 `seedAO:true`.
      검증: 게임 clean 비율 ≈ 실제 내부% + 겉면 완전 오염(맨살 없음).
- [ ] cavity 과도 주의: dog_ao처럼 어두우면 세척솔 바닥값에 막혀 잘 안 닦임. 매끈한 유물은 AO 밝게.

## 6. 프레이밍 (화면에 온전히) — "향로 잘림/개토우 과대" 유형
- [ ] **fit.byMax:true** 사용(최대 치수 기준 스케일). 길쭉/넓은 유물이 화면 밖으로 안 잘리게.
- [ ] **frameFill(화면 채움) 0.8~0.95** 목표로 fit.h 계산 (기본 카메라 camR=3.5 기준).
      1.0 초과=잘림, 0.7 미만=너무 작음.

## 7. 게임 통합 (ARTIFACTS 엔트리)
- [ ] id·name·era·material·desig·source·short·blurb 채우기.
- [ ] 멀티메시면 `assets.parts:[{...},{...}]` (메시 순서대로 텍스처 세트).
- [ ] 잠금해제 체인 순서 고려(중간에 빼면 진행 막힘 → loadProgress 보정 이미 있음).

## 8. 최종 자동 QA (전 유물 일괄 점검 하네스)
헤드리스 WebGL(playwright+swiftshader, node_modules three, chromium /opt/pw-browsers)로
각 유물: 로드/커버리지/bareFrac/frameFill/브러시 동작 을 표로 출력해 회귀 확인.
→ 이 방식으로 프레이밍 문제(0.61~1.88) 일괄 검출·수정함.

## 9. 사용자 확인
- [ ] **렌더 미리보기(오염 상태+세척 상태)를 사용자에게 보내 확인받은 뒤** playable 반영·배포.

---
### 배포
- 브랜치 `claude/antique-restoration-game-wof8gk` 커밋 → main FF-머지 push (GitHub Pages + Cloudflare 자동배포).
- 커밋 user.email=noreply@anthropic.com, user.name=Claude.
