<?php
header('Content-type: application/json');

function is_admin_logged_in(){
    return isset($_COOKIE["admin"]);
}

function is_user_logged_in(){
    if (is_admin_logged_in()){
        return false;
    }else{
        return true;
    }
}

function cackle_auth(){
    $timestamp = time();
    $siteApiKey = "dc2igJqXYRMxSKWHLfkb7HYIhnCA2H5VeZuE5qjO4a7EWQDcASzy3fGoOl4vlYYq";
    if (is_user_logged_in()){
       $user = array(
          'id' => $_GET["id"],
          'name' => "user" . $_get["id"]
    );
       $user_data = base64_encode(json_encode($user));
    }
    if (is_admin_logged_in()){
        $user = array(
                  'id' => "admin",
                  'name' => "Dermatologist",
                  'email' => 'dermatologist@skinry.com',
                  'avatar' => 'http://www.skinry.com/resources/img/nurse.jpg'
            );
        $user_data = base64_encode(json_encode($user));
    }
    //else{
    //    $user = '{}';
    //    $user_data = base64_encode($user);
    //}
    $sign = md5($user_data . $siteApiKey . $timestamp);
    return "$user_data $sign $timestamp";
}

$data =  cackle_auth();

echo json_encode(array('data' => $data));
?>