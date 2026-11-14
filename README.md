# ST909B-4G V1.0 — โน้ตถอดรหัสบอร์ด 4G GPS Tracker (v3)

บอร์ดจริง: **ST909B-4G-V1.0** (silkscreen, วันที่ผลิต 20230816) — แทร็กเกอร์ 4G/GPS ใช้แบตเตอรี่ Li-ion 1 ก้อน
ชิปหลัก: A7670SA (4G LTE Cat-1, SIMCom) + Quectel L76KB-A58 (GNSS) + TP4056 (ชาร์จ) + MCU ตระกูล LQFP-48 (ด้านหลัง, **ถูกถอดออกไปแล้ว**)

เอกสารละเอียดแยกฝั่ง:
- [Front_PCB.md](Front_PCB.md) — ฝั่งหน้า (โมดูล RF, SIM, วงจรชาร์จ, จุดทดสอบ/บริการ)
- [Back_PCB.md](Back_PCB.md) — ฝั่งหลัง (MCU, เสาอากาศ GPS แบบแผ่น, จุดบัดกรีสายเข้าเคส)

เอกสารงาน PCB (ใน `ST909B-4G\`):
- [docs/P3-ROUTING.md](ST909B-4G/docs/P3-ROUTING.md) — เส้นทาง P3 ที่ล็อกแล้ว: ตาราง segment รายชิ้น + กติกา clearance + ข้อพิสูจน์
- [docs/GND-ISLANDS.md](ST909B-4G/docs/GND-ISLANDS.md) — เกาะ GND 4 ชิ้น: โครงสร้าง fill, สาเหตุ, การเย็บ stitching via, วิธี probe
- [docs/DRC-LOG.md](ST909B-4G/docs/DRC-LOG.md) — วิวัฒนาการ DRC ทุกรอบ + 45 warning ที่ยอมรับพร้อมเหตุผล
- `export\` — CSV สถานะล่าสุด (components / nets_pads / routes / drc_violations) + PDF schematic/layers/BOM
- `archive\` — dump ดิบ `.out.txt` (55 ไฟล์) ทุกรอบแก้ + `pads_dump.txt` — ใช้อ้างอิงย้อนหลังเท่านั้น
- `scripts\` — สคริปต์แก้บอร์ด/ตรวจทั้งหมด (หัวไฟล์มีโน้ตการออกแบบ) • รายงาน DRC ปัจจุบันอยู่ที่ `ST909B-4G_drc_violations.json` (รากโปรเจกต์ — อย่าย้าย)

---

## ภาพอ้างอิง (8 ไฟล์)

| ไฟล์ | คำอธิบาย |
|---|---|
| `ภาพทำเองด้านหน้า.jpg` | ภาพวาดฝั่งหน้า + ป้ายกำกับ (แก้ตามรูปจริงแล้ว = v2) |
| `ภาพทำเองด้านหลัง.jpg` | ภาพวาดฝั่งหลัง + ป้ายกำกับ (แก้ตามรูปจริงแล้ว = v2) |
| `ด้านหน้า(บน).jpg` | รูปถ่ายจริงฝั่งหน้าส่วนบน (โมดูล A7670SA, 220µF, +SPK, BOOT) |
| `ด้านหน้า(กลาง).jpg` | รูปถ่ายจริงฝั่งหน้าส่วนกลาง (GPS L76KB, G3V3, SIM slot, LRX/LTX) |
| `ด้านหน้า(ล่าง).jpg` | รูปถ่ายจริงฝั่งหน้าส่วนล่าง (TP4056, M3V3, ขาบริการขอบล่าง) |
| `ด้านหลัง(บน).jpg` | รูปถ่ายจริงฝั่งหลังส่วนบน (ANT-4G, SOS, LED GPS/CHR/4G) |
| `ด้านหลัง(กลาง).jpg` | รูปถ่ายจริงฝั่งหลังส่วนกลาง (แผ่นเสาอากาศ GPS, 0Ω ×2) |
| `ด้านหลัง(ล่าง).jpg` | รูปถ่ายจริงฝั่งหลังส่วนล่าง (MCU footprint, shield fence, MIC) |

---

## สรุปสถานะ (ตรวจครบทุกภาพแล้ว)

### ✅ ยืนยันแล้วจากรูปจริง
- โมดูล **A7670SA** พร้อมข้อมูลฉลากครบ (ดู [Front_PCB.md](Front_PCB.md))
- โมดูล **Quectel L76KB-A58** (ฉลากมาร์ค `L76KB-A58 / 01-C1003`)
- ตัวเก็บประจุ tantalum **220µF / 6.3V** (มาร์ค "220 6.3V") บริเวณ VBAT
- **Nano SIM slot** แบบกด (แบรนด์ MUP, ป้าย LOCKED/OPEN)
- **TP4056** บริเวณล่างขวา + ตัวต้านทานมาร์ค `R200` ข้างตัว (PROG)
- **ANT-4G 2 ขา (RF + GND)** — หน้าซ้ายบน / หลังขวาบน เป็นคู่เดียวกันผ่านทะลุบอร์ด
- **ปุ่ม SOS** ฝั่งหลัง + ชุดวงจร LED ติดป้าย `GPS / CHR / 4G`
- **แผ่นเสาอากาศ GPS เซรามิก** มาร์ค `204003` มี pad feed ตรงกลาง
- **0Ω Jumpers ×2** (มาร์ค "0 0") ข้างไอคอนเสาอากาศฝั่งหลัง — *ไม่ใช่* Battery Voltage Divider
- **Shield-can fence**: แถบ pad รูปตัว L รอบบริเวณ MCU ฝั่งหลัง
- **ลำดับ pad ขอบล่างฝั่งหน้า** *(ยืนยันใหม่ใน v3)*: ซ้าย→ขวา = `GND / URX / UTX / +5V` แล้ว `PKEY` เป็นปุ่ม 2 pads แยกขวาสุด
- **M3V3 pad**: pad ซ้ายสุดในแถว 3 จุด ตรงป้าย M3V3
- **G3V3**: ป้าย + pad ทดสอบ ของเส้น 3.3V ฝั่ง GPS (มี LDO ตัวเล็ก SOT-23 ใกล้เคียง)
- Silkscreen `ST909B-4G-V1.0` / `20230816` ฝั่งหลัง

### ⚠️ สันนิษฐาน (ตำแหน่งถูก แต่ยืนยันตัวตน/ค่าไม่ได้)
- **Level Shifter (1.8V–3.3V)**: v3 อัปเดต — เห็นชิปดำตัวเล็กบริเวณขวาของโมดูลตรง callout แล้ว (แก้จาก v2 ที่สรุปว่าไม่เห็น) แต่ marking ยังอ่านไม่ได้
- **22R ×4** (มาร์ค "220" สี่ตัวในแถวเดียว) — น่าจะเป็นตัวต้านทานอนุกรมสาย UART/USB ที่วิ่งลง MCU ด้านหลัง
- **TP4056 ตัวจริง**: มาร์คบน IC อ่านไม่ชัด สรุปชื่อจากตำแหน่ง + Rprog เท่านั้น
- **R200**: ถ้าค่าจริงเป็น 2.0k (ตามภาพวาด) → กระแสชาร์จ TP4056 ≈ 600 mA; ต้องวัดด้วยมัลติมิเตอร์เพื่อปิดจบ
- **ขนาดแผ่นเสาอากาศ GPS ~25×25 mm** — ตามภาพวาด ยังไม่ได้วัดจริง
- **จุดป้าย `GND / BAT / PKEY` ขอบล่างฝั่งหลัง** — อ้างจากภาพวาด (ในรูปจริงเห็นชัดแค่ `MIC`)
- **ตำแหน่ง Buck/LDO footprint ว่าง** (ฝั่งหลัง ขวาของ MCU) — เห็น footprint ว่างตรงบริเวณตามภาพวาด แต่รูปแบบ pad ยังจับคู่กับชนิด IC ไม่ได้

### ❓ ยังแก้ไม่ได้
- รุ่น/ตัวตน **MCU** (LQFP-48 ถูกถอดแล้ว ไม่มีหลักฐานรุ่น)
- ฟังก์ชัน **SOT-23 IC** ใกล้ ANT-4G ฝั่งหลัง (v1 เคยเดาว่า "Power Switch IC" — ไม่มีหลักฐาน)
- ฟังก์ชัน **0Ω ×2** (จัมเปอร์อะไร / อยู่บนเส้นสัญญาณใด)
- ฟังก์ชัน pad **GTX** และ **Quectel test pad** (น่าจะเป็นจุดทดสอบ UART ของ GPS)
- ชิ้นส่วนที่ **ถูกถอด/ขูดออก**: MCU, ชุด Buck/LDO, และบริเวณเหนือ `+SPK` (ผิว mask ฉีกขาว 2 แถบ — พบใหม่ใน v3)

---

## สถานะการสร้างใน KiCAD (12 พ.ย. 2026)

โปรเจกต์: `ST909B-4G\ST909B-4G.kicad_pro` — สร้าง/แก้ผ่าน KiCAD MCP (SWIG backend, เซฟลงดิสก์ทุกขั้น)

- **Board outline**: สี่เหลี่ยม **35 × 74 mm** ⚠️ ประมาณจากเคส 78×39 มม. หักกำแพง ~2 มม./ข้าง — รอวัดจริง
- **ชิ้นส่วนที่วางแล้ว 34 รายการ** (ตำแหน่งทั้งหมด ⚠️ ชั่วคราว ตามสัดส่วนรูปถ่าย):
  - หน้า (F.Cu): `U1` A7670SA block 24×24 • `C1` tantalum 220µF block 7.3×4.3 • `U2` L76KB block 10.1×9.7 • `J1` SIM slot block 12.4×11.6 • `U3` TP4056 SOP-8 block • `ANT1` 2 pads (RF+GND) • `J2` 4 pads GND/URX/UTX/+5V • `SW1` PKEY 2 pads • `J6` +SPK 2 pads • `J7` BOOT 3 pads • `J3` VBUS/DP/DM 3 pads • `J4` M3V3 3 pads • `J5` BAT pad 4×3 • `TP1` LRX • `TP2` LTX • `TP3` GTX • `TP4` Quectel TP • `RN1` 22R×4 (footprint จริง 4x0603) • `U5` Level Shifter (SOT-23-6 จริง) • `U6` GPS LDO (SOT-23 จริง) • `R3` R200 (0603 จริง)
  - หลัง (B.Cu): `U4` **LQFP-48 7×7 footprint มาตรฐานจริง** (ตัวแทน MCU ที่ถูกถอด) • `AE2` GPS patch block 18×18 ⚠️ (ภาพวาดบอก 25×25 แต่การสเกล 2 ทางชี้ ~18×18) • `R1`+`R2` 0603 ค่า 0 (จัมเปอร์ ×2) • `SW2` SOS (2 pads + body) • `LED1`–`LED3` 0603 จริง (GPS/CHR/4G) • `U7` SOT-23 ขับ LED (fn?) • `TP5`–`TP8` ขอบล่าง MIC/GND/BAT/PKEY
- **คลัง footprint โปรเจกต์**: `lib\ST909B.pretty` (footprint ทำเอง 15 ตัว: block modules, pad groups, test pads) — ลงทะเบียนใน `fp-lib-table` ทั้งโปรเจกต์และ global
- ชิ้นที่ใช้ footprint มาตรฐาน: LQFP-48 (`Package_QFP`), R_0603 ×3 (`Resistor_SMD`), R_Array_Convex_4x0603 (`Resistor_SMD`), SOT-23 / SOT-23-6 ×2 (`Package_TO_SOT_SMD`), LED_0603 ×3 (`LED_SMD`)
- ยังไม่ได้วาง: shield-can fence รอบ MCU (แถบ pad รูป L — ทำพร้อม phase routing), GPS antenna via (เป็น via เดี่ยว ไม่ใช่ component), footprint Buck/LDO ที่ถูกถอด (ยังจับคู่ชนิด IC ไม่ได้)
- หมายเหตุเทคนิค: `place_component` ของ MCP เคย resolve คลังโปรเจกต์ไม่ได้ (LibraryManager อ่านตารางคลังครั้งเดียวตอนถูกสร้าง) — แก้ด้วยการ trigger สร้าง manager ใหม่ จากนั้นใช้งานได้ปกติทั้งคลังโปรเจกต์และคลังมาตรฐาน

## Netlist reconstruction (12 พ.ย. 2026)

- **Schematic จำลอง**: `ST909B-4G.kicad_sch` — 34 components ตรงกับบอร์ดทุกตัว (จับคู่ด้วย ref) • ต่อ net ด้วย label บน pin ตรงจุด (115 labels, ไม่ใช้ wire — local label ชื่อเดียวกันใน sheet เดียว = net เดียวกันตามกติกา KiCad)
- **คลัง symbol**: `lib\ST909B.kicad_sym` (13 symbol ทำเอง, ลงทะเบียน project scope): `U1_A7670SA` (17 pins), `U2_L76KB`, `U3_TP4056`, `U4_MCU_LQFP48` (17 pins กลุ่มหน้าที่), `U5_LEVELSHIFT`, `U6_LDO_SOT23`, `U7_LEDDRV`, `RN1_ARRAY4`, `J1_SIM6` (C1/C2/C3/C5/C6/C7), `J2_SERVICE4`, `J6_SPK2`, `ANT1_ANT4G`, `PADS_ROW3` • ส่วน R/C/LED/SW/TestPoint ใช้ symbol มาตรฐาน (`Device`, `LED`, `Switch`, `Connector`)
- **Pinout ทั้งหมดเป็นการสันนิษฐาน** ⚠️ ตามการวิเคราะห์เส้นทางบนบอร์ดใน `Front_PCB.md`/`Back_PCB.md` — รอ datasheet A7670SA/L76KB เพื่อยืนยัน
- **PWR_FLAG ×6** (`#FLG1`–`#FLG6`): ปักไว้ที่ +5V / GND / VBAT / VDD_EXT / SIM_VDD / USB_VBUS เพื่อไม่ให้ ERC ติด power-pin error กับ net ที่ถูกขับจาก IC ภายใน block
- **สถานะ net (ตรวจแล้ว 2 ฝั่ง)**: บอร์ด 37 nets / 73 pads ตรงแผน 100% • schematic netlist (kicad-cli) 54 nets — ทุก net ที่มี pad บนบอร์ดตรง PLAN ทุก pin, ส่วนเพิ่มคือ pin ของ block component (U1/U2/U3/C1/J1) ที่ไม่มี pad จริงตามดีไซน์ — ดูแผนฉบับเต็มใน `scripts\assign_nets_v1.py` (PLAN)
- **ERC (kicad-cli)**: **0 errors** • 65 warnings ที่ตั้งใจยอมรับ: 40 `endpoint_off_grid` (pin symbol ทำเองไม่ตรง grid), 15 `lib_symbol_mismatch` (cache ใน .sch ต่างจาก lib เชิงคอสเมติก), 10 `isolated_pin_label` (net ขาเดียวที่ตั้งใจ: TEMP, MIC_N, SIM_VPP, R1_A/B, R2_A/B, QUECTEL_TP, MCU_UTX/URX4G)
- **DRC baseline** (ยังไม่เดิน track): 85 รายการ — 36 `unconnected_items` (รอ routing), 20 `silk_overlap` + 23 `silk_over_copper` (block footprint ชั่วคราว), 5 `courtyards_overlap` + 1 `clearance` (R1↔R2 ชิด 0.05 มม., TP4/TP5/TP7/U4 ชนขอบเพื่อนบ้าน) ⚠️ ตำแหน่งชั่วคราว จะเก็บตอน routing/วัดจริง
- ⚠️ **บั๊ก MCP ที่พบและวิธีข้าม**:
  - `sync_schematic_to_board` map net ผิด (GND/VBAT หาย, pad ได้ net เพี้ยน) → กำหนด net ตรงด้วย pcbnew script แทน
  - `batch_add_and_connect` **วาง symbol ทุกตัวที่ (0,0)** + label ใช้พิกัด local ของ symbol → ทุก component ทับกัน, label ซ้อนกัน, net หลอมรวมเป็นก้อนเดียว → แก้ด้วย `fix_sch_layout.py` (ย้าย instance + สร้าง label ใหม่ตรง pin endpoint, สูตร `sheet = (X+libx, Y−liby)`)
- **สคริปต์ใน `scripts\`**:
  - `assign_nets_v1.py` — แผน net→pads ฉบับเต็ม (authoritative) + สั่งกำหนดจริง (71/71 pad)
  - `assign_nets_fix1.py` — แก้ 2 pad ที่ SetNet ไม่ติดรอบแรก (`R3/2→/GND`, `U4/9→/LED_EN`)
  - `fix_sch_layout.py` — ซ่อมเลย์เอาต์ schematic (ย้าย 40 instances, label 115 จุด, no-connect 9 จุด) + backup `.sch.bak-pre-layout`
  - `fix_pin_types.py` — แก้ pin type ผิด (TX→output, A1/A2→bidirectional, GND/VBUS/SIM_VDD→passive) ใน .sch + .sym
  - `net_check.py` — export/parse netlist ด้วย kicad-cli แล้วเทียบกับ PLAN
  - `erc_summary.py`, `erc.json`, `drc_report.json`, `ST909B-4G_drc_violations.json` — ผลตรวจ
- วิธีตรวจ net ที่เชื่อถือได้: pcbnew script หรือ kicad-cli (`D:\KiCad\10.0\bin\python.exe` / `kicad-cli.exe`) — เครื่องมือ `get_net_pads` ของ MCP คืน 0 เสมอ (ชื่อ net บนดิสก์มี prefix `/` เช่น `/GPS_TX`)

## Routing (13 พ.ย. 2026) — v4b เสร็จ: **DRC 0 errors**

- **สถิติบอร์ด**: 99 tracks (F 47 / B 52) + 24 vias + GND copper zones 2 ชั้น (F.Cu + B.Cu เติม fill ครบ) • มิติเส้น: สัญญาณ 0.25 มม., VBAT 0.3 มม., via Ø0.6 / drill 0.3, ช่องไฟร์ขั้นต่ำ 0.2 มม. (ตรง 0.2 พอดีผ่าน DRC — พิสูจน์แล้วหลายจุด)
- **โครง routing หลัก**: MCU ฝั่งหลัง (B.Cu) ต่อตรงแถว pad ขวาของ U4; สาย USB ต่าง ๆ เดินกำแพง F.Cu ลง via ข้ามชั้น; 4G_TXD/4G_RXD เป็น trunk บน F.Cu ขอบขวา; LED_GPS วนลัดกำแพงเสาอากาศฝั่งหลัง; GND ประสานด้วย via (16.5,58.5) เย็บเกาะใต้ U4 เข้ากับโซน F และ (29.5,45.0) ต่อโซนหลัก F↔B *(อัปเดต: ปัจจุบัน via (16.5,58.5) ถูกใช้เป็นเส้น /M3V3 — สถานะและเหตุผลดู [docs/DRC-LOG.md](ST909B-4G/docs/DRC-LOG.md))*
- **Keepout เสาอากาศ GPS (AE2)**: B.Cu ห้าม track/via/pad ใน x 2.5..20.5, y 35..53 — เส้น GPS_RX ฝั่ง B เลาะขอบตะวันตกที่ x=2.25 (กฎ MCP: สนามผ้าเส้นเดียวชนขอบ = ผ่าน ตัดเข้าไปเท่านั้นที่ผิด)
- **การเดินทางของ DRC ต่อ error**: v2 = 45 (triage ครบ) → v3 = 15 (6 crossing + 4 short ใหม่จาก jog ผิดฝั่ง) → v4 = 4 → **v4b = 0** • เหลือ warning ที่ตั้งใจยอมรับ: silk 42 (block footprint ชั่วคราว) + via_dangling 1 (GPS_RF @ 11.5,44.0 — โครงสร้างเดิมของบอร์ดจริงใน keepout เสาอากาศ เติมไม่ได้ตั้งแต่ต้น)
- **บทเรียน geometry ที่ค้นพบจาก DRC** (สำคัญกับการวัดจริง):
  - pad แถวขวา/บน/ล่างของ U4 กว้าง **1.475 มม. ตามแกน x** (x-span 20.43..21.90) — ไม่ใช่ 0.3; มาจาก orientation pad ใน footprint LQFP-48 ที่แก้โดยให้ DRC ตัดสิน
  - U6/1–2 ก็ยาวตามแกน x (3.325..4.800) → เส้น x=3.4 ลัดวงจร, x=2.95 ผ่าน • ช่อง TP4 (ขอบขวา 2.80) ↔ U6/1 กว้าง 0.525 < 0.65 ที่ track 0.25 ต้องการ → แก้ด้วย local jog ไป x=3.2 เฉพาะช่วง y 50.5..60 (จบใน pad TP3 เน็ตเดียวกัน)
  - starved_thermal U4/2: pad GND แถวขวาถูกเพื่อนบ้านปิดจนมีสไป้ก์เดียว → ขยับเส้น GPS_TX จาก x=22.25 → x=22.9 เปิด fill ช่องตะวันออกกว้าง 0.4745 ได้ 2 สไป้ก์
- **ขั้นตอนบังคับของ workflow**: refill zone ต้องแยก process (script แก้เส้น: UnFill + save → process ใหม่: `ZONE_FILLER.Fill` + save) — Fill ใน process เดียวกับการ `b.Delete` จะ segfault; DRC สั่งผ่าน MCP (`run_drc`) อ่านผลจาก JSON
- **สคริปต์ routing** (ลำดับใช้จริง): `route_tracks_v1.py` → `route_fix_v2.py` (เดินครบ 85+21) → `route_fix_v3.py` (patch 20+6 → 35+7) → `route_fix_v4.py` (patch 28+5 → 25+5) → `route_fix_v4b.py` (แก้ 4 error สุดท้าย: 5+2 → 7+3) • เครื่องมือตรวจ: `dump_all_pads.py`, `diag_v4.py` (โครงสร้าง pad/via รายจุด)
- ⚠️ **เน็ต single-pad ที่ยังลอย (รอตัดสิน route-or-leave)**: `R1_A/B`, `R2_A/B`, `ANT_4G_RF`, `B_VBUS`, `MIC_P`, `K_P/K_N`, `VDD_EXT`, `G_TXD_1V8`, `G_RXD_1V8`, `MCU_UTX4G/URX4G`, `QUECTEL_TP`, `R3/1` — DRC ไม่ฟ้อง unconnected (เน็ตลอยเดี่ยว) แต่ในบอร์ดจริงเส้นพวกนี้มีปลายทางต่อ ต้องรอ pinout จริงเมื่อวัดบอร์ด/datasheet
- ⚠️ **ยังไม่ทำ**: GND stitching grid เสริม (~5 มม. — ตอนนี้ GND ต่อครบแล้ว เป็น optional), shield-can fence รอบ MCU

## P2.5 — Gate ตัวโมดูล U1/U2 (13 พ.ย. 2026) — **0 errors, gate ปิดแล้ว**

กติกาใหม่ (มติโครงการ): **F.Cu ห้ามมี track/via ใต้ตัวโมดูล** U1 (center ±12 มม.) และ U2 (±4.85×5.05) — B.Cu ใต้โมดูลยอมให้ • เกณฑ์ผ่าน = DRC 0 error (clearance/keepout/shorting/mask/hole/edge/crossing/courtyard) — warning ยกไป P4

- **เดินทาง error: 12 → 6 → 0** (สามรอบแก้: `p25b_fix` → `p25c_fix` → `p25d_clean`) ตรวจด้วย `kicad-cli pcb drc --severity-all` เท่านั้น (checker เขียนเองพิสูจน์แล้วว่ามี 2 บั๊ก)
- **ข้อค้นพบสำคัญ**:
  - **Board edge clearance = 0.5000 มม.** (จาก board setup) → ทองแดงต้องห่างขอบบอร์ด ≥0.5 — เส้น x=34.60 เดิมล้ำ (จริง 0.275) → แก้เป็น x=34.30 (ขอบเส้น 34.425 เว้น 0.575)
  - CrtYd จริงของ U6 (ดัมพ์ polygon): bbox (3.08..6.92, 43.20..46.59 ตอน center 44.90) — ค่าเดิมที่เดาจาก `GetBoundingBox` ผิดทั้งชุด ต้องวัดจาก polygon เสมอ
  - p25b ลบได้ 33/34 เพราะ DEL list ใส่ layer `B` แต่เส้นจริงเป็น `F` → เส้นผี /LED_GPS F.Cu (23.60,58.00)→(23.60,30.10) ตกค้าง (dangling สองข้าง) ลบท้ายรอบด้วย `p25d_clean`
- **การแก้รอบสุดท้าย**:
  - `/LED_4G` เส้นใหม่: B.Cu v x=34.30 (68.10→6.90) → via (33.90,6.90) → F.Cu hop h y=6.90 ลัดเหนือ SOS h_top → F.Cu v x=25.40 (6.90→14.80) → via (25.40,14.80) → B.Cu h y=14.80 → v x=17.71 ลง LED3.2 — ทุกช่องเว้น ≥0.225 (U1 pads 0.475, LED_EN x=26.05 0.40, J7.1 0.575, LED_CHR 0.40)
  - `U6` ย้าย (5.00,44.90)→(5.00,44.15): CrtYd 42.45..45.84 เว้น U2 CrtYd (ล่าง 46.10) = 0.26 และ J3 CrtYd (บน 41.99) = 0.46 + ปรับมุม /VBAT เป็น (1.00,44.15) — pad1/2 ของ U6 เว้น 0.50
  - `U1 pad39` starved_thermal (spoke 1/2 — ล้อมด้วย pad ไร้เน็ตช่อง 0.40 กลืนด้วย clearance 0.2×2, ฝั่ง E โดน LED_CHR/LED_EN ปิด) → ตั้ง **zone connection = FULL** (แผ่นเชื่อมตรง — มาตรฐาน GND ของ RF module)
- **สถานะปัจจุบัน**: 95 tracks + 21 vias • DRC **0 error** / 44 warning ยอมรับ (silk 42 + via_dangling 2 — ไป P4) • **unconnected 15** = punch list ของ P3
- ⚠️ **ห้ามเซฟทับไฟล์บอร์ดจาก KiCad GUI ที่เปิดค้างอยู่** (จะกลับสถานะ zone fill / track)

**P3 punch list (15 unconnected)**: G3V3 (U6.2↔U2.8) • VBAT (trk↔U1.55/56/57) • GPS_TX (U2.3↔trk 7.00,37.00) • USB_VBUS (J3.1↔U1.24) • PKEY (trk 17.75,71.50↔U1.1) • GPS_RX (web B.Cu↔TP2.1 และ↔U2.2) • ANT_4G_RF (ANT1.1↔U1.60) • VDD_EXT (U1.15↔U5.1) • 4G_TXD_1V8 (U1.9↔U5.2) • 4G_RXD_1V8 (U1.10↔U5.3) • USB_DP_M (trk↔U1.27) • USB_DM_M (trk↔U1.28)

---

## P3 — เดินเส้น criticals ที่เหลือ + ซ่อมเกาะ GND (14 พ.ย. 2026) — **0 errors, unconnected 0**

เดินเส้นเพิ่ม 6 เน็ต (batch 1–2 ทำก่อนหน้า, batch 3–4 รอบนี้) ตรวจเชิงตัวเลขครบด้วย `scripts/p3_verify.py` (44 candidates / 0 violation) ก่อนลงบอร์ดทุกครั้ง

- **batch 3 (`scripts/p3_batch3.py`)** — ⑦ PKEY + ⑪ VDD_EXT + ⑫ 4G_TXD_1V8 + ⑬ 4G_RXD_1V8 (21 tracks + 8 vias):
  - **PKEY**: via-in-pad U1.1 (1.70,9.50) → F lane ตะวันตก **x=0.60 w0.20** (ขอบทองแดง 0.50 = edge clearance พอดี) ลงถึง y 29.35 → via (1.65,29.35) → B ลงช่องแคบ x=1.625 (เว้น 0.20 พอดีทั้งซ้าย–ขวา: via VBAT (1.00,44.15) กับ via GPS_RX) → ขึ้น y=60.10 → x=10.15 → ลง y=66.30 → x=4.00 → y=70.40 → เข้า via เกาะ (17.75,70.40)
  - **VDD_EXT**: via-in-pad U1.15 (1.70,23.50) → B v x=1.70 → h y=25.00 → v x=27.70 → via-in-pad U5.1 (27.70,32.05)
  - **TXD**: via-in-pad U1.9 → B h y=17.50 → v x=2.80 → h y=22.00 → v x=29.35 → via (29.35,33.00) → F stub เข้า U5.2
  - **RXD**: via-in-pad U1.10 → B h y=18.50 → v x=2.35 → h y=24.30 → v x=28.50 → via-in-pad U5.3 (28.50,33.95)
- **batch 4 (`scripts/p3_batch4.py`)** — ⑭⑮ USB_DP_M/DM_M (11 tracks + 3 vias): ออกจากแถวใต้ U1 (14.00/15.00,28.90) → B แยกเลน DP (x=25.00) / DM (x=24.10) ลงเกาะ USB ฝั่งใต้ (DP เข้าเลน B เดิม y=57.75, DM via (24.30,57.00) → F → via เกาะ (19.90,58.00))
- **batch 5 (`scripts/p3_batch5_fix.py`) — ซ่อม 2 เกาะ zone-fill ที่ DRC รายงาน unconnected 2 คู่**:
  - รากเหตุ (จาก dump vertex ของ fill outline): **เกาะ B** = แถบล่าง/เส้นด้ายตะวันตก ถูกกรงด้วยเส้น PKEY B ใหม่ (x=1.625 ปิดช่อง fill x 1.35..2.03, ต่อด้วยกำแพง VBAT/M3V3 เดิม) — pad เดียวในเกาะคือ TP6.1 (B) • **เกาะ F** = บล็อก NE (x 25.73..34.5 × y 7.2..31.7) + แถบตะวันออก (x 34.03..34.5 × y 32..73.4) ถูกปิดด้วย anti ของ LED_4G/LED_CHR/LED_EN F ที่แตะกันพอดีที่ x=25.725 — pad เดียวคือ J7.3 (F-SMD)
  - แก้ด้วย **GND stitching via 2 ตัว** (ยืนยัน fill ด้วย `scripts/p3_probe.py` ก่อน): **(2.50,71.20)** = F main + B เกาะ และ **(30.00,15.00)** = F เกาะ + B main → ครบ 4 fill เชื่อมกันผ่าน via /GND เดิม (29.50,45.00) → **unconnected 2 → 0** (รายละเอียดใน [docs/GND-ISLANDS.md](docs/GND-ISLANDS.md))
- **starved_thermal U1.2** (error ตัวเดียวที่เหลือ): lane PKEY F ต้องผ่าน corridor ตะวันตกกว้าง 0.70 (x 0.50..1.20) จึงปิด spoke ตะวันตกของ pad2 เสมอ (ตะวันตกของเลนไม่มี fill: ขอบ zone 0.50 กับ anti เลน 0.30..0.90; N/S ถูก anti pad ข้างเคียงปิดตายโครงสร้าง — เหมือน pad39 ที่แก้ใน P2.5) → ตั้ง **U1.2 zone connection = FULL** (`scripts/p3_pad2_solid.py`) → error หาย
- **สถานะปัจจุบัน**: **153 tracks + 42 vias** • DRC **0 error / 45 warning** (silk 42 + via_dangling 3: M3V3 (16.50,58.50), PKEY via-in-pad (1.70,9.50) [F-only โดยเจตนา — ทุกทางเส้น B ถูกกำแพง via-in-pad ปิดหมด], GPS_RF (11.50,44.00)) • **unconnected 0** • ⚠️ ยังห้ามเซฟทับจาก GUI ค้าง

**รอ**: การวัดสัดส่วนจากผู้ใช้ (P1) + ตาราง net ลอย (J1 SIM pads, AE2 pads, pinout V1.03) ก่อนปลดล็อก P5 (Gerber)

---

## ประวัติการแก้

### v7 (รอบนี้ — P3 ปิด: 0 error / 0 unconnected)
- ✅ **P3 ปิด**: เดินครบ 6 criticals (PKEY / VDD_EXT / 4G_TXD_1V8 / 4G_RXD_1V8 / USB_DP_M / USB_DM_M) — unconnected 15 → **0**
- 🔧 ซ่อม 2 เกาะ GND ด้วย stitching via (2.50,71.20) + (30.00,15.00) — ตรวจ fill ด้วย point-in-poly ก่อนทุกจุด • lane PKEY F ขยับ x=0.80→0.60 w0.20 (ขอบ 0.50 พอดี) • U1.2 zone connection = FULL แก้ starved_thermal ตามแนว pad39
- 📤 สถานะ: **153 tracks + 42 vias**, DRC 45 warning ยอมรับ (silk 42 + via_dangling 3) — เหลือ P4 silkscreen → P5 Gerber (รอการวัด P1 จากผู้ใช้)
- 🧹 เคลียร์ไฟล์: dump ดิบ 55 ไฟล์ + pads_dump → `archive\` • เอกสารสะอาด 3 ไฟล์ใน `docs\` (P3-ROUTING / GND-ISLANDS / DRC-LOG) • สคริปต์ตรวจเพิ่ม `p3_gnd_graph.py` (parse บอร์ดตรง: เน็ต via ทั้งหมด + ยืนยันไม่มี TH pad)

### v6 (P2.5 gate โมดูล ปิดแล้ว)
- ✅ **P2.5 gate ปิด: DRC 0 error** (12→6→0) — F.Cu ว่างใต้ U1/U2 ครบ, ทองแดงห่างขอบบอร์ด ≥0.5 มม. ทุกเส้น
- 🔧 แก้หลัก: /LED_4G เส้นใหม่ (v x=34.30 + F.Cu hop หน้า SOS + ลง v x=25.40), U6 →(5.00,44.15) ตาม CrtYd จริง, U1 pad39 zone connection = FULL, ลบเส้นผี /LED_GPS (บั๊กใส่ layer ผิดใน DEL list ของ p25b)
- 📤 export CSV ใหม่ (tracks 95 / vias 21 / footprints 35) • punch list P3 = 15 unconnected

### v5 (routing v4b)
- ✅ **Routing ครบทุกเน็ต multi-pad**: 99 tracks + 24 vias + GND zone 2 ชั้น — **DRC 0 errors / 43 warnings ที่ยอมรับ** (เดินทางต่อ error: 45 → 15 → 4 → 0)
- 🔧 จุดแก้สำคัญรอบสุดท้าย (v4b): local jog GPS_RX หนีช่อง TP4↔U6/1 (x=3.2), stub B ของ via (7.0,34.5), ขยับ GPS_TX x=22.25→22.9 แก้ starved_thermal U4/2, ลบ via (22.0,45.0) เน็ตเพี้ยน + เติม via GND ประสาน 2 จุด ((16.5,58.5), (29.5,45.0))
- ⚠️ ค้างรอ: เน็ต single-pad ลอย 13 กลุ่ม (route-or-leave — รอ pinout จริง), GND stitching grid, shield-can fence รอบ MCU

### v4 (netlist + ERC/DRC)
- ✅ **Net บนบอร์ดครบสมบูรณ์**: 37 nets / 73 pads ตรง PLAN 100% (แก้ 2 pad ค้าง: R3/2→GND, U4/9→LED_EN)
- 🛠 **ซ่อม schematic ที่พังจากบั๊ก MCP**: symbol ทุกตัวถูกวางซ้อนที่ (0,0) + label หลุดพิกัด → net หลอมเป็นก้อนเดียว (79 pins ใน +5V) — ย้าย instance 40 ตัว + label 115 จุดตรง pin (A4 portrait) แล้ว netlist จาก kicad-cli ตรง PLAN ทุก pin
- ✅ **ERC 0 errors** (เดิม 7 errors จาก pin type ผิด — แก้ TX/A1/A2/GND/VBUS/SIM_VDD)
- 📊 **DRC baseline**: 85 รายการ (unconnected 36 รอ routing, silk 43, courtyard/clearance 6 จากตำแหน่งชั่วคราว)
- 🚫 ปัก no-connect 9 ขา: RN1 5–8, U4 16–17, U3 STDBY/CHRG/CE (สันนิษฐานไม่ใช้ ⚠️)

### v3 (ตรวจครบทั้ง 8 ภาพ)
- ✅ **ลำดับ pad ขอบล่าง**: ก่อนหน้านี้รอรูปจริงส่วนล่าง — ตอนนี้มี `ด้านหน้า(ล่าง).jpg` แล้ว ยืนยันว่าภาพวาดตรง (`GND/URX/UTX/+5V` + PKEY ปุ่ม 2 pads)
- ⚠️→ **Level Shifter**: จาก v2 ที่ว่า "ไม่เห็นชิป QFN" → ใน `ด้านหน้า(บน).jpg` เห็นชิปดำตัวเล็กตรงตำแหน่งแล้ว (แต่ยังอ่าน marking ไม่ได้ จึงไม่ปิดสถานะ)
- ➕ เพิ่มข้อสังเกต: บริเวณเหนือ `+SPK` ฝั่งหน้ามีร่องขูด/ชิ้นส่วนถูกถอด (สัมพันธ์กับ "คราบตะกั่ว" ที่ v2 พบ)
- 📄 แยกเอกสารรายฝั่ง: `Front_PCB.md`, `Back_PCB.md`

### v2 (ก่อนหน้า — แก้ภาพวาดตามรูปถ่ายจริง)
- `"Battery Voltage Divider" → "0Ω Jumpers ×2"`: รูปจริงพิมพ์ว่า "0" ทั้งสองตัว จึงเป็นจัมเปอร์ ไม่ใช่วงจรแบ่งแรงดัน
- `"Power Switch IC" → "SOT-23 IC (function?)"`: จากรูปไม่มีหลักฐานว่าเป็น power switch จึงไม่ระบุหน้าที่
- ➕ `"Shield-can fence"`: แถบ pad รูปตัว L รอบบริเวณ MCU คือฐานฝาครอบกันสัญญาณรุ่นที่ไม่ได้ใส่ฝา
- `"LDO 3.3V" → "GPS LDO (G3V3)"`: ให้ตรงกับ silkscreen จริงที่เขียนว่า G3V3
- ➕ `"M3V3 pad"`: pad ซ้ายสุดในแถว 3 จุด ตรงตำแหน่งตัวอักษร M3V3 บนบอร์ดจริง
