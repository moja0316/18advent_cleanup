var googlehome = require('./google-home-notifier');
var language = 'ja';

googlehome.device('Google Home', language); // Change to your Google Home name
// or if you know your Google Home IP
// googlehome.ip('192.168.1.1', language);

var msg = 'こんにちは。世界。';
if(process.argv.length > 2){
  msg = process.argv[2];
}

googlehome.notify(msg, function(res) {
  console.log(res);
});
