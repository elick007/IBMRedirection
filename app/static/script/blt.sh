cmd=$(curl -k -i --raw -X POST -d "type=1&v=5.6.5&public_parameters=%%7B%%22android_cpu%%22%%3A%%22x86%%2Carmeabi-v7a%%2Carmeabi%%22%%2C%%22new_project_name%%22%%3A%%221%%22%%2C%%22is_has_contract%%22%%3Afalse%%2C%%22is_login%%22%%3Atrue%%2C%%22company_city%%22%%3A%%22%%E6%%97%%A0%%22%%2C%%22platformType%%22%%3A%%22Android%%22%%2C%%22device_id%%22%%3A%%22510000000077324%%22%%2C%%22gps_city%%22%%3A%%22%%E6%%97%%A0%%22%%2C%%22blt_user_id%%22%%3A%%221010503954%%22%%2C%%22city_code%%22%%3A%%22440100%%22%%2C%%22channel%%22%%3A%%22guanwang%%22%%7D&device_id=510000000077324&contract_id=1103259&preset_parameters=%%7B%%22%%24app_version%%22%%3A%%225.6.5%%22%%2C%%22%%24lib%%22%%3A%%22Android%%22%%2C%%22%%24lib_version%%22%%3A%%223.1.5%%22%%2C%%22%%24manufacturer%%22%%3A%%22Netease%%22%%2C%%22%%24model%%22%%3A%%22MuMu%%22%%2C%%22%%24os%%22%%3A%%22Android%%22%%2C%%22%%24os_version%%22%%3A%%226.0.1%%22%%2C%%22%%24screen_height%%22%%3A1280%%2C%%22%%24screen_width%%22%%3A720%%2C%%22%%24wifi%%22%%3Atrue%%2C%%22%%24network_type%%22%%3A%%22WIFI%%22%%2C%%22%%24is_first_day%%22%%3Afalse%%2C%%22%%24device_id%%22%%3A%%22c546a207939c38d3%%22%%2C%%22distinct_id%%22%%3A%%221010503954%%22%%7D&ut=e78e44669303942df200c656cedcc77236fef765&from=3&user_id=1010503954" "https://api.baletu.com/App401/UserPoints/checkInCoupon" -H "User-Agent: app:5.6.5(Linux; Android 6.0.1;Android MuMu Build:V417IR;510000000077324)" -H "Content-Type: application/x-www-form-urlencoded;charset=UTF-8" -H "Host: api.baletu.com" -H "Connection: Keep-Alive")
echo "result=$cmd"