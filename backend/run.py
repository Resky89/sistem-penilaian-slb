from app import app

if __name__ == "__main__":
    # Menjalankan server lokal Flask di port 8001 dengan fitur debug reload otomatis
    app.run(host="127.0.0.1", port=8001, debug=True)
