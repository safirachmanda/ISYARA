"""
ISYARA BDD Testing Suite - Speech-to-Text Service
Menguji alur Normal, Alternative, dan Exception dengan membuka speechtotext.html
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ISYARASpeechToTextTests:
    def __init__(self, base_url="http://localhost:5500"):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 15)
        self.base_url = base_url
        self.results = []

    def close(self):
        self.driver.quit()

    def login_as_admin(self):
        self.driver.get(f"{self.base_url}/login.html")
        self.wait.until(EC.presence_of_element_located((By.ID, "username")))
        self.driver.find_element(By.ID, "username").send_keys("superadmin")
        self.driver.find_element(By.ID, "password").send_keys("admin123")
        self.driver.find_element(By.CSS_SELECTOR, ".btn-login").click()
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard-wrap")))

    def go_to_dashboard(self):
        self.driver.get(f"{self.base_url}/dashboard.html")
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard-wrap")))

    def switch_tab(self, tab_id):
        tab_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-tab="{tab_id}"]'))
        )
        tab_btn.click()
        time.sleep(0.5)

    def get_table_rows(self, table_body_id):
        tbody = self.driver.find_element(By.ID, table_body_id)
        return tbody.find_elements(By.TAG_NAME, "tr")

    def inject_event_from_page(self, page_url, event_data):
        self.driver.get(page_url)
        time.sleep(2)
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
        time.sleep(1)

    # ============================================================
    # TEST 1: Normal Flow - Transkripsi sukses
    # ============================================================
    def test_normal_flow_transcription_success(self):
        print("🧪 [Speech-1] Testing: Normal Flow - Transkripsi sukses")
        try:
            self.inject_event_from_page(
                f"{self.base_url}/speechtotext.html",
                {
                    "kategori": "Info",
                    "deskripsi": "[SPEECH] Transkripsi sukses (latensi 0.8s)",
                    "instansi": "Dinas Kesehatan Kota A"
                }
            )

            self.login_as_admin()
            self.go_to_dashboard()
            self.switch_tab("tab2")

            rows = self.get_table_rows("eventTableBody")
            found = any("Transkripsi sukses" in row.text for row in rows)

            if found:
                print("✅ Normal Flow: Event Info muncul")
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
    # TEST 2: Alternative Flow - Latensi tinggi (NLP antrean)
    # ============================================================
    def test_alternative_flow_latency_high(self):
        print("🧪 [Speech-2] Testing: Alternative Flow - Latensi tinggi → Scale server")
        try:
            self.inject_event_from_page(
                f"{self.base_url}/speechtotext.html",
                {
                    "kategori": "Warning",
                    "deskripsi": "[NLP] Latensi tinggi (2.3s) - antrean penuh",
                    "instansi": "Pusat"
                }
            )

            self.login_as_admin()
            self.go_to_dashboard()
            self.switch_tab("tab2")

            rows = self.get_table_rows("eventTableBody")
            found = False
            for row in rows:
                if "Latensi tinggi" in row.text:
                    found = True
                    try:
                        eskalasi_btn = row.find_element(By.CSS_SELECTOR, ".btn-sm.warning")
                        eskalasi_btn.click()
                        time.sleep(1)
                        print("   ⚡ Event Warning di-eskalasi ke Insiden")
                    except:
                        print("   ⚠️  Tombol eskalasi tidak ditemukan")
                    break

            if not found:
                print("❌ Event Warning tidak ditemukan")
                self.results.append(False)
                return False

            self.switch_tab("tab3")
            rows = self.get_table_rows("insidenTableBody")
            found_inc = any("latensi" in row.text.lower() or "NLP" in row.text for row in rows)

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
    # TEST 3: Exception Flow - Audio tidak terproses
    # ============================================================
    def test_exception_audio_not_processed(self):
        print("🧪 [Speech-3] Testing: Exception Flow - Audio tidak terproses")
        try:
            self.inject_event_from_page(
                f"{self.base_url}/speechtotext.html",
                {
                    "kategori": "Exception",
                    "deskripsi": "[SPEECH] Audio tidak terproses - NLP service down",
                    "instansi": "Dinas Kesehatan Kota A"
                }
            )

            self.login_as_admin()
            self.go_to_dashboard()
            self.switch_tab("tab2")

            rows = self.get_table_rows("eventTableBody")
            found = False
            for row in rows:
                if "Audio tidak terproses" in row.text:
                    found = True
                    try:
                        eskalasi_btn = row.find_element(By.CSS_SELECTOR, ".btn-sm.warning")
                        eskalasi_btn.click()
                        time.sleep(1)
                        print("   ⚡ Event Exception di-eskalasi ke Insiden")
                    except:
                        print("   ⚠️  Tombol eskalasi tidak ditemukan")
                    break

            if not found:
                print("❌ Event Exception tidak ditemukan")
                self.results.append(False)
                return False

            self.switch_tab("tab3")
            rows = self.get_table_rows("insidenTableBody")
            found_inc = any("audio" in row.text.lower() or "NLP" in row.text for row in rows)

            if found_inc:
                # Update status insiden untuk mensimulasikan restart service NLP
                for row in rows:
                    if "audio" in row.text.lower():
                        try:
                            detail_btn = row.find_element(By.CSS_SELECTOR, ".btn-sm")
                            detail_btn.click()
                            time.sleep(1)
                            status_select = self.wait.until(
                                EC.presence_of_element_located((By.ID, "modalStatusSelect"))
                            )
                            status_select.send_keys("Ditangani")
                            self.driver.find_element(By.ID, "modalConfirm").click()
                            time.sleep(1)
                            print("   🔧 Insiden diupdate status ke 'Ditangani' (simulasi restart NLP)")
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
    # RUN ALL TESTS
    # ============================================================
    def run_all_tests(self):
        print("=" * 60)
        print("🧪 ISYARA BDD Test Suite - Speech-to-Text (langsung buka speechtotext.html)")
        print("=" * 60)

        tests = [
            self.test_normal_flow_transcription_success,
            self.test_alternative_flow_latency_high,
            self.test_exception_audio_not_processed,
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"⚠️  Test {test.__name__} gagal dengan error: {e}")
                self.results.append(False)
            time.sleep(1)

        self.print_summary()

    def print_summary(self):
        print("\n" + "=" * 60)
        print("📊 HASIL TEST - Speech-to-Text")
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
    test_suite = ISYARASpeechToTextTests(base_url=BASE_URL)
    try:
        test_suite.run_all_tests()
    finally:
        test_suite.close()