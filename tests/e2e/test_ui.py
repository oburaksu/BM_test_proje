# =============================================
# E2E (End-to-End) Tarayıcı Testleri
# =============================================
# Playwright kullanılarak arayüz üzerinden son kullanıcı 
# senaryolarının (Görev ekleme, tamamlama, silme) otomatik test edilmesini sağlar.

import pytest
from playwright.sync_api import Page, expect

# Test sunucusunun adresi
BASE_URL = "http://localhost:8000/ui/"

def test_add_task_e2e(page: Page):
    """Kullanıcının arayüz üzerinden yeni bir görev ekleyebildiğini test eder."""
    # Arayüze git
    page.goto(BASE_URL)
    
    # Doğru sayfada olduğumuzu kontrol et
    expect(page.locator("h1")).to_have_text("Görev Yöneticisi")
    
    # Yeni görev adını gir
    task_name = "Playwright E2E Test Görevi"
    page.fill("#taskInput", task_name)
    
    # Ekle butonuna tıkla
    page.click("#addTaskBtn")
    
    # Yeni eklenen görevin listede göründüğünü doğrula
    # Görev adının task-title class'ına sahip span içinde olduğunu biliyoruz
    # .first ekliyoruz çünkü testi birden fazla kez çalıştırdığımızda aynı isimde birden fazla görev olabilir
    task_locator = page.locator(f".task-title:has-text('{task_name}')").first
    expect(task_locator).to_be_visible()

def test_toggle_task_e2e(page: Page):
    """Eklenen bir görevin tamamlandı (is_completed) durumuna alınmasını test eder."""
    page.goto(BASE_URL)
    
    # Playwright'a listede bir görevin yüklenmesini beklemesini söyle
    page.wait_for_selector("#taskList li")
    
    # İlk görevi seç
    first_task = page.locator("#taskList li").first
    
    # Başlangıçta görevin completed class'ına sahip olup olmadığına bakmadan
    # direkt butona tıklayıp state'in değişip değişmediğini kontrol edebiliriz
    toggle_button = first_task.locator(".toggle-btn")
    initial_text = toggle_button.inner_text()
    
    # Butona tıkla (API'ye istek atar ve listeyi günceller)
    toggle_button.click()
    
    # Butonun metninin değişmesini bekle
    if initial_text == "Tamamla":
        expect(toggle_button).to_have_text("Geri Al")
        expect(first_task).to_have_class("completed")
    else:
        expect(toggle_button).to_have_text("Tamamla")
        expect(first_task).not_to_have_class("completed")

def test_delete_task_e2e(page: Page):
    """Bir görevin arayüzden başarılı bir şekilde silinmesini test eder."""
    page.goto(BASE_URL)
    
    # Önce test için geçici bir görev ekle
    temp_task = "Silinmek İçin Eklendi"
    page.fill("#taskInput", temp_task)
    page.click("#addTaskBtn")
    
    # Yeni eklenen görevi bul
    task_locator = page.locator(f"li:has(.task-title:has-text('{temp_task}'))")
    expect(task_locator).to_be_visible()
    
    # Bu görevin içindeki Sil butonuna tıkla
    task_locator.locator(".delete-btn").click()
    
    # Görevin DOM'dan tamamen kaldırıldığını doğrula
    expect(task_locator).not_to_be_visible()
