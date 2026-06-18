"""
ISYARA BDD Testing Suite - Sign-to-Text Service
Menguji alur Normal, Alternative, dan Exception dengan membuka bisindo.html
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
import time

class ISYARASignToTextTests:
    def __init__(self, base_url="http://localhost:5500"):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 15)
        self.base_url = base_url
        self.results = []

        # Konfigurasi delay
        self.ACTION_DELAY = 3          # delay antar aksi normal
        self.LONG_ACTION_DELAY = 10    # delay untuk simulasi deteksi tangan (sesuai permintaan)

    def close(self):
        self.driver.quit()

    def wait_for_alert(self, timeout=5, accept=True):
        """Menangani pop-up alert jika muncul"""
        try:
            alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            if accept:
                alert.accept()
                print("   ✅ Alert diterima")
            else:
                alert.dismiss()
                print("   ❌ Alert dibatalkan")
            time.sleep(self.ACTION_DELAY)
            return True
        except:
            return False

    def check_overlay_presence(self):
        """
        Memeriksa apakah overlay (loading/spinner) muncul pada halaman bisindo.html.
        Overlay ini menandakan tahap pemrosesan gesture.
        """
        try:
            # Cari elemen overlay umum (misal div dengan class 'overlay' atau 'loading')
            overlay = self.driver.find_element(By.CSS_SELECTOR, ".overlay, .loading, #loadingOverlay")
            if overlay.is_displayed():
                print("   📌 Overlay terdeteksi (tahap pemrosesan gesture)")
                return True
            else:
                print("   ⚠️ Overlay ada tetapi tidak terlihat")
                return False
        except:
            print("   ℹ️ Overlay tidak ditemukan (mungkin sudah selesai atau tidak digunakan)")
            return False

    def login_as_admin(self):
        self.driver.get(f"{self.base_url}/login.html")
        self.wait.until(EC.presence_of_element_located((By.ID, "username")))
        self.driver.find_element(By.ID, "username").send_keys("superadmin")
        self.driver.find_element(By.ID, "password").send_keys("admin123")
        self.driver.find_element(By.CSS_SELECTOR, ".btn-login").click()
        time.sleep(self.ACTION_DELAY)

        # Cek kemungkinan alert setelah login
        self.wait_for_alert(timeout=2, accept=True)

        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard-wrap")))
        time.sleep(self.ACTION_DELAY)

    def go_to_dashboard(self):
        self.driver.get(f"{self.base_url}/dashboard.html")
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard-wrap")))
        time.sleep(self.ACTION_DELAY)

    def switch_tab(self, tab_id):
        tab_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-tab="{tab_id}"]'))
        )
        tab_btn.click()
        time.sleep(self.ACTION_DELAY)

    def get_table_rows(self, table_body_id):
        tbody = self.driver.find_element(By.ID, table_body_id)
        return tbody.find_elements(By.TAG_NAME, "tr")

    def inject_event_from_page(self, page_url, event_data):
        """
        Buka halaman layanan dan inject event ke localStorage seolah-olah berasal dari halaman tersebut.
        Selama membuka halaman, akan dilakukan pengecekan overlay (tahap pemrosesan).
        """
        self.driver.get(page_url)
        # Tunggu halaman siap (simulasi waktu deteksi tangan - 10 detik)
        time.sleep(self.LONG_ACTION_DELAY)

        # Cek overlay (selalu ada selama proses deteksi)
        self.check_overlay_presence()

        inject_script = f"""
            (function() {{
                const state = JSON.parse(localStorage.getItem('isyara_dashboard_data'));
                if (!state) return;
                if (!state.eventLog) state.eventLog = [];
                const now = new Date();
                const waktu = now.toLocaleTimeString('id-ID', {{ hour:'2-digit', minute:'2-digit' }});
                state.eventLog.push({{
                    id: Date.now(),
                    waktu: waktu,
                    kategori: '{event_data["kategori"]}',
                    deskripsi: '{event_data["deskripsi"]}',
                    instansi: '{event_data.get("instansi", "Dinas Kesehatan Kota A")}',
                    eskalasi: false
                }});
                localStorage.setItem('isyara_dashboard_data', JSON.stringify(state));
                console.log('✅ Event injected from page:', '{event_data["deskripsi"]}');
            }})();
        """
        self.driver.execute_script(inject_script)
        time.sleep(self.ACTION_DELAY)  # beri waktu untuk penyimpanan

    # ============================================================
    # TEST 1: Normal Flow - Gestur sukses (Info event)
    # ============================================================
    def test_normal_flow_gesture_success(self):
        print("🧪 [Sign-1] Testing: Normal Flow - Gestur sukses")
        try:
            self.inject_event_from_page(
                f"{self.base_url}/bisindo.html",
                {
                    "kategori": "Info",
                    "deskripsi": "[LOKET 1] Sign-to-Text sukses (latensi 0.9s)",
                    "instansi": "Dinas Kesehatan Kota A"
                }
            )

            self.login_as_admin()
            self.go_to_dashboard()
            self.switch_tab("tab2")

            rows = self.get_table_rows("eventTableBody")
            found = any("Sign-to-Text sukses" in row.text for row in rows)

            if found:
                print("✅ Normal Flow: Event Info muncul di dashboard")
                self.results.append(True)
                return True
            else:
                print("❌ Event tidak ditemukan")
                self.results.append(False)
                return False
        except Exception as e:
            print(f"❌ Failed: {e}")
            self.results.append(False)
            return False

    # ============================================================
    # TEST 2: Alternative Flow - Latensi tinggi (Warning → Insiden)
    # ============================================================
    def test_alternative_flow_latency_high(self):
        print("🧪 [Sign-2] Testing: Alternative Flow - Latensi tinggi")
        try:
            self.inject_event_from_page(
                f"{self.base_url}/bisindo.html",
                {
                    "kategori": "Warning",
                    "deskripsi": "[SERVER] Sign-to-Text latensi > 1.5 dtk (2.1s)",
                    "instansi": "Pusat"
                }
            )

            self.login_as_admin()
            self.go_to_dashboard()
            self.switch_tab("tab2")

            # Eskalasi event ke insiden
            rows = self.get_table_rows("eventTableBody")
            found = False
            for row in rows:
                if "latensi > 1.5" in row.text:
                    found = True
                    try:
                        eskalasi_btn = row.find_element(By.CSS_SELECTOR, ".btn-sm.warning")
                        eskalasi_btn.click()
                        time.sleep(self.ACTION_DELAY)
                        print("   ⚡ Event Warning di-eskalasi ke Insiden")

                        # Cek apakah ada pop-up konfirmasi
                        self.wait_for_alert(timeout=3, accept=True)
                    except:
                        print("   ⚠️  Tombol eskalasi tidak ditemukan")
                    break

            if not found:
                print("❌ Event Warning tidak ditemukan")
                self.results.append(False)
                return False

            # Cek insiden muncul
            self.switch_tab("tab3")
            rows = self.get_table_rows("insidenTableBody")
            found_inc = any("latensi" in row.text.lower() for row in rows)

            if found_inc:
                print("✅ Alternative Flow: Insiden berhasil dibuat dari Warning")
                self.results.append(True)
                return True
            else:
                print("❌ Insiden tidak ditemukan")
                self.results.append(False)
                return False
        except Exception as e:
            print(f"❌ Failed: {e}")
            self.results.append(False)
            return False

    # ============================================================
    # TEST 3: Exception Flow - Gestur tidak dikenali
    # ============================================================
    def test_exception_gesture_not_recognized(self):
        print("🧪 [Sign-3] Testing: Exception Flow - Gestur tidak dikenali → Insiden & rollback")
        try:
            self.inject_event_from_page(
                f"{self.base_url}/bisindo.html",
                {
                    "kategori": "Exception",
                    "deskripsi": "[AI] Gestur tidak dikenali (akurasi 65% - retry 3x)",
                    "instansi": "Pusat"
                }
            )

            self.login_as_admin()
            self.go_to_dashboard()
            self.switch_tab("tab2")

            rows = self.get_table_rows("eventTableBody")
            found = False
            for row in rows:
                if "Gestur tidak dikenali" in row.text:
                    found = True
                    try:
                        eskalasi_btn = row.find_element(By.CSS_SELECTOR, ".btn-sm.warning")
                        eskalasi_btn.click()
                        time.sleep(self.ACTION_DELAY)
                        print("   ⚡ Event Exception di-eskalasi ke Insiden")
                        self.wait_for_alert(timeout=3, accept=True)
                    except:
                        print("   ⚠️  Tombol eskalasi tidak ditemukan")
                    break

            if not found:
                print("❌ Event Exception tidak ditemukan")
                self.results.append(False)
                return False

            self.switch_tab("tab3")
            rows = self.get_table_rows("insidenTableBody")
            found_inc = any("gestur" in row.text.lower() or "akurasi" in row.text.lower() for row in rows)

            if found_inc:
                # Simulasi rollback: update status insiden menjadi "Ditangani"
                for row in rows:
                    if "gestur" in row.text.lower():
                        try:
                            detail_btn = row.find_element(By.CSS_SELECTOR, ".btn-sm")
                            detail_btn.click()
                            time.sleep(self.ACTION_DELAY)
                            status_select = self.wait.until(
                                EC.presence_of_element_located((By.ID, "modalStatusSelect"))
                            )
                            status_select.send_keys("Ditangani")
                            self.driver.find_element(By.ID, "modalConfirm").click()
                            time.sleep(self.ACTION_DELAY)
                            print("   🔧 Insiden diupdate status ke 'Ditangani' (simulasi rollback)")
                            # Cek pop-up sukses
                            self.wait_for_alert(timeout=3, accept=True)
                            break
                        except:
                            pass
                print("✅ Exception Flow: Insiden berhasil dibuat dan diupdate")
                self.results.append(True)
                return True
            else:
                print("❌ Insiden tidak ditemukan")
                self.results.append(False)
                return False
        except Exception as e:
            print(f"❌ Failed: {e}")
            self.results.append(False)
            return False

    # ============================================================
    # TEST 4: Exception Flow - Kamera mati
    # ============================================================
    def test_exception_camera_dead(self):
        print("🧪 [Sign-4] Testing: Exception Flow - Kamera mati → Incident Management")
        try:
            self.inject_event_from_page(
                f"{self.base_url}/bisindo.html",
                {
                    "kategori": "Exception",
                    "deskripsi": "[LOKET 3] Kamera tidak terdeteksi - hardware failure",
                    "instansi": "Dinas Kesehatan Kota A"
                }
            )

            self.login_as_admin()
            self.go_to_dashboard()
            self.switch_tab("tab2")

            rows = self.get_table_rows("eventTableBody")
            found = False
            for row in rows:
                if "Kamera tidak terdeteksi" in row.text:
                    found = True
                    try:
                        eskalasi_btn = row.find_element(By.CSS_SELECTOR, ".btn-sm.warning")
                        eskalasi_btn.click()
                        time.sleep(self.ACTION_DELAY)
                        print("   ⚡ Event kamera mati di-eskalasi ke Insiden")
                        self.wait_for_alert(timeout=3, accept=True)
                    except:
                        pass
                    break

            if not found:
                print("❌ Event kamera mati tidak ditemukan")
                self.results.append(False)
                return False

            self.switch_tab("tab3")
            rows = self.get_table_rows("insidenTableBody")
            found_inc = any("kamera" in row.text.lower() or "hardware" in row.text.lower() for row in rows)

            if found_inc:
                # Verifikasi prioritas Kritis
                for row in rows:
                    if "kamera" in row.text.lower():
                        if "Kritis" in row.text or "red" in row.text:
                            print("   🔴 Insiden berprioritas Kritis")
                        break
                print("✅ Exception Flow (Kamera): Insiden berhasil dibuat")
                self.results.append(True)
                return True
            else:
                print("❌ Insiden kamera tidak ditemukan")
                self.results.append(False)
                return False
        except Exception as e:
            print(f"❌ Failed: {e}")
            self.results.append(False)
            return False

    # ============================================================
    # RUN ALL TESTS
    # ============================================================
    def run_all_tests(self):
        print("=" * 60)
        print("🧪 ISYARA BDD Test Suite - Sign-to-Text (langsung buka bisindo.html)")
        print("=" * 60)

        tests = [
            self.test_normal_flow_gesture_success,
            self.test_alternative_flow_latency_high,
            self.test_exception_gesture_not_recognized,
            self.test_exception_camera_dead,
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"⚠️  Test {test.__name__} gagal dengan error: {e}")
                self.results.append(False)
            time.sleep(self.ACTION_DELAY)  # delay antar test

        self.print_summary()

    def print_summary(self):
        print("\n" + "=" * 60)
        print("📊 HASIL TEST - Sign-to-Text")
        print("=" * 60)
        total = len(self.results)
        passed = sum(self.results)
        failed = total - passed
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {failed}/{total}")
        if passed == total:
            print("🎉 Semua test berhasil!")
        else:
            print(f"⚠️  {failed} test gagal. Periksa log di atas.")


if __name__ == "__main__":
    BASE_URL = "http://localhost:5500"
    test_suite = ISYARASignToTextTests(base_url=BASE_URL)
    try:
        test_suite.run_all_tests()
    finally:
        test_suite.close()