#!/usr/bin/env bash
# install-hooks.sh: hooks/ 디렉토리의 git hook을 .git/hooks/ 에 심볼릭 링크로 설치한다.
# 실행: bash hooks/install-hooks.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
HOOKS_SRC="$ROOT/hooks"
HOOKS_DST="$ROOT/.git/hooks"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}▶ Git hooks 설치 중...${NC}"

for src in "$HOOKS_SRC"/*; do
  name="$(basename "$src")"
  # install-hooks.sh 자신은 건너뜀
  [ "$name" = "install-hooks.sh" ] && continue
  # .md 파일 건너뜀
  [[ "$name" == *.md ]] && continue

  dst="$HOOKS_DST/$name"

  # 기존 파일(심볼릭 링크 아닌 것)은 백업
  if [ -f "$dst" ] && [ ! -L "$dst" ]; then
    mv "$dst" "${dst}.bak"
    echo "  백업: ${dst}.bak"
  fi

  ln -sfn "$src" "$dst"
  chmod +x "$src"
  echo -e "  ${GREEN}✔${NC} $name → .git/hooks/$name"
done

echo ""
echo -e "${CYAN}▶ 선택적 설정${NC}"
echo "  diff 리뷰 모델 변경 (기본: haiku):"
echo "    export REVIEW_MODEL=sonnet  # 보안 민감 프로젝트 권장"
echo "    export REVIEW_MODEL=claude-haiku-4-5-20251001  # 기본값 (빠름·저렴)"
echo ""
echo -e "${GREEN}✔ 설치 완료${NC}"
