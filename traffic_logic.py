# traffic_logic.py

def status_lalu_lintas(jumlah):
    if jumlah >= 9: return "macet"
    elif jumlah >= 6: return "padat"
    elif jumlah >= 3: return "sedang"
    else: return "lancar"


def hitung_eta(jarak_km, status):
    kecepatan_map = {
        "lancar": 50,
        "sedang": 30,
        "padat": 20,
        "macet": 10
    }
    kecepatan = kecepatan_map.get(status, 30)
    return round((jarak_km / kecepatan) * 60)


def trafic_duration(eta_bandara, eta_pelabuhan, total_duration=30):
    total_beban = eta_bandara + eta_pelabuhan
    if total_beban == 0:
        return {"bandara": 15, "pelabuhan": 15}

    dur_bandara = int((eta_bandara / total_beban) * total_duration)
    dur_pelabuhan = total_duration - dur_bandara
    return {"bandara": dur_bandara, "pelabuhan": dur_pelabuhan}
