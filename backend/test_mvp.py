"""
Quick test script to verify MVP setup

Run this after starting the server to verify everything works:
    python test_mvp.py
"""
import httpx
import sys

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("1. Testing health endpoint...")
    try:
        response = httpx.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data}")
            return True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   Make sure the server is running: python main.py")
        return False


def test_templates():
    """Test templates endpoint"""
    print("\n2. Testing templates endpoint...")
    try:
        response = httpx.get(f"{BASE_URL}/api/templates/")
        if response.status_code == 200:
            templates = response.json()
            print(f"   ✅ Found {len(templates)} templates")
            if len(templates) == 0:
                print("   ⚠️  No templates found. Run: python seed_templates.py")
                return False
            for t in templates[:3]:
                print(f"      - {t['name']}: {t['condition']} in {t['hours_ahead']}h")
            return True
        else:
            print(f"   ❌ Templates request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_otp_generation():
    """Test OTP generation"""
    print("\n3. Testing OTP generation...")
    try:
        response = httpx.post(
            f"{BASE_URL}/api/otp/generate",
            json={"session_id": "test-session-123"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ OTP generated: {data['otp']} (expires in {data['expires_in']}s)")
            return True
        else:
            print(f"   ❌ OTP generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_database():
    """Test database access"""
    print("\n4. Testing database...")
    try:
        from app.core.database import SessionLocal, init_db
        from app.models.reminder import UseCaseTemplate

        init_db()
        db = SessionLocal()

        try:
            count = db.query(UseCaseTemplate).count()
            print(f"   ✅ Database accessible: {count} templates in DB")
            if count == 0:
                print("   ⚠️  Database is empty. Run: python seed_templates.py")
                return False
            return True
        finally:
            db.close()

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_config():
    """Test configuration"""
    print("\n5. Testing configuration...")
    try:
        from app.core.config import settings

        has_telegram = bool(settings.TELEGRAM_BOT_TOKEN) and \
                      settings.TELEGRAM_BOT_TOKEN != "your_bot_token_from_botfather"
        has_weather = bool(settings.OPENWEATHER_API_KEY) and \
                     settings.OPENWEATHER_API_KEY != "your_api_key_here"

        if has_telegram:
            print(f"   ✅ Telegram bot token configured")
        else:
            print(f"   ⚠️  Telegram bot token NOT configured in .env")

        if has_weather:
            print(f"   ✅ OpenWeather API key configured")
        else:
            print(f"   ⚠️  OpenWeather API key NOT configured in .env")

        return has_telegram and has_weather

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("Weather Alert Bot - MVP Tests")
    print("=" * 50)

    results = []

    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Templates API", test_templates()))
    results.append(("OTP Generation", test_otp_generation()))
    results.append(("Database", test_database()))
    results.append(("Configuration", test_config()))

    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed! Your MVP is ready.")
        print("\nNext steps:")
        print("1. Make sure bot is running: python app/bot_polling.py")
        print("2. Send /start to your bot on Telegram")
        print("3. Start frontend: cd ../frontend && npm run dev")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
