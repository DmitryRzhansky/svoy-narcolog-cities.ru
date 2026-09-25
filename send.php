<?php

declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'Method not allowed'], JSON_UNESCAPED_UNICODE);
    exit;
}

$telegramToken = '8786116533:AAGCox4vaVBUkau6HcRBM6m6xSIikPTZfeU';
$chatId = '-5529601864';

$name = trim((string) ($_POST['name'] ?? ''));
$phone = trim((string) ($_POST['phone'] ?? ''));
$message = trim((string) ($_POST['message'] ?? ''));
$page = trim((string) ($_POST['page'] ?? ''));

$phoneDigits = preg_replace('/\D+/', '', $phone) ?? '';

if ($name === '' || mb_strlen($name) < 2 || mb_strlen($name) > 60) {
    http_response_code(422);
    echo json_encode(['ok' => false, 'error' => 'Укажите корректное имя'], JSON_UNESCAPED_UNICODE);
    exit;
}

if (!preg_match('/^(?:7|8)?9\d{9}$/', $phoneDigits)) {
    http_response_code(422);
    echo json_encode(['ok' => false, 'error' => 'Укажите корректный телефон'], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($message !== '' && mb_strlen($message) > 1000) {
    http_response_code(422);
    echo json_encode(['ok' => false, 'error' => 'Сообщение слишком длинное'], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($phoneDigits[0] === '8') {
    $phoneDigits = '7' . substr($phoneDigits, 1);
} elseif ($phoneDigits[0] === '9') {
    $phoneDigits = '7' . $phoneDigits;
}

$formattedPhone = '+7 (' . substr($phoneDigits, 1, 3) . ') '
    . substr($phoneDigits, 4, 3) . '-'
    . substr($phoneDigits, 7, 2) . '-'
    . substr($phoneDigits, 9, 2);

$text = "Новая заявка:\n";
$text .= 'Имя: ' . $name . "\n";
$text .= 'Телефон: ' . $formattedPhone . "\n";

if ($message !== '') {
    $text .= 'Сообщение: ' . $message . "\n";
}

$host = $_SERVER['HTTP_HOST'] ?? 'svoy-narcolog.ru';
$text .= 'Сайт: ' . $host . "\n";

if ($page !== '') {
    $text .= 'Страница: ' . $page . "\n";
}

$payload = http_build_query([
    'chat_id' => $chatId,
    'text' => $text,
]);

$url = 'https://api.telegram.org/bot' . $telegramToken . '/sendMessage';

$context = stream_context_create([
    'http' => [
        'method' => 'POST',
        'header' => "Content-Type: application/x-www-form-urlencoded\r\n"
            . 'Content-Length: ' . strlen($payload) . "\r\n",
        'content' => $payload,
        'timeout' => 15,
        'ignore_errors' => true,
    ],
]);

$responseBody = @file_get_contents($url, false, $context);
$responseData = is_string($responseBody) ? json_decode($responseBody, true) : null;

if (!is_array($responseData) || empty($responseData['ok'])) {
    http_response_code(502);
    echo json_encode([
        'ok' => false,
        'error' => 'Не удалось отправить заявку. Позвоните нам или напишите в мессенджер.',
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

echo json_encode(['ok' => true], JSON_UNESCAPED_UNICODE);
