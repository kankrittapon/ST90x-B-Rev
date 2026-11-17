# DRC บันทึก — วิวัฒนาการ + ข้อที่ยอมรับ

> สถานะปัจจุบันอ่านจาก `ST909B-4G_drc_violations.json` (เก็บในตำแหน่งรากโปรเจกต์ — **ห้ามย้ายไฟล์** `scripts/drc_summary.py` และ `drc_detail.py` อ่านจากตรงนั้น)
> เช็คซ้ำได้: `python scripts/drc_summary.py` (สรุป) • `scripts/drc_detail.py` (รายการแยกชนิด)

## วิวัฒนาการ (ตัวเลขหลัก)

| จุดตัด | violations | errors | unconnected | หมายเหตุ |
|---|---|---|---|---|
| v4b — เดินเส้นรุ่นแรกจบ | 44 | 0 | 15 | punch list ยังค้างทั้งหมด |
| หลัง P2.5 — ซ่อม pad U1.39 solid + ตรวจ clearance | 44 | 0 | 15 | เลขเดิม — งานที่เหลือคือ P3 |
| หลัง P3 batch 1–2 | 44 | 0 | 6 | ต่อสำเร็จ: G3V3, VBAT×3, GPS_TX, USB_VBUS, GPS_RX×2, ANT_4G_RF |
| หลัง P3 batch 3+4 | 46 | 1 | 2 | +1 error starved_thermal (U1.2), +via_dangling PKEY; ที่ค้าง 6 → 2 (คู่เกาะ zone) |
| หลัง P3 batch 5 | 45 | 0 | 0 | เลื่อนเลน PKEY F x=0.80→0.60 + เติม GND stitching via 2 ตัว |
| หลัง pad2 solid | 45 | 0 | 0 | starved_thermal หาย • parity 0 |
| หลัง P4 — ล้าง silkscreen 42 ข้อ + ลบ via M3V3 — **สถานะปัจจุบัน** | **2** | **0** | **0** | silk 0 • text_height 0 • lib_footprint_mismatch 0 • เหลือ via_dangling 2 ที่ยอมรับ (ดู [P4-SILKSCREEN.md](P4-SILKSCREEN.md)) |

## Punch list ตั้งต้นของ P3 (15 ข้อ จากยุค P2.5)

| เน็ต | จำนวน | รายละเอียด (ตัวอย่างจุด) |
|---|---|---|
| /G3V3 | 1 | U6.2 (4.06,45.10) ↔ U2.8 (4.15,55.30) |
| /VBAT | 3 | track↔U1.57 (1.00,44.15) • U1.56↔U1.57 (17.00,6.10) • U1.55↔U1.56 (18.00,6.10) |
| /GPS_TX | 1 | U2.3 (4.15,49.80) ↔ track (7.00,37.00) |
| /USB_VBUS | 1 | J3.1 (6.50,40.50) ↔ U1.24 (11.00,28.90) |
| /PKEY | 1 | track 13.625 มม. (17.75,71.50) ↔ U1.1 (1.60,9.50) |
| /GPS_RX | 2 | track B (2.25,33.00) ↔ TP2.1 (9.50,37.00) • อีกจุด @(2.25,53.80) |
| /ANT_4G_RF | 1 | (ต่อใน batch 1) |
| /VDD_EXT | 1 | U1.15 ↔ U5.1 |
| /4G_TXD_1V8 | 1 | U1.9 ↔ U5.2 |
| /4G_RXD_1V8 | 1 | U1.10 ↔ U5.3 |
| /USB_DP_M | 1 | U1.27 ↔ เกาะ USB |
| /USB_DM_M | 1 | U1.28 ↔ เกาะ USB |

6 ข้อสุดท้ายที่ค้างหลัง batch 1–2 = PKEY, VDD_EXT, TXD_1V8, RXD_1V8, USB_DP_M, USB_DM_M (จุด (17.75,71.50), (1.60,23.50), (1.60,17.50), (1.60,18.50), (20.10,32.60), (20.10,34.20))

## สถานะปัจจุบัน (DRC 2026-11-17 หลัง P4)

**2 violations = warning ทั้งหมด / 0 error / 0 unconnected / parity 0**

| ชนิด | จำนวน |
|---|---|
| via_dangling | 2 |

### 2 ข้อ via_dangling — ยอมรับพร้อมเหตุผล

| ตำแหน่ง | เน็ต | สาเหตุ | หากต้องการแก้ |
|---|---|---|---|
| (1.70, 9.50) | /PKEY | via-in-pad บน pad U1.1 ฝั่ง F **โดยเจตนา**; ฝั่ง B ไม่มีเส้นต่อเพราะทุกทางลง B ถูกปิด (via-in-pad TXD/RXD/VDD + เส้น VBAT v x=1.00) — พิสูจน์แล้วว่า all-B เป็นไปไม่ได้ (ดู [P3-ROUTING.md](P3-ROUTING.md)) | รับไว้ — เอกสารแล้ว |
| (11.50, 44.00) | GPS_RF | เน็ตเสาอากาศ GPS ยังไม่มีเส้นเลย; pad ของ AE2 ไม่ปรากฏใน footprint ที่ import (pads = 0) → ตำแหน่ง pad จริงยังไม่ทราบ | รอ P1 — วัด pad จริงของ AE2 แล้วเดินเส้น GPS_RF ต่อ (อยู่ในบัญชี blocked ของ P5) |

via ที่สาม (เดิม /M3V3 @ 16.50,58.50) **ถูกลบแล้วใน P4** — ฝั่ง B ไม่มีเส้นต่อจริง การลบไม่กระทบการเดินเส้น (DRC ยัง 0 unconnected)

### 42 ข้อ silk ของยุคก่อน P4 — แก้ครบแล้ว

แก้ด้วย 3 กลไก (ย้าย Reference 21 จุด • ขยาย silk rect 14 อัน • ย้าน U1 pin-1 poly) + sync lib 6 footprint — สรุปเต็มใน [P4-SILKSCREEN.md](P4-SILKSCREEN.md); dumps รายรอบ `p4_*.out.txt` อยู่ที่ `archive/`

### Checks ที่โปรเจกต์ปิดไว้ (จากไฟล์ DRC)

- `missing_courtyard` — footprint เกือบทั้งหมดวาดเอง ไม่มี courtyard
- `track_not_centered_on_via` — ยอมให้ track ปลายไม่ตรงแกน via (ผ่านเส้นที่ถูกต้องอยู่แล้ว)
- `tuning_profile_track_geometries`
- `footprint_filters_mismatch` / `footprint_type_mismatch` — symbol/footprint คู่มือ ไม่มี filter

## ไฟล์ที่เกี่ยวข้อง

- `ST909B-4G_drc_violations.json` — รายงานล่าสุด (อย่าย้าย)
- `scripts/drc_summary.py`, `scripts/drc_detail.py` — ผู้อ่านรายงาน
- `export/drc_violations.csv` — สำเนา CSV สถานะล่าสุด
- dumps รายรอบ (`drc_after_b2.out.txt`, `drc_summary_p25final.out.txt` ฯลฯ) ถูกย้ายไป `archive/` — ใช้อ้างอิงเฉพาะเมื่อต้องย้อนเลขเก่า
