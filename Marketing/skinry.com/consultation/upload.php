<?php
header('Content-type: application/json');

$valid_exts = array('jpeg', 'jpg', 'png', 'gif'); // valid extensions
$max_size = 20 * 1024 * 1024; // max file size (20mb)
$path = 'uploads/'; // upload directory

$request_method = strtoupper(getenv('REQUEST_METHOD'));

if ($request_method === 'POST') {
    if (@is_uploaded_file($_FILES['image']['tmp_name'])) {
        // get uploaded file extension
        $ext = strtolower(pathinfo($_FILES['image']['name'], PATHINFO_EXTENSION));
        $type = 'ERROR';
        // looking for format and size validity
        if (in_array($ext, $valid_exts)) {
            if ($_FILES['image']['size'] < $max_size) {
                // unique file path
                $path = $path . uniqid() . '.' . $ext;
                // move uploaded file from temp to uploads directory
                if (move_uploaded_file($_FILES['image']['tmp_name'], $path)) {
                    $type = 'SUCCESS';
                    $status = 'Изображение загружено!';
                } else {
                    $status = 'Неизвестная ошибка!';
                }
            } else {
                $status = 'Ошибка: размер файла больше 20Мб!';
            }
        } else {
            $status = 'Ошибка: формат файлов должен быть: .jpeg, .jpg, .png или .gif!';
        }
    } else {
        $status = 'Ошибка: файл не был выбран!';
    }
} else {
    $status = 'Ошибка: Неправильный запрос!';
}

// echo out json encoded status
echo json_encode(array('status' => $status, 'path' => $path, 'type' => $type));
