import httpx, asyncio, time

TARGET_BASE_URL = "http://target_api:8000"

async def _dispatch_single_probe(client: httpx.AsyncClient, contract: dict, probe_idx: int):
    start_time = time.perf_counter()
    prevented = False
    status_code = 500
    
    probe_val = contract["probe_values"][probe_idx % len(contract["probe_values"])]
    url = f"{TARGET_BASE_URL}{contract['endpoint']}"
    
    try:
        if contract["method"] == "POST":
            payload = {contract["payload_key"]: probe_val}
            res = await client.post(url, json=payload, timeout=2.0)
        else:
            res = await client.get(f"{url}?{contract['query_param_key']}={probe_val}", timeout=2.0)
            
        status_code = res.status_code
        
        # Avaliação de Evidência Agnóstica (Baseada no Contrato)
        if status_code in contract.get("prevented_status_codes", []):
            prevented = True
        elif status_code == 200 and "prevented_body_eval" in contract:
            data = res.json()
            eval_key = contract["prevented_body_eval"]["key"]
            eval_val = contract["prevented_body_eval"]["expected"]
            if data.get(eval_key) == eval_val:
                prevented = True

    except Exception:
        status_code = 500
        prevented = False

    return {
        "probe_idx": probe_idx,
        "status_code": status_code, 
        "prevented": prevented, 
        "latency_ms": (time.perf_counter() - start_time) * 1000.0
    }

async def run_probe_campaign(contract: dict, total_probes: int = 50):
    async with httpx.AsyncClient() as client:
        tasks = [_dispatch_single_probe(client, contract, i) for i in range(total_probes)]
        results = await asyncio.gather(*tasks)

    prevented_count = sum(1 for r in results if r["prevented"])
    latencies = sorted([r["latency_ms"] for r in results])
    
    return {
        "total_probes": total_probes,
        "prevented": prevented_count,
        "bypassed": total_probes - prevented_count,
        "mitigation_percent": (prevented_count / total_probes) * 100.0,
        "mean_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0.0,
        "p95_latency_ms": round(latencies[int(len(latencies) * 0.95)], 2) if latencies else 0.0,
        "availability_percent": round((sum(1 for r in results if r["status_code"] < 500) / total_probes) * 100.0, 2)
    }