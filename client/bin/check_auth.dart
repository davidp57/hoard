// Does media_kit's `httpHeaders` actually reach libmpv?
//
// The Dart HTTP client and mpv fetch over completely separate stacks, so a
// working file listing proves nothing about playback against a server that
// requires HTTP Basic. This opens a Media with headers and reports whether
// mpv got a duration — which it only can if the request was authorised.
//
// Run against the throwaway server in tools: dart run bin/check_auth.dart <url>

import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:media_kit/media_kit.dart';

Future<void> main(List<String> args) async {
  MediaKit.ensureInitialized();

  final url = args.isNotEmpty ? args.first : 'http://127.0.0.1:8799/media.mp4';
  final token = base64Encode(utf8.encode('tester:secret'));
  final headers = {'Authorization': 'Basic $token'};

  final player = Player();
  final gotDuration = Completer<Duration>();

  player.stream.duration.listen((d) {
    if (d > Duration.zero && !gotDuration.isCompleted) gotDuration.complete(d);
  });
  player.stream.error.listen((e) {
    stderr.writeln('mpv error: $e');
  });

  await player.open(Media(url, httpHeaders: headers));

  final duration = await gotDuration.future
      .timeout(const Duration(seconds: 15), onTimeout: () => Duration.zero);

  if (duration > Duration.zero) {
    stdout.writeln('PASS duration=${duration.inMilliseconds}ms');
  } else {
    stdout.writeln('FAIL no duration — mpv could not read the stream');
  }

  await player.dispose();
  exit(duration > Duration.zero ? 0 : 1);
}
