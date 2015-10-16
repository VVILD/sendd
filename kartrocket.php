<?php
$url = 'http://crazymindtechnologies.kartrocket.co/index.php?route=feed/web_api/addorder&key=c20ad4d76fe97759aa27a0c99bff6710';


$data['import_order_id']='';#generate auto 1
$data['firstname']=$argv[1];#2-*
#$data['lastname']='Pinto';
$data['email']='abc@sendd.co';
#$data['company']='';
$data['address_1']=$argv[2];#3
$data['address_2']=$argv[3];
$data['city']=$argv[4];#4
$data['postcode']=$argv[5];#5
$data['state']=$argv[6];#6
$data['country_code']='IN';
#$data['telephone']='9999999999';
$data['mobile']=$argv[7];
#$data['fax']='9999999999 ';
if ($argv[11]=='C'){
$data['payment_method']='cod';
$data['payment_code']='cod';

}
else{
$data['payment_method']='Free checkout';
$data['payment_code']='Payment Code';
}
$data['shipping_method']='Shipment Method';
$data['shipping_code']='Shipment Code';
$data['products'][0]['name']=$argv[8];#enter in admin
$data['products'][0]['model']='SE';#generate auto
$data['products'][0]['sku']='SE';#generate auto
$data['products'][0]['quantity']='1';#constant 1
$data['products'][0]['price']=$argv[9];#enter in admin
$data['products'][0]['total']=$argv[9];
#$data['products'][0]['tax']='6.9047619047619';
#$data['products'][1]['name']='Apple iPhone 4C';
#$data['products'][1]['model']='MB0011';
#$data['products'][1]['sku']='MB0011';
#$data['products'][1]['quantity']='1';
#$data['products'][1]['price']='145';
#$data['products'][1]['total']='145';
#$data['products'][1]['tax']='6.9047619047619';
#$data['totals']['handling']='44';
#$data['totals']['low_order_fee']='77';
$data['totals']['sub_total']=$argv[9];#same as price
#$data['totals']['tax']='0.0';
$data['totals']['total']=$argv[9];#same as price
$data['weight']=$argv[10];#enter in admin
#$data['comment']='';
$data['total']=$argv[9];#same as price
$params['data'] = json_encode($data);
$request = http_build_query($params);
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);
$response = json_decode($response, true);

if ($response["order_added"]["order_id"]){
	echo '1'.$response["order_added"]["order_id"];
}
else{
	echo '0'.$response["error"];
}
?>