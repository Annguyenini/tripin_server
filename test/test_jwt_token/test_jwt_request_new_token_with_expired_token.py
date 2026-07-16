import requests
def test_access_token_request_new_token_with_expired_token():
    headers={
        "Authorization":"Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlciI6IkFubmd1eWVuIiwiaXNzdWUiOjE3NTk3NTAxOTcsImV4cCI6MTc2MjM0NTc5N30.JWBYld1i6JtGgILHiYfioSRFJxNE59Jd3SDEE6t7aQIiaM2b2du_kC6Un-U-Wn_RBa-x22szQNfHhyjHokZq9Y-vpPbZCmZv2C3vogU5ebfYvnOtfyMPFnKjBZ8i_8KIpVeBY8ZAexqc5yY0i-0HFJH-m81gO170B-ZyTie74ujU4pzAEVauLCVVwFgZbOomA5t__PG8nT6J8i3lrISIFKQKmT9YSdjundU92K7sHVFQ7byxI9OnVcMZKtE3zlItQyHC5IyJggs-W97T-O-M0q_ggvHPDZA5li98g8XwUi9xfofy9TEHaVyEUAg6Oc4yQT0PLHgpVzkT1xMZ95yxtw"
    }
    response = requests.post("http://127.0.0.1:8000/auth/request-access-token",headers =headers)
    data =response.json()
    print(data)
    assert response.status_code ==  401,"Unexpected error"
    
test_access_token_request_new_token_with_expired_token()