$base = "c:\Users\frumk\Desktop\ACG\aicraftspeopleguild.github.io\guild\Enterprise\L2\hmi\web\style"
$f = Get-Content "$base\main.css"

function Extract([int]$s, [int]$e, [string]$out) {
    $dir = Split-Path $out
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $slice = $f[($s-1)..($e-1)]
    Set-Content -Path $out -Value $slice -Encoding UTF8
    Write-Host "OK $out ($s-$e)"
}

Extract 1  85  "$base\base\animations.css"
Extract 86   567   "$base\pages\acg-peer-reviews.css"
Extract 568  1106  "$base\pages\ai-harness.css"
Extract 1107 1525  "$base\pages\ai-rituals.css"
Extract 1526 1911  "$base\pages\manifesto.css"
Extract 1912 2413  "$base\pages\charter.css"
Extract 2414 2685  "$base\pages\chief-ai-skeptic.css"
Extract 2686 3226  "$base\pages\code-of-conduct.css"
Extract 3227 3706  "$base\pages\decentralized-guild-web.css"
Extract 3707 4014  "$base\pages\flywheel.css"
Extract 4015 4506  "$base\pages\grid-brain.css"
Extract 4507 5012  "$base\pages\guild-chain.css"
Extract 5013 5294  "$base\pages\guild-radar.css"
Extract 5295 5705  "$base\pages\hall-of-fame.css"
Extract 5706 6104  "$base\pages\hall-of-shame.css"
Extract 6105 6356  "$base\pages\hushbell-full-spec.css"
Extract 6357 6616  "$base\pages\hushbell.css"
Extract 6617 7416  "$base\pages\index.css"
Extract 7417 8086  "$base\pages\index-old.css"
Extract 8087 8449  "$base\pages\irrational-universe.css"
Extract 8450 8936  "$base\pages\konomi-standard.css"
Extract 8937 9471  "$base\pages\lightning-factory.css"
Extract 9472 9992  "$base\pages\members.css"
Extract 9993 10248 "$base\pages\mission-statement.css"
Extract 10249 10611 "$base\pages\occams-razor.css"
Extract 10612 11119 "$base\pages\question-reflection-action.css"
Extract 11120 11606 "$base\pages\sad.css"
Extract 11607 11976 "$base\pages\showcases.css"
Extract 11977 12363 "$base\pages\the-dog.css"
Extract 12364 12883 "$base\pages\the-harm-equation.css"
Extract 12884 13364 "$base\pages\the-pattern-that-wasnt-there.css"
Extract 13365 13903 "$base\pages\the-prediction-trap.css"
Extract 13904 14266 "$base\pages\the-rational-empire.css"
Extract 14267 14676 "$base\pages\white-papers.css"
Extract 14677 15181 "$base\pages\youre-absolutely-wrong.css"
Extract 15182 15242 "$base\widgets\tokens.css"
Extract 15243 15252 "$base\widgets\base.css"
Extract 15253 15305 "$base\widgets\kpi-card.css"
Extract 15306 15346 "$base\widgets\status-pill.css"
Extract 15347 15357 "$base\widgets\tag-value.css"
Extract 15358 15379 "$base\widgets\alarm-count.css"
Extract 15380 15393 "$base\widgets\split-panel.css"
Extract 15394 15431 "$base\widgets\tabbed-panel.css"
Extract 15432 15471 "$base\widgets\param-card.css"
Extract 15472 15485 "$base\widgets\embed.css"

Write-Host 'All files extracted.'

Get-ChildItem -Path $base\base, $base\pages, $base\widgets -Recurse -File | Select-Object FullName | Sort-Object FullName
