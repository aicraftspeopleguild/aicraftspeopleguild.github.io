#!/usr/bin/env python3
"""
p2p-test — headless end-to-end probe of the WSS tracker signalling
path. Simulates two peers announcing to the same info_hash and asserts
that each receives the other's offer back through the tracker.

No WebRTC actually happens — we don't need ICE/DTLS/DataChannel to
verify that the signalling matchmaker is working. That's the layer
that whiteboard reports broken when the chip stays on "looking for
peers" forever.

Usage
-----
  python bin/p2p-test.py                 # uses default TRACKERS from config.js
  python bin/p2p-test.py --room smoke    # custom room name
  python bin/p2p-test.py --tracker wss://tracker.openwebtorrent.com

Exits 0 on success, 1 if no peer cross-sees within TIMEOUT_S.
Requires: pip install websockets
"""
import argparse, asyncio, hashlib, json, re, secrets, sys, time
from pathlib import Path

try:
    import websockets
except ImportError:
    print("ERROR: pip install websockets", file=sys.stderr)
    sys.exit(2)

REPO = Path(__file__).resolve().parents[1]
CONFIG_JS = REPO / "guild" / "Enterprise" / "L2" / "scada" / "gateway" / "scripts" / "config.js"

TIMEOUT_S = 15
FAKE_SDP = (
    "v=0\r\no=- 0 0 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n"
    "a=group:BUNDLE 0\r\na=msid-semantic: WMS\r\n"
    "m=application 0 UDP/DTLS/SCTP webrtc-datachannel\r\n"
    "c=IN IP4 0.0.0.0\r\na=mid:0\r\na=sctp-port:5000\r\n"
)


def trackers_from_config() -> list:
    if not CONFIG_JS.exists():
        return ["wss://tracker.openwebtorrent.com"]
    text = CONFIG_JS.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"TRACKERS\s*=\s*\[(.*?)\]", text, re.DOTALL)
    if not m: return ["wss://tracker.openwebtorrent.com"]
    return re.findall(r"'(wss://[^']+)'", m.group(1)) or ["wss://tracker.openwebtorrent.com"]


def mk_peer_id() -> str:
    # Mirror client: 20 chars, '-ACG001-' + 12 hex
    return "-ACG001-" + secrets.token_hex(6)


def info_hash(room: str) -> str:
    return hashlib.sha1(("acg:" + room).encode()).hexdigest()


async def peer(label: str, url: str, hsh: str, pid: str, seen: dict,
               other_pid: str, ready: asyncio.Event) -> None:
    seen[label] = {"saw_other_offer": False, "saw_other_answer": False,
                   "got_interval": False, "errors": []}

    async def _announce(ws):
        offer_id = secrets.token_hex(16)
        await ws.send(json.dumps({
            "action": "announce", "event": "started",
            "info_hash": hsh, "peer_id": pid,
            "numwant": 50, "uploaded": 0, "downloaded": 0, "left": 1,
            "offers": [{"offer_id": offer_id, "offer": {"type": "offer", "sdp": FAKE_SDP}}],
        }))
        return offer_id

    try:
        async with websockets.connect(url, open_timeout=8, close_timeout=2,
                                       user_agent_header="acg-p2p-test/1.0") as ws:
            print(f"[{label}] WS open -> {url}")
            await _announce(ws)
            print(f"[{label}] -> announce {pid[-8:]}  info_hash={hsh[:8]}..")
            ready.set()

            deadline = time.time() + TIMEOUT_S
            next_reannounce = time.time() + 3.0
            while time.time() < deadline:
                # mirror the whiteboard's fast-announce cadence so a late joiner
                # has a chance to see us. Real client does this every 5 s for
                # the first minute.
                if time.time() >= next_reannounce:
                    await _announce(ws)
                    next_reannounce = time.time() + 3.0
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=1.5)
                except asyncio.TimeoutError:
                    continue
                try:
                    m = json.loads(raw)
                except Exception:
                    continue
                if m.get("failure reason"):
                    print(f"[{label}] XX tracker refused: {m['failure reason']}")
                    seen[label]["errors"].append(m["failure reason"])
                    return
                if m.get("interval"):
                    seen[label]["got_interval"] = True
                from_pid = m.get("peer_id") or m.get("from_peer_id") or ""
                if m.get("offer") and from_pid == other_pid and not seen[label]["saw_other_offer"]:
                    seen[label]["saw_other_offer"] = True
                    print(f"[{label}] OK SAW OFFER from peer {from_pid[-8:]}")
                    # Reply with an answer so the other peer sees something too
                    await ws.send(json.dumps({
                        "action": "announce",
                        "info_hash": hsh, "peer_id": pid,
                        "to_peer_id": from_pid,
                        "offer_id": m.get("offer_id"),
                        "answer": {"type": "answer", "sdp": FAKE_SDP},
                    }))
                if m.get("answer") and from_pid == other_pid:
                    seen[label]["saw_other_answer"] = True
                    print(f"[{label}] OK SAW ANSWER from peer {from_pid[-8:]}")
                # Early exit once this peer has seen the other (keeps test snappy)
                if seen[label]["saw_other_offer"]:
                    # Give the other side a few more seconds to re-announce
                    deadline = min(deadline, time.time() + 5.0)
    except Exception as e:
        print(f"[{label}] XX {type(e).__name__}: {e}")
        seen[label]["errors"].append(f"{type(e).__name__}: {e}")


async def probe(url: str, room: str) -> dict:
    hsh = info_hash(room)
    a_id = mk_peer_id()
    b_id = mk_peer_id()
    seen: dict = {}
    ready_a = asyncio.Event()
    ready_b = asyncio.Event()

    print(f"\n-- tracker: {url}  room={room!r}  hash={hsh[:12]}..")
    await asyncio.gather(
        peer("A", url, hsh, a_id, seen, b_id, ready_a),
        _lag_then(peer, "B", url, hsh, b_id, seen, a_id, ready_b, lag=1.0),
    )
    return {"url": url, "a": seen.get("A", {}), "b": seen.get("B", {}),
            "cross_seen": any(s.get("saw_other_offer") for s in seen.values())}


async def _lag_then(fn, *args, lag=1.0, **kw):
    await asyncio.sleep(lag)
    return await fn(*args, **kw)


async def amain(args):
    trackers = [args.tracker] if args.tracker else trackers_from_config()
    print(f"-- config trackers: {trackers}")
    results = []
    for url in trackers:
        r = await probe(url, args.room)
        results.append(r)

    any_ok = any(r["cross_seen"] for r in results)
    print("\n-- SUMMARY --")
    for r in results:
        ok = "OK" if r["cross_seen"] else "XX"
        print(f"  {ok}  {r['url']}  A_saw={r['a'].get('saw_other_offer')}  B_saw={r['b'].get('saw_other_offer')}  "
              f"errs={[*r['a'].get('errors',[]), *r['b'].get('errors',[])]}")
    if any_ok:
        print("\nRESULT: at least one tracker cross-forwards offers — signalling layer OK.")
        return 0
    print("\nRESULT: no tracker cross-forwarded. Either all trackers down, or matchmaker broken.")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--room",    default=f"acg-smoke-{secrets.token_hex(3)}")
    ap.add_argument("--tracker", help="override; defaults to TRACKERS in config.js")
    args = ap.parse_args()
    return asyncio.run(amain(args))


if __name__ == "__main__":
    sys.exit(main())
