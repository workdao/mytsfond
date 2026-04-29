<?php
/**
 * Proxy для обхода CORS при запросах к API my.tsfond.ru
 * Использование: proxytsfond.php?url=<encoded_api_url>
 */

// Разрешаем запросы только с вашего домена (можно настроить)
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization");

// Обработка предзапроса OPTIONS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Получаем целевой URL из параметра
$targetUrl = isset($_GET['url']) ? $_GET['url'] : '';

// Проверка: разрешаем запросы только к домену tsfond.ru
if (empty($targetUrl) || strpos($targetUrl, 'my.tsfond.ru') === false) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid URL. Only my.tsfond.ru is allowed.']);
    exit();
}

// Инициализируем cURL
$ch = curl_init();

// Настраиваем cURL
curl_setopt($ch, CURLOPT_URL, $targetUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); // В продакшене лучше включить и настроить сертификаты
curl_setopt($ch, CURLOPT_TIMEOUT, 30);

// Передаем заголовки от клиента (например, Cookie, если нужно)
$headers = [
    'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer: https://my.tsfond.ru/city'
];
if (function_exists('getallheaders')) {
    $allHeaders = getallheaders();
    if (isset($allHeaders['Authorization'])) {
        $headers[] = 'Authorization: ' . $allHeaders['Authorization'];
    }
}
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

// Выполняем запрос
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);

curl_close($ch);

// Возвращаем ответ
if ($error) {
    http_response_code(500);
    echo json_encode(['error' => 'Proxy error: ' . $error]);
} else {
    http_response_code($httpCode);
    // Возвращаем данные как есть (JSON или другой контент)
    header("Content-Type: application/json");
    echo $response;
}
